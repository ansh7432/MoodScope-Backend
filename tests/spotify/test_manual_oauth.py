#!/usr/bin/env python3
"""
Simple Spotify OAuth Test - Manual Flow
"""

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def test_manual_oauth():
    """Test OAuth flow with manual token exchange"""
    load_dotenv()
    
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_uri = "https://127.0.0.1:8501/callback"
    
    print("🔐 Manual Spotify OAuth Test")
    print("=" * 40)
    
    # Create auth manager
    scope = "user-read-private user-read-email playlist-read-private playlist-read-collaborative"
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path=".spotify_cache_test"
    )
    
    # Get authorization URL
    auth_url = auth_manager.get_authorize_url()
    print(f"🔗 Authorization URL:")
    print(f"{auth_url}")
    
    print(f"\n📋 Steps to Complete OAuth:")
    print(f"1. Copy the URL above")
    print(f"2. Open it in your browser")
    print(f"3. Login to Spotify and click 'Agree'")
    print(f"4. You'll be redirected to a URL starting with:")
    print(f"   https://127.0.0.1:8501/callback?code=...")
    print(f"5. Copy that ENTIRE callback URL and paste it below")
    
    # Get callback URL from user
    callback_url = input(f"\n🔗 Enter the callback URL you were redirected to: ").strip()
    
    try:
        # Extract code from callback URL
        if "code=" in callback_url:
            code = callback_url.split("code=")[1].split("&")[0]
            print(f"✅ Authorization code extracted: {code[:20]}...")
            
            # Exchange code for token
            token_info = auth_manager.get_access_token(code)
            if token_info:
                print(f"✅ Token exchange successful!")
                
                # Test API access
                sp = spotipy.Spotify(auth_manager=auth_manager)
                user = sp.current_user()
                print(f"✅ Authenticated as: {user['display_name']} ({user['id']})")
                
                return True
            else:
                print(f"❌ Token exchange failed")
                return False
        else:
            print(f"❌ No authorization code found in URL")
            print(f"   Make sure you copied the FULL callback URL")
            return False
            
    except Exception as e:
        print(f"❌ OAuth failed: {str(e)}")
        return False
    
    finally:
        # Clean up test cache
        if os.path.exists(".spotify_cache_test"):
            os.remove(".spotify_cache_test")

if __name__ == "__main__":
    success = test_manual_oauth()
    if success:
        print(f"\n🎉 OAuth test successful! Your Spotify app is configured correctly.")
    else:
        print(f"\n⚠️ OAuth test failed. Check your Spotify app settings:")
        print(f"   - Redirect URI: https://127.0.0.1:8501/callback")
        print(f"   - Make sure the app is not in 'Review' status")
