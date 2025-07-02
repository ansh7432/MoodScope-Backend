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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="MoodScope API Bridge", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:3002", 
        "http://localhost:3004",
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:3001", 
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3004",
        "https://moodscope-ai.vercel.app",
        "https://nextmoodscale.vercel.app",
        "https://moodscope-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
MOODSCOPE_PATH = Path(__file__).parent

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
    from core.huggingface_ai_insights import LocalMoodAI
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
    """Demo endpoint with sample data for testing frontend - redirects to demo1"""
    return await demo_upbeat_playlist()

@app.get("/demo/upbeat")
async def demo_upbeat_playlist():
    """Demo endpoint with upbeat/energetic playlist - 20 songs"""
    demo_tracks = [
        {"name": "Blinding Lights", "artist": "The Weeknd", "mood_score": 0.9, "energy": 0.9, "valence": 0.8, "danceability": 0.8, "acousticness": 0.1, "speechiness": 0.1, "instrumentalness": 0.0, "popularity": 95, "mood_category": "Energetic & Happy"},
        {"name": "Levitating", "artist": "Dua Lipa", "mood_score": 0.85, "energy": 0.85, "valence": 0.9, "danceability": 0.9, "acousticness": 0.1, "speechiness": 0.05, "instrumentalness": 0.0, "popularity": 90, "mood_category": "Energetic & Happy"},
        {"name": "Good 4 U", "artist": "Olivia Rodrigo", "mood_score": 0.8, "energy": 0.9, "valence": 0.7, "danceability": 0.7, "acousticness": 0.2, "speechiness": 0.2, "instrumentalness": 0.0, "popularity": 88, "mood_category": "Energetic & Excited"},
        {"name": "Anti-Hero", "artist": "Taylor Swift", "mood_score": 0.7, "energy": 0.8, "valence": 0.6, "danceability": 0.7, "acousticness": 0.3, "speechiness": 0.1, "instrumentalness": 0.0, "popularity": 92, "mood_category": "Energetic & Confident"},
        {"name": "As It Was", "artist": "Harry Styles", "mood_score": 0.75, "energy": 0.7, "valence": 0.8, "danceability": 0.6, "acousticness": 0.4, "speechiness": 0.05, "instrumentalness": 0.0, "popularity": 89, "mood_category": "Upbeat & Nostalgic"},
        {"name": "Heat Waves", "artist": "Glass Animals", "mood_score": 0.7, "energy": 0.6, "valence": 0.8, "danceability": 0.7, "acousticness": 0.3, "speechiness": 0.1, "instrumentalness": 0.1, "popularity": 85, "mood_category": "Chill & Happy"},
        {"name": "Industry Baby", "artist": "Lil Nas X", "mood_score": 0.9, "energy": 0.95, "valence": 0.85, "danceability": 0.9, "acousticness": 0.05, "speechiness": 0.3, "instrumentalness": 0.0, "popularity": 87, "mood_category": "Energetic & Confident"},
        {"name": "Stay", "artist": "The Kid LAROI & Justin Bieber", "mood_score": 0.8, "energy": 0.8, "valence": 0.75, "danceability": 0.8, "acousticness": 0.2, "speechiness": 0.1, "instrumentalness": 0.0, "popularity": 86, "mood_category": "Energetic & Happy"},
        {"name": "Peaches", "artist": "Justin Bieber", "mood_score": 0.85, "energy": 0.7, "valence": 0.9, "danceability": 0.8, "acousticness": 0.3, "speechiness": 0.1, "instrumentalness": 0.0, "popularity": 84, "mood_category": "Chill & Happy"},
        {"name": "Sunflower", "artist": "Post Malone & Swae Lee", "mood_score": 0.8, "energy": 0.7, "valence": 0.85, "danceability": 0.7, "acousticness": 0.2, "speechiness": 0.15, "instrumentalness": 0.0, "popularity": 83, "mood_category": "Upbeat & Cheerful"},
        {"name": "Watermelon Sugar", "artist": "Harry Styles", "mood_score": 0.9, "energy": 0.8, "valence": 0.95, "danceability": 0.8, "acousticness": 0.3, "speechiness": 0.05, "instrumentalness": 0.0, "popularity": 82, "mood_category": "Energetic & Happy"},
        {"name": "Flowers", "artist": "Miley Cyrus", "mood_score": 0.85, "energy": 0.8, "valence": 0.8, "danceability": 0.7, "acousticness": 0.3, "speechiness": 0.1, "instrumentalness": 0.0, "popularity": 90, "mood_category": "Energetic & Empowering"},
        {"name": "Unholy", "artist": "Sam Smith ft. Kim Petras", "mood_score": 0.7, "energy": 0.85, "valence": 0.6, "danceability": 0.8, "acousticness": 0.1, "speechiness": 0.2, "instrumentalness": 0.0, "popularity": 88, "mood_category": "Energetic & Edgy"},
        {"name": "About Damn Time", "artist": "Lizzo", "mood_score": 0.95, "energy": 0.9, "valence": 0.95, "danceability": 0.9, "acousticness": 0.1, "speechiness": 0.15, "instrumentalness": 0.0, "popularity": 85, "mood_category": "Energetic & Empowering"},
        {"name": "Bad Habit", "artist": "Steve Lacy", "mood_score": 0.75, "energy": 0.6, "valence": 0.8, "danceability": 0.7, "acousticness": 0.4, "speechiness": 0.1, "instrumentalness": 0.1, "popularity": 81, "mood_category": "Chill & Groovy"},
        {"name": "Running Up That Hill", "artist": "Kate Bush", "mood_score": 0.6, "energy": 0.7, "valence": 0.5, "danceability": 0.6, "acousticness": 0.2, "speechiness": 0.1, "instrumentalness": 0.3, "popularity": 79, "mood_category": "Intense & Emotional"},
        {"name": "I'm Good (Blue)", "artist": "David Guetta & Bebe Rexha", "mood_score": 0.9, "energy": 0.95, "valence": 0.9, "danceability": 0.95, "acousticness": 0.05, "speechiness": 0.1, "instrumentalness": 0.0, "popularity": 87, "mood_category": "Energetic & Euphoric"},
        {"name": "Calm Down", "artist": "Rema", "mood_score": 0.8, "energy": 0.7, "valence": 0.85, "danceability": 0.8, "acousticness": 0.2, "speechiness": 0.1, "instrumentalness": 0.0, "popularity": 83, "mood_category": "Chill & Happy"},
        {"name": "Super Freaky Girl", "artist": "Nicki Minaj", "mood_score": 0.85, "energy": 0.9, "valence": 0.8, "danceability": 0.9, "acousticness": 0.1, "speechiness": 0.4, "instrumentalness": 0.0, "popularity": 82, "mood_category": "Energetic & Confident"},
        {"name": "Break My Soul", "artist": "Beyoncé", "mood_score": 0.9, "energy": 0.95, "valence": 0.85, "danceability": 0.95, "acousticness": 0.05, "speechiness": 0.2, "instrumentalness": 0.0, "popularity": 84, "mood_category": "Energetic & Empowering"}
    ]
    
    mood_summary = {
        "total_tracks": 20,
        "mood_score": 0.82,
        "avg_energy": 0.81,
        "avg_valence": 0.8,
        "avg_danceability": 0.78,
        "avg_acousticness": 0.22,
        "avg_speechiness": 0.13,
        "avg_instrumentalness": 0.02,
        "avg_popularity": 85.5,
        "dominant_mood": "Energetic & Happy",
        "most_common_mood": "Energetic & Happy",
        "mood_distribution": {
            "Energetic & Happy": 6,
            "Energetic & Confident": 3,
            "Energetic & Empowering": 3,
            "Chill & Happy": 3,
            "Upbeat & Cheerful": 2,
            "Other": 3
        },
        "emotional_range": 0.35,
        "using_estimates": False
    }
    
    ai_insights = {
        "emotional_analysis": "This is a high-energy playlist perfect for workouts, parties, or boosting your mood. The tracks show a preference for uplifting, danceable music with strong positive vibes.",
        "personality_traits": ["Energetic", "Optimistic", "Socially confident", "Trend-aware", "Motivation-seeking"],
        "recommendations": ["Perfect for morning motivation", "Great for social gatherings", "Try exploring more dance/electronic genres", "Consider adding some throwback hits"],
        "mood_coaching": "Your music taste suggests you use upbeat music to maintain high energy and positive emotions. This indicates strong emotional regulation skills and a proactive approach to mood management!"
    }
    
    return AnalysisResponse(
        tracks=demo_tracks,
        mood_summary=mood_summary,
        ai_insights=ai_insights,
        playlist_name="✨ Upbeat Vibes - Demo Playlist"
    )

