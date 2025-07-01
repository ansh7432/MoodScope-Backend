#!/usr/bin/env python3
"""
Test the exact same workflow as enhanced app to debug
"""

import os
import sys
sys.path.append('/Users/ishaan743/Moodscale')

from fallback_spotify import FallbackSpotifyAnalyzer
from ai_insights import MoodAI
from visualizer import MoodVisualizer

def test_exact_workflow():
    """Test the exact same workflow as enhanced app"""
    
    print("🧪 Testing Enhanced App Workflow...")
    
    # Use the exact same playlist that was successful in terminal
    playlist_url = "https://open.spotify.com/playlist/4stlIpoPS7uKCsmUA7D8KZ"
    
    # Initialize services exactly like enhanced app
    print("\n1. Initializing services...")
    try:
        spotify_analyzer = FallbackSpotifyAnalyzer(use_user_auth=True)
        print("   ✅ Spotify analyzer initialized")
        
        try:
            mood_ai = MoodAI()
            print("   ✅ AI service initialized")
        except Exception as ai_error:
            print(f"   ⚠️ AI service failed: {ai_error}")
            mood_ai = None
        
        visualizer = MoodVisualizer()
        print("   ✅ Visualizer initialized")
        
    except Exception as e:
        print(f"   ❌ Service initialization failed: {e}")
        return False
    
    # Analyze playlist exactly like enhanced app
    print(f"\n2. Analyzing playlist: {playlist_url}")
    try:
        # Get playlist data
        df = spotify_analyzer.analyze_playlist(playlist_url)
        mood_summary = spotify_analyzer.get_mood_summary(df)
        print(f"   ✅ Analyzed {len(df)} tracks")
        print(f"   📊 Mood summary: {mood_summary}")
        
        # Generate AI insights with fallback
        insights = None
        if mood_ai:
            try:
                sample_tracks = [f"{row['name']} by {row['artist']}" for _, row in df.head(10).iterrows()]
                insights = mood_ai.generate_mood_insights(mood_summary, sample_tracks)
                print("   ✅ AI insights generated")
            except Exception as ai_error:
                print(f"   ⚠️ AI insights failed: {ai_error}")
                insights = None
        
        # Create fallback insights if needed
        if not insights:
            insights = {
                'emotional_analysis': f"Your playlist shows a {mood_summary['most_common_mood'].lower()} mood with an average mood score of {mood_summary['avg_mood_score']:.2f}.",
                'personality_traits': [f"You enjoy {mood_summary['most_common_mood'].lower()} music"],
                'recommendations': ["Keep exploring music that matches your mood!"],
                'mood_coaching': f"Your music taste reflects a {mood_summary['most_common_mood'].lower()} personality."
            }
            print("   ✅ Fallback insights created")
        
    except Exception as e:
        print(f"   ❌ Analysis failed: {e}")
        return False
    
    # Test visualizations
    print("\n3. Testing visualizations...")
    try:
        fig_pie = visualizer.create_mood_distribution_pie(mood_summary)
        fig_gauge = visualizer.create_mood_gauge(mood_summary)
        fig_radar = visualizer.create_emotion_radar(df)
        print("   ✅ All visualizations created")
    except Exception as e:
        print(f"   ❌ Visualization failed: {e}")
        return False
    
    print("\n🎉 Complete workflow successful!")
    print("📊 Results summary:")
    print(f"   • Tracks analyzed: {len(df)}")
    print(f"   • Mood score: {mood_summary['avg_mood_score']:.2f}")
    print(f"   • Dominant mood: {mood_summary['most_common_mood']}")
    print(f"   • Energy level: {mood_summary['avg_energy']:.2f}")
    print(f"   • Using estimates: {mood_summary.get('using_estimates', False)}")
    print("   • AI insights: ✅" if insights else "   • AI insights: ❌")
    print("   • Visualizations: ✅")
    
    return True, df, mood_summary, insights

if __name__ == "__main__":
    os.chdir('/Users/ishaan743/Moodscale')
    test_exact_workflow()
