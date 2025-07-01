#!/usr/bin/env python3
"""
Search for accessible playlists using search API
"""

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def search_working_playlists():
    """Search for playlists that actually work"""
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
    
    print("🔍 Searching for accessible playlists...")
    print("=" * 50)
    
    working_playlists = []
    
    # Search for popular playlists by keyword
    search_terms = ["pop", "rock", "hip hop", "chill", "workout"]
    
    for term in search_terms:
        try:
            print(f"🔍 Searching for '{term}' playlists...")
            results = sp.search(q=term, type='playlist', limit=10)
            
            for playlist in results['playlists']['items']:
                try:
                    # Test if we can access this playlist
                    test = sp.playlist(playlist['id'], fields="name,tracks.total,owner.display_name")
                    if test['tracks']['total'] > 20:  # Only playlists with decent tracks
                        working_playlists.append({
                            'name': test['name'],
                            'id': playlist['id'],
                            'url': f"https://open.spotify.com/playlist/{playlist['id']}",
                            'tracks': test['tracks']['total'],
                            'owner': test['owner']['display_name']
                        })
                        print(f"✅ {test['name']} by {test['owner']['display_name']} - {test['tracks']['total']} tracks")
                        
                        # Stop after finding 3 working playlists per term
                        if len([p for p in working_playlists if term in p['name'].lower()]) >= 2:
                            break
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"❌ Search error for '{term}': {e}")
            continue
    
    # Remove duplicates
    unique_playlists = []
    seen_ids = set()
    for playlist in working_playlists:
        if playlist['id'] not in seen_ids:
            unique_playlists.append(playlist)
            seen_ids.add(playlist['id'])
    
    print(f"\n🎯 Found {len(unique_playlists)} unique working playlists!")
    print("=" * 50)
    
    # Show top 5 results
    for i, playlist in enumerate(unique_playlists[:5], 1):
        print(f"{i}. {playlist['name']}")
        print(f"   URL: {playlist['url']}")
        print(f"   Owner: {playlist['owner']}")
        print(f"   Tracks: {playlist['tracks']}")
        print()
    
    return unique_playlists

if __name__ == "__main__":
    playlists = search_working_playlists()
    
    if playlists:
        print("🎉 Success! Copy any of the URLs above to test in MoodScope.")
        print("\n📋 Quick Test URLs:")
        for playlist in playlists[:3]:
            print(f"• {playlist['url']}")
    else:
        print("⚠️ No working playlists found.")
        print("💡 Try creating your own playlist on Spotify and using that URL!")
