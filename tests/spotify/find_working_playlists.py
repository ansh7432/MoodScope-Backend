#!/usr/bin/env python3
"""
Find working Spotify playlists for MoodScope
"""

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def find_working_playlists():
    """Find actual working Spotify playlists"""
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
    
    print("🔍 Finding working Spotify playlists...")
    print("=" * 50)
    
    # Test various playlist sources
    working_playlists = []
    
    # 1. Try featured playlists
    try:
        print("📋 Checking featured playlists...")
        featured = sp.featured_playlists(limit=10)
        for playlist in featured['playlists']['items']:
            try:
                # Test if we can access this playlist
                test = sp.playlist(playlist['id'], fields="name,tracks.total")
                if test['tracks']['total'] > 0:
                    working_playlists.append({
                        'name': test['name'],
                        'id': playlist['id'],
                        'url': f"https://open.spotify.com/playlist/{playlist['id']}",
                        'tracks': test['tracks']['total']
                    })
                    print(f"✅ {test['name']} - {test['tracks']['total']} tracks")
            except:
                pass
    except Exception as e:
        print(f"⚠️ Featured playlists error: {e}")
    
    # 2. Try user's own playlists
    try:
        print("\n📋 Checking your playlists...")
        user_playlists = sp.current_user_playlists(limit=5)
        for playlist in user_playlists['items']:
            if playlist['tracks']['total'] > 10:  # Only playlists with decent number of tracks
                working_playlists.append({
                    'name': playlist['name'],
                    'id': playlist['id'],
                    'url': f"https://open.spotify.com/playlist/{playlist['id']}",
                    'tracks': playlist['tracks']['total'],
                    'owner': playlist['owner']['display_name']
                })
                print(f"✅ {playlist['name']} - {playlist['tracks']['total']} tracks (your playlist)")
    except Exception as e:
        print(f"⚠️ User playlists error: {e}")
    
    # 3. Try some known working playlist IDs
    print("\n📋 Testing known playlist IDs...")
    known_ids = [
        "37i9dQZF1DX0XUsuxWHRQd",  # RapCaviar
        "37i9dQZF1DXcBWIGoYBM5M",  # Today's Top Hits
        "37i9dQZF1DX1lVhptIYRda",  # Hot Country
        "37i9dQZF1DX4JAvHpjipBk",  # New Music Friday
    ]
    
    for playlist_id in known_ids:
        try:
            test = sp.playlist(playlist_id, fields="name,tracks.total")
            working_playlists.append({
                'name': test['name'],
                'id': playlist_id,
                'url': f"https://open.spotify.com/playlist/{playlist_id}",
                'tracks': test['tracks']['total']
            })
            print(f"✅ {test['name']} - {test['tracks']['total']} tracks")
        except Exception as e:
            print(f"❌ {playlist_id} - {str(e)}")
    
    print(f"\n🎯 Found {len(working_playlists)} working playlists!")
    print("=" * 50)
    
    # Show results
    for i, playlist in enumerate(working_playlists[:5], 1):
        print(f"{i}. {playlist['name']}")
        print(f"   URL: {playlist['url']}")
        print(f"   Tracks: {playlist['tracks']}")
        if 'owner' in playlist:
            print(f"   Owner: {playlist['owner']}")
        print()
    
    return working_playlists

if __name__ == "__main__":
    playlists = find_working_playlists()
    
    if playlists:
        print("🎉 Success! Copy any of the URLs above to test in MoodScope.")
    else:
        print("⚠️ No working playlists found. Check your authentication.")
