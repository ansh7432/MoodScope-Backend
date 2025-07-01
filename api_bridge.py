#!/usr/bin/env python3
"""
Enhanced FastAPI server to connect Next.js frontend with MoodScope backend
This acts as a bridge between the Next.js app and your existing Python analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import subprocess
import json
from pathlib import Path

app = FastAPI(title="MoodScope API Bridge", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlaylistRequest(BaseModel):
    playlist_url: str

class AnalysisResponse(BaseModel):
    tracks: list
    mood_summary: dict
    ai_insights: dict = None
    playlist_name: str = None

# Path to your original MoodScope directory
MOODSCOPE_PATH = Path(__file__).parent.parent

def get_playlist_name_from_spotify(playlist_url: str) -> str:
    """
    Try to get the playlist name from Spotify before full analysis
    """
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        import os
        
        # Set up Spotify client with the correct environment variable names
        os.environ['SPOTIPY_CLIENT_ID'] = 'dd5cd07d15bc4de8a67641e959441624'
        os.environ['SPOTIPY_CLIENT_SECRET'] = '3e05f4fce6c04cf69026043a2ca5c8b1'
        
        auth_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # Extract playlist ID from URL - handle multiple formats
        import re
        
        # Handle Spotify URI format (spotify:playlist:ID)
        if playlist_url.startswith('spotify:playlist:'):
            playlist_id = playlist_url.split(':')[2] if len(playlist_url.split(':')) > 2 else None
        else:
            # Handle regular URL formats
            playlist_id_match = re.search(r'playlist[:/]([a-zA-Z0-9]+)', playlist_url)
            playlist_id = playlist_id_match.group(1) if playlist_id_match else None
        
        if not playlist_id:
            print(f"❌ Could not extract playlist ID from URL: {playlist_url}")
            return None
        print(f"🔍 Extracted playlist ID: {playlist_id}")
        
        # Get playlist info
        playlist_info = sp.playlist(playlist_id, fields='name,public,owner.display_name')
        print(f"📋 Fetched playlist info: {playlist_info}")
        
        if playlist_info and playlist_info.get('name'):
            owner = playlist_info.get('owner', {}).get('display_name', 'Unknown')
            playlist_name = f"{playlist_info['name']} by {owner}"
            print(f"✅ Successfully got playlist name: {playlist_name}")
            return playlist_name
        
        return None
        
    except Exception as e:
        print(f"⚠️ Could not fetch playlist name: {e}")
        return None

def run_moodscope_analysis(playlist_url: str):
    """
    Run the original MoodScope analysis using subprocess
    This allows us to use your existing backend without import issues
    """
    try:
        print(f"🔧 Setting up analysis for: {playlist_url}")
        
        # Create a temporary analysis script
        analysis_script = f"""
import os
import sys
import json
import traceback

# Set environment variables with correct names for spotipy
os.environ['SPOTIPY_CLIENT_ID'] = 'dd5cd07d15bc4de8a67641e959441624'
os.environ['SPOTIPY_CLIENT_SECRET'] = '3e05f4fce6c04cf69026043a2ca5c8b1'

sys.path.append('.')
sys.path.append('core')

try:
    print("📦 Importing modules...")
    from core.fallback_spotify import FallbackSpotifyAnalyzer
    from core.local_ai_insights import LocalMoodAI
    print("✅ Modules imported successfully")
    
    # Initialize analyzer
    print("🎵 Initializing Spotify analyzer...")
    analyzer = FallbackSpotifyAnalyzer(use_user_auth=False)
    print("✅ Analyzer initialized")
    
    # Analyze playlist
    print("🔍 Analyzing playlist...")
    df = analyzer.analyze_playlist("{playlist_url}")
    print(f"📊 Analysis complete. Found {{len(df)}} tracks")
    
    if df.empty:
        print(json.dumps({{"error": "Could not analyze playlist - no tracks found"}}))
        exit(1)
    
    # Get mood summary
    print("📈 Generating mood summary...")
    mood_summary = analyzer.get_mood_summary(df)
    print("✅ Mood summary generated")
    
    # Convert DataFrame to list of tracks
    tracks = df.to_dict('records')
    print(f"🎯 Converted {{len(tracks)}} tracks to dict format")
    
    # Generate AI insights
    print("🤖 Generating AI insights...")
    try:
        local_ai = LocalMoodAI()
        ai_insights = local_ai.generate_mood_insights(mood_summary, tracks[:5])
        print("✅ AI insights generated")
    except Exception as ai_error:
        print(f"⚠️ AI insights failed, using fallback: {{ai_error}}")
        ai_insights = {{
            "emotional_analysis": "Analysis completed successfully with basic mood categorization.",
            "personality_traits": ["Music enthusiast", "Emotionally aware"],
            "recommendations": ["Explore similar artists", "Try mood-based playlists"],
            "mood_coaching": "Your music taste shows good emotional awareness."
        }}
    
    # Output results as JSON
    result = {{
        "tracks": tracks,
        "mood_summary": mood_summary,
        "ai_insights": ai_insights
    }}
    
    print("🎉 Analysis complete, outputting results...")
    print(json.dumps(result, default=str))
    
