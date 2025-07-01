#!/usr/bin/env python3
"""
Browser-assisted Spotify OAuth Test
"""

import os
import webbrowser
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def test_browser_oauth():
    """Test OAuth flow with automatic browser opening"""
    load_dotenv()
    
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_uri = "https://127.0.0.1:8501/callback"
    
    print("🌐 Browser-Assisted Spotify OAuth Test")
    print("=" * 45)
    
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
    
    print("🚀 Opening Spotify authorization in your browser...")
    print(f"📱 If browser doesn't open, manually visit:")
    print(f"   {auth_url}")
    
    # Try to open browser
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened!")
    except:
        print("⚠️ Could not open browser automatically")
    
    print(f"\n📋 What will happen:")
    print(f"1. 🌐 Browser opens Spotify login page")
    print(f"2. 🔐 Login with your Spotify account")
    print(f"3. ✅ Click 'Agree' to authorize MoodScope")
    print(f"4. 🔄 You'll be redirected to: https://127.0.0.1:8501/callback?code=...")
    print(f"5. 📋 Copy that ENTIRE redirect URL")
    
    print(f"\n🎯 IMPORTANT:")
    print(f"   - The redirect will show an error page (normal!)")
    print(f"   - Just copy the URL from your browser's address bar")
    print(f"   - Make sure it contains '?code=' in the URL")
    
    # Get callback URL from user
    print(f"\n" + "="*45)
    callback_url = input(f"🔗 Paste the callback URL here: ").strip()
    
    # Validate and process
    if not callback_url:
        print("❌ No URL provided")
        return False
    
    if "authorize?client_id" in callback_url:
        print("❌ You pasted the AUTHORIZATION URL again!")
        print("   You need to CLICK that URL, login, and get the CALLBACK URL")
        print("   The callback URL should contain '?code=' parameter")
        return False
    
    if "127.0.0.1:8501/callback" not in callback_url:
        print("❌ This doesn't look like the correct callback URL")
        print(f"   Expected: https://127.0.0.1:8501/callback?code=...")
        print(f"   Got: {callback_url[:50]}...")
        return False
    
    if "code=" not in callback_url:
        print("❌ No authorization code found in URL")
        print("   Make sure you completed the OAuth flow in the browser")
        return False
    
    try:
        # Extract code from callback URL
        code = callback_url.split("code=")[1].split("&")[0]
        print(f"✅ Authorization code found: {code[:20]}...")
        
        # Exchange code for token
        print("🔄 Exchanging code for access token...")
        token_info = auth_manager.get_access_token(code)
        
        if token_info:
            print(f"✅ Token exchange successful!")
            
            # Test API access
            print("🧪 Testing API access...")
            sp = spotipy.Spotify(auth_manager=auth_manager)
            user = sp.current_user()
            print(f"🎉 SUCCESS! Authenticated as: {user['display_name']} ({user['id']})")
            
            # Test playlist access
            playlists = sp.current_user_playlists(limit=5)
            print(f"📋 Found {len(playlists['items'])} playlists")
            
            return True
        else:
            print(f"❌ Token exchange failed")
            return False
            
    except Exception as e:
        print(f"❌ OAuth failed: {str(e)}")
        
        if "INVALID_CLIENT" in str(e):
            print("\n🔧 SOLUTION: Fix your Spotify app settings:")
            print("   1. Go to: https://developer.spotify.com/dashboard")
            print("   2. Edit your app settings")
            print("   3. Add redirect URI: https://127.0.0.1:8501/callback")
            print("   4. Save and try again")
        
        return False
    
    finally:
        # Clean up test cache
        if os.path.exists(".spotify_cache_test"):
            os.remove(".spotify_cache_test")

if __name__ == "__main__":
    print("🎵 Make sure your Spotify app has redirect URI:")
    print("   https://127.0.0.1:8501/callback")
    print()
    
    success = test_browser_oauth()
    
    if success:
        print(f"\n🎉 OAUTH TEST PASSED!")
        print(f"✅ Your Spotify app is configured correctly")
        print(f"✅ You can now use the enhanced MoodScope app")
        print(f"\n🚀 Next: Run 'python run_https.py' and enjoy real-time analysis!")
    else:
        print(f"\n❌ OAuth test failed")
        print(f"📋 Next steps:")
        print(f"   1. Check Spotify app redirect URI settings")
        print(f"   2. Make sure you complete the full OAuth flow")
        print(f"   3. Copy the callback URL (not authorization URL)")
