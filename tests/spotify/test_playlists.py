"""
Test specific Spotify playlist access
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

def test_playlist(playlist_url):
    load_dotenv()
    
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # Extract playlist ID
    if 'playlist/' in playlist_url:
        playlist_id = playlist_url.split('playlist/')[1].split('?')[0]
    else:
        playlist_id = playlist_url
    
    print(f"🔍 Testing playlist ID: {playlist_id}")
    
    try:
        # Get playlist info
        playlist_info = sp.playlist(playlist_id, fields="name,description,public,tracks.total")
        print(f"✅ Playlist found: {playlist_info['name']}")
        print(f"   Total tracks: {playlist_info['tracks']['total']}")
        print(f"   Public: {playlist_info['public']}")
        
        # Try to get tracks
        tracks = sp.playlist_tracks(playlist_id, limit=5)
        print(f"✅ Successfully got {len(tracks['items'])} sample tracks")
        
        for i, item in enumerate(tracks['items'][:3]):
            if item['track']:
                print(f"   {i+1}. {item['track']['name']} by {item['track']['artists'][0]['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the playlists we found that actually work
    test_playlists = [
        "https://open.spotify.com/playlist/6Mf614QiAuop5ud9x5beBS",  # All Time Pop Hits
        "https://open.spotify.com/playlist/34NbomaTu7YuOYnky8nLXL",  # Pop Hits 2025 (Top 50)
        "https://open.spotify.com/playlist/61jNo7WKLOIQkahju8i0hw",  # 100 Greatest Rock Songs
    ]
    
    for playlist_url in test_playlists:
        print(f"\n{'='*50}")
        print(f"Testing: {playlist_url}")
        test_playlist(playlist_url)
