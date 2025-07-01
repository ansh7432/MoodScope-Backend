#!/usr/bin/env python3
"""
Quick test of a working playlist
"""

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def test_playlist(playlist_url):
    """Test a specific playlist"""
    load_dotenv()
    
    # Initialize Spotify with user auth
    auth_manager = SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri="https://127.0.0.1:8501/callback",
        scope="user-read-private user-read-email playlist-read-private playlist-read-collaborative",
        cache_path=".spotify_cache"
    )
    
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Extract playlist ID
    playlist_id = playlist_url.split('playlist/')[1].split('?')[0]
    
    print(f"🧪 Testing playlist: {playlist_url}")
    print(f"📋 ID: {playlist_id}")
    print("=" * 50)
    
    try:
        # Get playlist info
        playlist_info = sp.playlist(playlist_id, fields="name,tracks.total,owner.display_name")
        print(f"✅ Name: {playlist_info['name']}")
        print(f"✅ Owner: {playlist_info['owner']['display_name']}")
        print(f"✅ Tracks: {playlist_info['tracks']['total']}")
        
        # Get first few tracks
        tracks = sp.playlist_tracks(playlist_id, limit=5)
        print(f"\n🎵 First 5 tracks:")
        for i, item in enumerate(tracks['items'], 1):
            if item['track']:
                print(f"   {i}. {item['track']['name']} - {item['track']['artists'][0]['name']}")
        
        # Test audio features for first track
        if tracks['items'] and tracks['items'][0]['track']:
            track_id = tracks['items'][0]['track']['id']
            features = sp.audio_features([track_id])
            if features and features[0]:
                print(f"\n🎯 Audio features sample:")
                print(f"   Energy: {features[0]['energy']:.2f}")
                print(f"   Valence: {features[0]['valence']:.2f}")
                print(f"   Danceability: {features[0]['danceability']:.2f}")
        
        print(f"\n🎉 SUCCESS! This playlist works perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the first working playlist
    test_url = "https://open.spotify.com/playlist/67kbhvyUfnMbzgX6zRxrPg"
    success = test_playlist(test_url)
    
    if success:
        print(f"\n✅ Great! Use this URL in MoodScope: {test_url}")
    else:
        print(f"\n❌ This playlist didn't work, try another from the list.")
