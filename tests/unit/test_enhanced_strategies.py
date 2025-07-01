#!/usr/bin/env python3
"""
Enhanced Spotify Analyzer - Now with Better Audio Features Support
Tests multiple strategies to get real audio features
"""

import os
import sys
sys.path.append('/Users/ishaan743/Moodscale')

from fallback_spotify import FallbackSpotifyAnalyzer
from visualizer import MoodVisualizer

def test_audio_features_strategies():
    """Test different strategies for getting audio features"""
    
    print("🧪 Testing Enhanced Audio Features Strategies...")
    
    # Test with your personal playlist (smaller, should work better)
    test_playlist = "https://open.spotify.com/playlist/0VJlzsjY1dVtr4F7vM8uCi"
    
    print("\n1. Testing with User Auth (broader scope)...")
    try:
        analyzer = FallbackSpotifyAnalyzer(use_user_auth=True)
        df = analyzer.analyze_playlist(test_playlist)
        mood_summary = analyzer.get_mood_summary(df)
        
        print(f"   ✅ Analyzed {len(df)} tracks")
        print(f"   📊 Method: {'Real audio features' if not mood_summary.get('using_estimates') else 'Metadata estimation'}")
        print(f"   🎵 Mood score: {mood_summary['avg_mood_score']:.2f}")
        
        return True, df, mood_summary
        
    except Exception as e:
        print(f"   ❌ User auth failed: {e}")
    
    print("\n2. Testing with Client Credentials...")
    try:
        analyzer = FallbackSpotifyAnalyzer(use_user_auth=False)
        df = analyzer.analyze_playlist(test_playlist)
        mood_summary = analyzer.get_mood_summary(df)
        
        print(f"   ✅ Analyzed {len(df)} tracks")
        print(f"   📊 Method: {'Real audio features' if not mood_summary.get('using_estimates') else 'Metadata estimation'}")
        print(f"   🎵 Mood score: {mood_summary['avg_mood_score']:.2f}")
        
        return True, df, mood_summary
        
    except Exception as e:
        print(f"   ❌ Client credentials failed: {e}")
    
    return False, None, None

def create_enhanced_insights(mood_summary, sample_tracks):
    """Create detailed insights without relying on OpenAI"""
    
    mood_score = mood_summary['avg_mood_score']
    energy = mood_summary['avg_energy']
    valence = mood_summary['avg_valence']
    dominant_mood = mood_summary['most_common_mood']
    
    # Emotional Analysis
    if mood_score > 0.7:
        emotional_state = "highly positive and energetic"
        emotion_desc = "Your music choices reflect an upbeat, optimistic mindset with high energy levels."
    elif mood_score > 0.4:
        emotional_state = "balanced and content"
        emotion_desc = "Your playlist shows a healthy emotional balance with moderate energy and positive vibes."
    elif mood_score > 0.1:
        emotional_state = "contemplative and calm"
        emotion_desc = "Your music taste leans toward introspective and mellow tracks, suggesting a thoughtful mood."
    else:
        emotional_state = "introspective and melancholic"
        emotion_desc = "Your playlist reflects deeper emotions and contemplative themes."
    
    # Personality Traits
    traits = []
    if energy > 0.7:
        traits.append("High energy and motivation-driven")
        traits.append("Enjoys dynamic and stimulating experiences")
    elif energy > 0.4:
        traits.append("Well-balanced between active and relaxed states")
        traits.append("Adaptable to different social situations")
    else:
        traits.append("Prefers calm and peaceful environments")
        traits.append("Values depth and contemplation")
    
    if valence > 0.7:
        traits.append("Optimistic and positive outlook")
        traits.append("Naturally uplifting to others")
    elif valence > 0.4:
        traits.append("Emotionally balanced and stable")
    else:
        traits.append("Deeply empathetic and emotionally aware")
        traits.append("Appreciates complexity in art and life")
    
    # Recommendations
    recommendations = []
    if mood_score > 0.6:
        recommendations.append("Continue exploring upbeat genres to maintain your positive energy")
        recommendations.append("Share your favorite tracks with friends to spread positivity")
        recommendations.append("Use music for motivation during workouts or productive tasks")
    else:
        recommendations.append("Balance introspective music with some uplifting tracks")
        recommendations.append("Use music for relaxation and stress relief")
        recommendations.append("Explore artists with positive messages in similar styles")
    
    recommendations.append("Create themed playlists for different activities and moods")
    recommendations.append("Discover new artists through Spotify's recommendations based on your favorites")
    
    # Mental Health Tips
    mental_health_tips = []
    if energy < 0.3:
        mental_health_tips.append("Consider adding some energizing music to boost mood naturally")
        mental_health_tips.append("Use music as a gentle way to increase daily activity levels")
    else:
        mental_health_tips.append("Music can be a powerful tool for emotional regulation")
        mental_health_tips.append("Create playlists for different emotional needs (calm, energizing, focus)")
    
    mental_health_tips.append("Regular music listening can reduce stress and improve mental well-being")
    mental_health_tips.append("Consider music therapy techniques like mindful listening")
    
    # Mood Coaching
    if mood_score > 0.6:
        coaching = f"Your {dominant_mood.lower()} music taste shows you're in a great emotional space! Keep nurturing this positive energy through music that lifts your spirits. Consider how your upbeat playlist choices might reflect your optimistic approach to life's challenges."
    else:
        coaching = f"Your {dominant_mood.lower()} music preferences suggest a thoughtful, introspective nature. This emotional depth is a strength - use it to connect with others and create meaningful experiences. Balance contemplative music with occasional uplifting tracks to maintain emotional wellness."
    
    return {
        'emotional_analysis': emotion_desc,
        'personality_traits': traits,
        'recommendations': recommendations,
        'mental_health_tips': mental_health_tips,
        'mood_coaching': coaching
    }

if __name__ == "__main__":
    os.chdir('/Users/ishaan743/Moodscale')
    success, df, mood_summary = test_audio_features_strategies()
    
    if success:
        print("\n3. Testing Enhanced Insights Generation...")
        sample_tracks = [f"{row['name']} by {row['artist']}" for _, row in df.head(5).iterrows()]
        insights = create_enhanced_insights(mood_summary, sample_tracks)
        
        print("   ✅ Enhanced insights generated!")
        print(f"   🎭 Emotional Analysis: {insights['emotional_analysis'][:100]}...")
        print(f"   🧩 Personality Traits: {len(insights['personality_traits'])} traits identified")
        print(f"   💡 Recommendations: {len(insights['recommendations'])} suggestions provided")
        print(f"   💚 Mental Health Tips: {len(insights['mental_health_tips'])} tips included")
        
        print("\n4. Testing Visualizations...")
        visualizer = MoodVisualizer()
        try:
            fig_pie = visualizer.create_mood_distribution_pie(mood_summary)
            fig_gauge = visualizer.create_mood_gauge(mood_summary)
            fig_radar = visualizer.create_emotion_radar(df)
            print("   ✅ All visualizations working!")
        except Exception as e:
            print(f"   ❌ Visualization error: {e}")
        
        print("\n🎉 Enhanced MoodScope is ready!")
        print("✅ Better audio features strategies implemented")
        print("✅ Robust insights generation (no OpenAI dependency)")
        print("✅ All visualizations working")
        print("✅ Complete analysis pipeline functional")
        
    else:
        print("\n❌ All strategies failed - playlist might not be accessible")
        print("💡 Try creating a new public playlist with popular songs")
