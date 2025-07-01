"""
Minimal test for Spotify audio features access
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

def test_audio_features():
    load_dotenv()
    
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    print(f"🔑 Using Client ID: {client_id[:10]}...")
    
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # Test with a single, well-known track
    test_track_id = "3n3Ppam7vgaVa1iaRUc9LP"  # Mr. Brightside by The Killers
    
    print(f"🎵 Testing audio features for track ID: {test_track_id}")
    
    try:
        # First, verify we can get track info
        track_info = sp.track(test_track_id)
        print(f"✅ Track info: {track_info['name']} by {track_info['artists'][0]['name']}")
        
        # Now test audio features
        print("🎵 Requesting audio features...")
        audio_features = sp.audio_features([test_track_id])
        
        if audio_features and audio_features[0]:
            features = audio_features[0]
            print("✅ SUCCESS! Audio features retrieved:")
            print(f"   Valence: {features['valence']:.3f}")
            print(f"   Energy: {features['energy']:.3f}")
            print(f"   Danceability: {features['danceability']:.3f}")
            print(f"   Tempo: {features['tempo']:.1f} BPM")
            return True
        else:
            print("❌ No audio features returned")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        
        if "403" in str(e):
            print("\n🚨 403 Forbidden Error - Possible causes:")
            print("1. Your Spotify app may not have the right permissions")
            print("2. Audio features endpoint might require different auth")
            print("3. Your app might be in development mode with restrictions")
            print("\n💡 Solutions:")
            print("1. Check Spotify Developer Dashboard settings")
            print("2. Try creating a new Spotify app")
            print("3. Ensure app is set to 'Development' mode initially")
        
        return False

if __name__ == "__main__":
    success = test_audio_features()
    
    if not success:
        print("\n🔄 Potential workaround: Use demo mode for now")
        print("   Run: streamlit run demo_app.py")
        print("   This shows full functionality without API limitations")