@app.get("/demo/chill")
async def demo_chill_playlist():
    """Demo endpoint with chill/relaxing playlist - 20 songs"""
    demo_tracks = [
        {"name": "Weightless", "artist": "Marconi Union", "mood_score": 0.3, "energy": 0.1, "valence": 0.6, "danceability": 0.2, "acousticness": 0.9, "speechiness": 0.0, "instrumentalness": 0.9, "popularity": 45, "mood_category": "Deeply Relaxing"},
        {"name": "Clair de Lune", "artist": "Claude Debussy", "mood_score": 0.4, "energy": 0.2, "valence": 0.7, "danceability": 0.1, "acousticness": 0.95, "speechiness": 0.0, "instrumentalness": 1.0, "popularity": 40, "mood_category": "Peaceful & Serene"},
        {"name": "River", "artist": "Joni Mitchell", "mood_score": 0.45, "energy": 0.3, "valence": 0.5, "danceability": 0.3, "acousticness": 0.8, "speechiness": 0.05, "instrumentalness": 0.2, "popularity": 50, "mood_category": "Melancholic & Reflective"},
        {"name": "Mad World", "artist": "Gary Jules", "mood_score": 0.2, "energy": 0.2, "valence": 0.2, "danceability": 0.2, "acousticness": 0.9, "speechiness": 0.05, "instrumentalness": 0.3, "popularity": 55, "mood_category": "Melancholic & Contemplative"},
        {"name": "Holocene", "artist": "Bon Iver", "mood_score": 0.4, "energy": 0.3, "valence": 0.4, "danceability": 0.2, "acousticness": 0.8, "speechiness": 0.05, "instrumentalness": 0.4, "popularity": 58, "mood_category": "Contemplative & Peaceful"},
        {"name": "Black", "artist": "Pearl Jam", "mood_score": 0.3, "energy": 0.4, "valence": 0.3, "danceability": 0.3, "acousticness": 0.6, "speechiness": 0.05, "instrumentalness": 0.1, "popularity": 60, "mood_category": "Melancholic & Emotional"},
        {"name": "Breathe Me", "artist": "Sia", "mood_score": 0.35, "energy": 0.4, "valence": 0.3, "danceability": 0.3, "acousticness": 0.7, "speechiness": 0.1, "instrumentalness": 0.2, "popularity": 62, "mood_category": "Vulnerable & Reflective"},
        {"name": "Skinny Love", "artist": "Bon Iver", "mood_score": 0.4, "energy": 0.3, "valence": 0.4, "danceability": 0.2, "acousticness": 0.9, "speechiness": 0.05, "instrumentalness": 0.3, "popularity": 65, "mood_category": "Melancholic & Beautiful"},
        {"name": "The Night We Met", "artist": "Lord Huron", "mood_score": 0.35, "energy": 0.4, "valence": 0.3, "danceability": 0.3, "acousticness": 0.8, "speechiness": 0.05, "instrumentalness": 0.1, "popularity": 68, "mood_category": "Nostalgic & Bittersweet"},
        {"name": "Hurt", "artist": "Johnny Cash", "mood_score": 0.25, "energy": 0.3, "valence": 0.2, "danceability": 0.2, "acousticness": 0.7, "speechiness": 0.1, "instrumentalness": 0.2, "popularity": 70, "mood_category": "Deeply Emotional"},
        {"name": "Hallelujah", "artist": "Jeff Buckley", "mood_score": 0.4, "energy": 0.4, "valence": 0.4, "danceability": 0.2, "acousticness": 0.8, "speechiness": 0.05, "instrumentalness": 0.1, "popularity": 72, "mood_category": "Spiritual & Moving"},
        {"name": "Comfortably Numb", "artist": "Pink Floyd", "mood_score": 0.3, "energy": 0.5, "valence": 0.3, "danceability": 0.3, "acousticness": 0.4, "speechiness": 0.05, "instrumentalness": 0.6, "popularity": 75, "mood_category": "Contemplative & Atmospheric"},
        {"name": "Tears in Heaven", "artist": "Eric Clapton", "mood_score": 0.35, "energy": 0.3, "valence": 0.3, "danceability": 0.2, "acousticness": 0.9, "speechiness": 0.05, "instrumentalness": 0.1, "popularity": 73, "mood_category": "Melancholic & Healing"},
        {"name": "Mad About You", "artist": "Sting", "mood_score": 0.5, "energy": 0.4, "valence": 0.6, "danceability": 0.4, "acousticness": 0.6, "speechiness": 0.05, "instrumentalness": 0.2, "popularity": 58, "mood_category": "Romantic & Gentle"},
        {"name": "Black No. 1", "artist": "Type O Negative", "mood_score": 0.2, "energy": 0.6, "valence": 0.2, "danceability": 0.4, "acousticness": 0.2, "speechiness": 0.1, "instrumentalness": 0.3, "popularity": 45, "mood_category": "Dark & Intense"},
        {"name": "Sour Times", "artist": "Portishead", "mood_score": 0.25, "energy": 0.3, "valence": 0.2, "danceability": 0.4, "acousticness": 0.3, "speechiness": 0.1, "instrumentalness": 0.4, "popularity": 48, "mood_category": "Moody & Atmospheric"},
        {"name": "Teardrop", "artist": "Massive Attack", "mood_score": 0.4, "energy": 0.3, "valence": 0.4, "danceability": 0.5, "acousticness": 0.4, "speechiness": 0.05, "instrumentalness": 0.6, "popularity": 52, "mood_category": "Atmospheric & Emotional"},
        {"name": "Hide and Seek", "artist": "Imogen Heap", "mood_score": 0.3, "energy": 0.2, "valence": 0.3, "danceability": 0.2, "acousticness": 0.8, "speechiness": 0.1, "instrumentalness": 0.7, "popularity": 55, "mood_category": "Ethereal & Haunting"},
        {"name": "Falling", "artist": "Harry Styles", "mood_score": 0.35, "energy": 0.3, "valence": 0.3, "danceability": 0.2, "acousticness": 0.9, "speechiness": 0.05, "instrumentalness": 0.1, "popularity": 78, "mood_category": "Vulnerable & Heartfelt"},
        {"name": "Someone Like You", "artist": "Adele", "mood_score": 0.4, "energy": 0.4, "valence": 0.3, "danceability": 0.3, "acousticness": 0.8, "speechiness": 0.05, "instrumentalness": 0.0, "popularity": 80, "mood_category": "Melancholic & Powerful"}
    ]
    
    mood_summary = {
        "total_tracks": 20,
        "mood_score": 0.34,
        "avg_energy": 0.34,
        "avg_valence": 0.37,
        "avg_danceability": 0.28,
        "avg_acousticness": 0.72,
        "avg_speechiness": 0.06,
        "avg_instrumentalness": 0.32,
        "avg_popularity": 60.7,
        "dominant_mood": "Melancholic & Reflective",
        "most_common_mood": "Melancholic & Reflective",
        "mood_distribution": {
            "Melancholic & Reflective": 6,
            "Contemplative & Peaceful": 4,
            "Atmospheric & Emotional": 3,
            "Vulnerable & Heartfelt": 3,
            "Deeply Emotional": 2,
            "Other": 2
        },
        "emotional_range": 0.6,
        "using_estimates": False
    }
    
    ai_insights = {
        "emotional_analysis": "This playlist reflects a deep, introspective musical taste with preference for emotional depth and atmospheric soundscapes. The music serves as a space for reflection and emotional processing.",
        "personality_traits": ["Introspective", "Emotionally deep", "Artistic", "Contemplative", "Values authenticity"],
        "recommendations": ["Perfect for quiet evenings and reflection", "Great for creative work or meditation", "Consider exploring ambient and post-rock genres", "Try adding some nature sounds for deeper relaxation"],
        "mood_coaching": "Your music choices suggest you're comfortable exploring complex emotions and use music for emotional processing. This indicates high emotional intelligence and self-awareness."
    }
    
    return AnalysisResponse(
        tracks=demo_tracks,
        mood_summary=mood_summary,
        ai_insights=ai_insights,
        playlist_name="🌙 Chill Reflections - Demo Playlist"
    )

