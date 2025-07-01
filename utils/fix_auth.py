"""
Quick Fix for Spotify Authentication Issues
Run this if the enhanced app gets stuck on "loading"
"""

import os

def fix_spotify_auth():
    """Clear Spotify cache and reset authentication"""
    
    # Remove cache file if it exists
    if os.path.exists('.spotify_cache'):
        os.remove('.spotify_cache')
        print("✅ Cleared Spotify cache")
    
    # Remove any lock files
    for file in ['.cache', '.spotify_cache.lock']:
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ Removed {file}")
    
    print("\n🎵 Authentication reset complete!")
    print("Now you can try connecting again.")

if __name__ == "__main__":
    fix_spotify_auth()