except Exception as e:
    print(f"❌ Analysis failed: {{str(e)}}")
    print(f"🔍 Traceback: {{traceback.format_exc()}}")
    print(json.dumps({{"error": f"Analysis failed: {{str(e)}}"}}))
    exit(1)
"""
        
        # Write the script to a temporary file
        script_path = Path("/tmp/moodscope_analysis.py")
        print(f"📝 Writing analysis script to: {script_path}")
        with open(script_path, "w") as f:
            f.write(analysis_script)
        
        print(f"🚀 Running analysis script...")
        # Run the analysis script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=120,  # 120 second timeout
            cwd=str(MOODSCOPE_PATH)  # Change working directory to MoodScope backend
        )
        
        print(f"📋 Script completed with return code: {result.returncode}")
        
        if result.returncode != 0:
            print(f"❌ Error output: {result.stderr}")
            print(f"📄 Standard output: {result.stdout}")
            raise Exception(f"Analysis script failed: {result.stderr}")
        
        # Parse the JSON output
        try:
            if not result.stdout.strip():
                raise Exception("No output from analysis script")
            
            # Find the JSON output in the stdout (it should be the last line)
            lines = result.stdout.strip().split('\n')
            json_line = None
            for line in reversed(lines):
                if line.startswith('{') and line.endswith('}'):
                    json_line = line
                    break
            
            if not json_line:
                raise Exception(f"No JSON output found in: {result.stdout}")
            
            analysis_result = json.loads(json_line)
            if "error" in analysis_result:
                raise Exception(analysis_result["error"])
            return analysis_result
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"📄 Raw output: {result.stdout}")
            raise Exception(f"Invalid JSON output: {result.stdout}")
            
    except subprocess.TimeoutExpired:
        raise Exception("Analysis timed out after 120 seconds")
    except Exception as e:
        print(f"❌ Failed to run analysis: {str(e)}")
        raise Exception(f"Failed to run analysis: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    moodscope_exists = MOODSCOPE_PATH.exists()
    return {
        "status": "healthy",
        "message": "MoodScope API Bridge is running",
        "moodscope_path_exists": moodscope_exists,
        "moodscope_path": str(MOODSCOPE_PATH)
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_playlist(request: PlaylistRequest):
    """Analyze a Spotify playlist"""
    
    print(f"🎵 Analyzing playlist: {request.playlist_url}")
    
    if not MOODSCOPE_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail=f"MoodScope backend not found at {MOODSCOPE_PATH}. Please check the path."
        )
    
    # Try to get playlist name first
    playlist_name = get_playlist_name_from_spotify(request.playlist_url)
    print(f"📝 Playlist name: {playlist_name or 'Could not fetch name'}")
    
    try:
        # Run the analysis using your existing backend
        print("🔄 Starting analysis...")
        result = run_moodscope_analysis(request.playlist_url)
        print("✅ Analysis completed successfully")
        
        # Add the playlist name to the result
        if playlist_name:
            result["playlist_name"] = playlist_name
        
        return AnalysisResponse(
            tracks=result["tracks"],
            mood_summary=result["mood_summary"],
            ai_insights=result.get("ai_insights"),
            playlist_name=result.get("playlist_name", "Unknown Playlist")
        )
        
    except Exception as e:
        print(f"❌ Analysis failed with error: {str(e)}")
        
        # For now, provide demo data as fallback until Spotify issues are resolved
        print("🔄 Providing demo analysis as fallback...")
        
        # Get demo data instead
        demo_data = await demo_analysis()
        
        # Customize the demo data to show this is a demonstration
        demo_data.ai_insights["emotional_analysis"] = f"This is a demo analysis showing MoodScope's capabilities! The system had trouble accessing your specific playlist (this could be due to privacy settings, an incorrect URL, or temporary connectivity issues), but here's what a real analysis would look like with your music."
        demo_data.ai_insights["mood_coaching"] = "Try the demo mode button for a smoother experience, or ensure your playlist URL is correct and public!"
        
        # Use the real playlist name if we got it
        if playlist_name:
            demo_data.playlist_name = f"{playlist_name} (Demo Fallback)"
        else:
            demo_data.playlist_name = "Demo Fallback Analysis"
        
        return demo_data

@app.get("/demo")
async def demo_analysis():
    """Demo endpoint with sample data for testing frontend"""
    demo_tracks = [
        {
            "name": "Happy Song",
            "artist": "Demo Artist",
            "mood_score": 0.8,
            "energy": 0.9,
            "valence": 0.85,
            "danceability": 0.7,
            "acousticness": 0.2,
            "speechiness": 0.1,
            "instrumentalness": 0.0,
            "popularity": 75,
            "mood_category": "Energetic & Happy"
        },
        {
            "name": "Calm Melody",
            "artist": "Demo Artist 2",
            "mood_score": 0.4,
            "energy": 0.3,
            "valence": 0.5,
            "danceability": 0.3,
            "acousticness": 0.8,
            "speechiness": 0.05,
            "instrumentalness": 0.2,
            "popularity": 60,
            "mood_category": "Calm & Content"
        }
    ]
    
    demo_mood_summary = {
        "total_tracks": 2,
        "mood_score": 0.6,
        "avg_energy": 0.6,
        "avg_valence": 0.675,
        "avg_danceability": 0.5,
        "avg_acousticness": 0.5,
        "avg_speechiness": 0.075,
        "avg_instrumentalness": 0.1,
        "avg_popularity": 67.5,
        "dominant_mood": "Energetic & Happy",
        "most_common_mood": "Energetic & Happy",
        "mood_distribution": {"Energetic & Happy": 1, "Calm & Content": 1},
        "emotional_range": 0.4,
        "using_estimates": False
    }
    
    demo_ai_insights = {
        "emotional_analysis": "This demo playlist shows a balanced mix of energetic and calm tracks, indicating emotional versatility and good mood regulation skills.",
        "personality_traits": ["Emotionally balanced", "Appreciates variety", "Good mood awareness"],
        "recommendations": ["Try exploring more upbeat tracks for energy", "Consider acoustic music for relaxation"],
        "mood_coaching": "Your demo playlist suggests you understand how to use music for different emotional states - a sign of good emotional intelligence!"
    }
    
    return AnalysisResponse(
        tracks=demo_tracks,
        mood_summary=demo_mood_summary,
        ai_insights=demo_ai_insights,
        playlist_name="Demo Playlist"
    )

@app.get("/test-spotify")
async def test_spotify():
    """Test Spotify connectivity with a known working playlist"""
    try:
        # Test with Today's Top Hits which should always exist
        test_url = "https://open.spotify.com/playlist/37i9dQZF1DWXRqgorJj26U"
        result = run_moodscope_analysis(test_url)
        return {"status": "success", "message": "Spotify connection working", "tracks_found": len(result.get("tracks", []))}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "MoodScope API Bridge",
        "description": "Bridge between Next.js frontend and MoodScope Python backend",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze (POST)",
            "demo": "/demo (GET) - for testing frontend",
            "docs": "/docs"
        },
        "frontend_url": "http://localhost:3001",
        "moodscope_backend": str(MOODSCOPE_PATH)
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting MoodScope API Bridge...")
    print("📱 Frontend URL: http://localhost:3001")
    print("🔗 API URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print(f"🎵 MoodScope Backend: {MOODSCOPE_PATH}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
