"""
Test Spotify API Connection
Quick script to verify your Spotify credentials work
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

def test_spotify_connection():
    print("🔍 Testing Spotify API Connection...")
    
    # Load environment variables
    load_dotenv()
    
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    print(f"Client ID: {client_id[:10]}..." if client_id else "❌ No Client ID found")
    print(f"Client Secret: {client_secret[:10]}..." if client_secret else "❌ No Client Secret found")
    
    if not client_id or not client_secret:
        print("❌ Missing Spotify credentials in .env file")
        return False
    
    try:
        # Test authentication
        print("\n🔐 Testing authentication...")
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Test API call
        print("📡 Testing API call...")
        result = sp.search(q="The Beatles", limit=1, type='artist')
        
        if result and result['artists']['items']:
            artist = result['artists']['items'][0]
            print(f"✅ SUCCESS! Found artist: {artist['name']}")
            print(f"   Followers: {artist['followers']['total']:,}")
            return True
        else:
            print("❌ No results from search")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_spotify_connection()
    
    if success:
        print("\n🎉 Your Spotify API is working correctly!")
        print("You can now use MoodScope with real playlists.")
    else:
        print("\n🚨 Please check your Spotify API credentials:")
        print("1. Go to: https://developer.spotify.com/dashboard")
        print("2. Create a new app or check existing app")
        print("3. Copy Client ID and Client Secret to .env file")
        print("4. Make sure credentials are correct (no extra quotes/spaces)")