@app.get("/demo/mixed")
async def demo_mixed_playlist():
    """Demo endpoint with mixed mood playlist - 20 songs"""
    demo_tracks = [
        {"name": "Bohemian Rhapsody", "artist": "Queen", "mood_score": 0.7, "energy": 0.8, "valence": 0.6, "danceability": 0.5, "acousticness": 0.3, "speechiness": 0.1, "instrumentalness": 0.2, "popularity": 95, "mood_category": "Epic & Dramatic"},
        {"name": "Stairway to Heaven", "artist": "Led Zeppelin", "mood_score": 0.6, "energy": 0.7, "valence": 0.5, "danceability": 0.4, "acousticness": 0.4, "speechiness": 0.05, "instrumentalness": 0.3, "popularity": 90, "mood_category": "Epic & Transcendent"},
        {"name": "Smells Like Teen Spirit", "artist": "Nirvana", "mood_score": 0.5, "energy": 0.9, "valence": 0.4, "danceability": 0.6, "acousticness": 0.1, "speechiness": 0.2, "instrumentalness": 0.1, "popularity": 88, "mood_category": "Energetic & Rebellious"},
        {"name": "Billie Jean", "artist": "Michael Jackson", "mood_score": 0.8, "energy": 0.8, "valence": 0.7, "danceability": 0.9, "acousticness": 0.1, "speechiness": 0.1, "instrumentalness": 0.0, "popularity": 92, "mood_category": "Energetic & Groovy"},
        {"name": "Hotel California", "artist": "Eagles", "mood_score": 0.5, "energy": 0.6, "valence": 0.4, "danceability": 0.4, "acousticness": 0.3, "speechiness": 0.05, "instrumentalness": 0.4, "popularity": 89, "mood_category": "Mysterious & Atmospheric"},
        {"name": "Sweet Child O' Mine", "artist": "Guns N' Roses", "mood_score": 0.8, "energy": 0.9, "valence": 0.8, "danceability": 0.6, "acousticness": 0.1, "speechiness": 0.1, "instrumentalness": 0.2, "popularity": 87, "mood_category": "Energetic & Passionate"},
        {"name": "Imagine", "artist": "John Lennon", "mood_score": 0.6, "energy": 0.3, "valence": 0.7, "danceability": 0.3, "acousticness": 0.8, "speechiness": 0.05, "instrumentalness": 0.1, "popularity": 85, "mood_category": "Peaceful & Hopeful"},
        {"name": "What's Going On", "artist": "Marvin Gaye", "mood_score": 0.5, "energy": 0.5, "valence": 0.4, "danceability": 0.6, "acousticness": 0.3, "speechiness": 0.1, "instrumentalness": 0.2, "popularity": 78, "mood_category": "Contemplative & Soulful"},
        {"name": "Purple Rain", "artist": "Prince", "mood_score": 0.7, "energy": 0.7, "valence": 0.6, "danceability": 0.5, "acousticness": 0.2, "speechiness": 0.1, "instrumentalness": 0.3, "popularity": 84, "mood_category": "Emotional & Powerful"},
        {"name": "Thriller", "artist": "Michael Jackson", "mood_score": 0.8, "energy": 0.9, "valence": 0.7, "danceability": 0.9, "acousticness": 0.1, "speechiness": 0.2, "instrumentalness": 0.1, "popularity": 91, "mood_category": "Energetic & Fun"},
        {"name": "Like a Rolling Stone", "artist": "Bob Dylan", "mood_score": 0.6, "energy": 0.7, "valence": 0.5, "danceability": 0.5, "acousticness": 0.3, "speechiness": 0.3, "instrumentalness": 0.2, "popularity": 80, "mood_category": "Rebellious & Poetic"},
        {"name": "Good Vibrations", "artist": "The Beach Boys", "mood_score": 0.9, "energy": 0.8, "valence": 0.9, "danceability": 0.7, "acousticness": 0.2, "speechiness": 0.1, "instrumentalness": 0.3, "popularity": 82, "mood_category": "Energetic & Joyful"},
        {"name": "What's Love Got to Do with It", "artist": "Tina Turner", "mood_score": 0.7, "energy": 0.8, "valence": 0.6, "danceability": 0.8, "acousticness": 0.1, "speechiness": 0.1, "instrumentalness": 0.0, "popularity": 79, "mood_category": "Energetic & Empowering"},
        {"name": "Born to Run", "artist": "Bruce Springsteen", "mood_score": 0.8, "energy": 0.9, "valence": 0.8, "danceability": 0.6, "acousticness": 0.1, "speechiness": 0.2, "instrumentalness": 0.1, "popularity": 81, "mood_category": "Energetic & Anthemic"},
        {"name": "Bridge Over Troubled Water", "artist": "Simon & Garfunkel", "mood_score": 0.6, "energy": 0.4, "valence": 0.6, "danceability": 0.2, "acousticness": 0.7, "speechiness": 0.05, "instrumentalness": 0.1, "popularity": 77, "mood_category": "Comforting & Spiritual"},
        {"name": "Respect", "artist": "Aretha Franklin", "mood_score": 0.9, "energy": 0.9, "valence": 0.8, "danceability": 0.8, "acousticness": 0.1, "speechiness": 0.2, "instrumentalness": 0.0, "popularity": 86, "mood_category": "Energetic & Empowering"},
        {"name": "The Sound of Silence", "artist": "Simon & Garfunkel", "mood_score": 0.4, "energy": 0.3, "valence": 0.3, "danceability": 0.2, "acousticness": 0.8, "speechiness": 0.05, "instrumentalness": 0.2, "popularity": 83, "mood_category": "Contemplative & Melancholic"},
        {"name": "Yesterday", "artist": "The Beatles", "mood_score": 0.4, "energy": 0.3, "valence": 0.3, "danceability": 0.2, "acousticness": 0.9, "speechiness": 0.05, "instrumentalness": 0.3, "popularity": 88, "mood_category": "Melancholic & Beautiful"},
        {"name": "Don't Stop Believin'", "artist": "Journey", "mood_score": 0.9, "energy": 0.9, "valence": 0.9, "danceability": 0.7, "acousticness": 0.1, "speechiness": 0.1, "instrumentalness": 0.2, "popularity": 89, "mood_category": "Energetic & Uplifting"},
        {"name": "My Girl", "artist": "The Temptations", "mood_score": 0.9, "energy": 0.6, "valence": 0.95, "danceability": 0.7, "acousticness": 0.2, "speechiness": 0.1, "instrumentalness": 0.1, "popularity": 85, "mood_category": "Joyful & Romantic"}
    ]
    
    mood_summary = {
        "total_tracks": 20,
        "mood_score": 0.71,
        "avg_energy": 0.71,
        "avg_valence": 0.64,
        "avg_danceability": 0.57,
        "avg_acousticness": 0.32,
        "avg_speechiness": 0.12,
        "avg_instrumentalness": 0.18,
        "avg_popularity": 85.1,
        "dominant_mood": "Energetic & Powerful",
        "most_common_mood": "Energetic & Powerful",
        "mood_distribution": {
            "Energetic & Powerful": 8,
            "Contemplative & Emotional": 4,
            "Epic & Dramatic": 3,
            "Joyful & Uplifting": 3,
            "Melancholic & Beautiful": 2
        },
        "emotional_range": 0.65,
        "using_estimates": False
    }
    
    ai_insights = {
        "emotional_analysis": "This playlist showcases a sophisticated musical taste spanning multiple decades and genres. You appreciate both emotional depth and energetic anthems, indicating a well-rounded personality that values both introspection and celebration.",
        "personality_traits": ["Musically sophisticated", "Emotionally complex", "Appreciates classics", "Values artistic depth", "Socially adaptable"],
        "recommendations": ["Perfect for road trips and social gatherings", "Great mix for different moods throughout the day", "Consider exploring more contemporary artists with similar depth", "Try creating themed playlists by decade or genre"],
        "mood_coaching": "Your diverse musical taste suggests emotional maturity and the ability to appreciate different perspectives. This playlist could work for almost any social situation - you're the person people trust with the aux cord!"
    }
    
    return AnalysisResponse(
        tracks=demo_tracks,
        mood_summary=mood_summary,
        ai_insights=ai_insights,
        playlist_name="🎭 Classic Mix - Demo Playlist"
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

@app.get("/health")
async def health():
    """Health check endpoint for Railway deployment"""
    return {"status": "healthy", "service": "MoodScope API Bridge"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "MoodScope API Bridge",
        "description": "Bridge between Next.js frontend and MoodScope Python backend",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze (POST)",
            "demo": "/demo (GET) - upbeat playlist demo",
            "demo_upbeat": "/demo/upbeat (GET) - 20 energetic songs",
            "demo_chill": "/demo/chill (GET) - 20 relaxing songs", 
            "demo_mixed": "/demo/mixed (GET) - 20 classic mixed mood songs",
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
    
    uvicorn.run("api_bridge:app", host="0.0.0.0", port=8000, reload=True)
