#!/usr/bin/env python3
"""
Test OAuth flow for MoodScope Enhanced Spotify Integration
"""

import sys
import os
from dotenv import load_dotenv
from enhanced_spotify import EnhancedSpotifyAnalyzer

def test_oauth_flow():
    """Test the OAuth authentication flow"""
    print("🔐 Testing MoodScope OAuth Flow...")
    
    load_dotenv()
    
    # Check environment variables
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
    
    print(f"✅ Client ID: {client_id[:10]}..." if client_id else "❌ Client ID missing")
    print(f"✅ Client Secret: {client_secret[:10]}..." if client_secret else "❌ Client Secret missing")
    print(f"✅ Redirect URI: {redirect_uri}" if redirect_uri else "❌ Redirect URI missing")
    
    if not all([client_id, client_secret]):
        print("❌ Missing Spotify credentials")
        return False
    
    try:
        # Initialize enhanced analyzer
        print("\n🎵 Initializing Enhanced Spotify Analyzer...")
        analyzer = EnhancedSpotifyAnalyzer(use_user_auth=True)
        
        # Get auth URL
        print("🔗 Getting authorization URL...")
        auth_url = analyzer.get_auth_url()
        
        if auth_url:
            print(f"✅ Authorization URL generated successfully!")
            print(f"🌐 URL: {auth_url[:50]}...")
            print(f"🔑 Redirect URI configured: {analyzer.redirect_uri}")
            return True
        else:
            print("❌ Failed to generate authorization URL")
            return False
            
    except Exception as e:
        print(f"❌ OAuth test failed: {str(e)}")
        return False

def test_api_access():
    """Test basic API access"""
    print("\n🧪 Testing API Access...")
    
    try:
        # Test with client credentials (no user auth)
        analyzer = EnhancedSpotifyAnalyzer(use_user_auth=False)
        
        # Test search
        results = analyzer.sp.search(q="test", type="track", limit=1)
        if results and results['tracks']['items']:
            print("✅ Basic API access working")
            return True
        else:
            print("❌ API search returned no results")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎵 MoodScope OAuth & API Test Suite")
    print("=" * 40)
    
    oauth_success = test_oauth_flow()
    api_success = test_api_access()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"🔐 OAuth Flow: {'✅ PASS' if oauth_success else '❌ FAIL'}")
    print(f"🎵 API Access: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if oauth_success and api_success:
        print("\n🎉 All tests passed! MoodScope is ready for real-time analysis.")
        print("🚀 Next step: Run 'python run_https.py' and connect your Spotify account")
    else:
        print("\n⚠️  Some tests failed. Check your configuration:")
        print("   1. Verify .env file has correct Spotify credentials")
        print("   2. Check Spotify Developer Dashboard redirect URIs")
        print("   3. Ensure internet connection for API access")
    
    sys.exit(0 if oauth_success and api_success else 1)
