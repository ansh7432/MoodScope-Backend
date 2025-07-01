#!/usr/bin/env python3
"""
Quick test to verify enhanced app components render correctly
"""

import os
import sys
sys.path.append('/Users/ishaan743/Moodscale')

from fallback_spotify import FallbackSpotifyAnalyzer
from visualizer import MoodVisualizer

def test_enhanced_app_components():
    """Test that all components work correctly"""
    
    print("🧪 Testing Enhanced App Components...")
    
    # Test 1: Initialize services
    print("\n1. Testing service initialization...")
    try:
        analyzer = FallbackSpotifyAnalyzer(use_user_auth=False)
        visualizer = MoodVisualizer()
        print("   ✅ Services initialized successfully")
    except Exception as e:
        print(f"   ❌ Service initialization failed: {e}")
        return False
    
    # Test 2: Test with verified working playlist
    print("\n2. Testing playlist analysis...")
    test_playlist = "https://open.spotify.com/playlist/67kbhvyUfnMbzgX6zRxrPg"
    
    try:
        df = analyzer.analyze_playlist(test_playlist)
        mood_summary = analyzer.get_mood_summary(df)
        print(f"   ✅ Analyzed {len(df)} tracks successfully")
        print(f"   📊 Mood score: {mood_summary['avg_mood_score']:.2f}")
        print(f"   🎵 Dominant mood: {mood_summary['most_common_mood']}")
    except Exception as e:
        print(f"   ❌ Playlist analysis failed: {e}")
        return False
    
    # Test 3: Test visualizations
    print("\n3. Testing visualizations...")
    try:
        fig_pie = visualizer.create_mood_distribution_pie(mood_summary)
        fig_gauge = visualizer.create_mood_gauge(mood_summary)
        fig_radar = visualizer.create_emotion_radar(df)
        print("   ✅ All visualizations created successfully")
    except Exception as e:
        print(f"   ❌ Visualization creation failed: {e}")
        return False
    
    print("\n🎉 All components test successfully!")
    print("🚀 Enhanced app should render all UI components correctly")
    
    return True

if __name__ == "__main__":
    os.chdir('/Users/ishaan743/Moodscale')
    test_enhanced_app_components()
