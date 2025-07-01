"""
Find working public playlists by searching
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

def find_public_playlists():
    load_dotenv()
    
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    print("🔍 Searching for public playlists...")
    
    # Search for popular public playlists
    search_queries = ["pop hits", "rock classics", "chill music", "rap hits", "indie music"]
    
    working_playlists = []
    
    for query in search_queries:
        try:
            print(f"\n📡 Searching: '{query}'")
            results = sp.search(q=query, type='playlist', limit=10)
            
            for playlist in results['playlists']['items']:
                if playlist and playlist['public'] and playlist['tracks']['total'] > 10:
                    playlist_id = playlist['id']
                    playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
                    
                    print(f"✅ Found: {playlist['name']}")
                    print(f"   Owner: {playlist['owner']['display_name']}")
                    print(f"   Tracks: {playlist['tracks']['total']}")
                    print(f"   URL: {playlist_url}")
                    
                    working_playlists.append({
                        'name': playlist['name'],
                        'url': playlist_url,
                        'tracks': playlist['tracks']['total'],
                        'owner': playlist['owner']['display_name']
                    })
                    
                    if len(working_playlists) >= 5:
                        break
            
            if len(working_playlists) >= 5:
                break
                
        except Exception as e:
            print(f"❌ Error searching '{query}': {str(e)}")
    
    return working_playlists

if __name__ == "__main__":
    playlists = find_public_playlists()
    
    print(f"\n🎯 Found {len(playlists)} working public playlists:")
    print("="*60)
    
    for i, playlist in enumerate(playlists, 1):
        print(f"\n{i}. {playlist['name']}")
        print(f"   Owner: {playlist['owner']}")
        print(f"   Tracks: {playlist['tracks']}")
        print(f"   URL: {playlist['url']}")
    
    print(f"\n🚀 Use any of these URLs in MoodScope!")
    
    if playlists:
        print(f"\n🎵 Try this one first:")
        print(f"   {playlists[0]['url']}")
