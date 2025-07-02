#!/usr/bin/env python3
"""
Enhanced Spotify Analyzer with Audio Features Fallback & AI Mood Categorization
Works even when audio features API is restricted, now with AI-powered mood analysis
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

# Import AI mood categorizer
try:
    from .ai_mood_categorizer import HuggingFaceMoodCategorizer
    AI_AVAILABLE = True
    print("🤖 AI mood categorizer available!")
except ImportError as e:
    AI_AVAILABLE = False
    print(f"⚠️ AI mood categorizer not available: {e}")

load_dotenv()

class FallbackSpotifyAnalyzer:
    def __init__(self, use_user_auth=False):  # Default to False for easier usage
        """Initialize Spotify client with fallback capabilities and AI mood categorization"""
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = "https://127.0.0.1:8501/callback"
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Spotify credentials not found. Please check your .env file.")
        
        self.use_user_auth = use_user_auth
        self.sp = None
        self._initialize_spotify()
        
        # Initialize AI mood categorizer
        self.ai_categorizer = None
        if AI_AVAILABLE:
            try:
                self.ai_categorizer = HuggingFaceMoodCategorizer()
                print("✅ AI mood categorizer initialized!")
            except Exception as e:
                print(f"⚠️ AI categorizer failed to load: {e}")
                self.ai_categorizer = None
    
    def _initialize_spotify(self):
        """Initialize Spotify client with appropriate auth method"""
        try:
            if self.use_user_auth:
                scope = "user-read-private user-read-email playlist-read-private playlist-read-collaborative user-library-read user-top-read user-read-recently-played"
                
                auth_manager = SpotifyOAuth(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    redirect_uri=self.redirect_uri,
                    scope=scope,
                    cache_path=".spotify_cache",
                    open_browser=True,  # Auto-open browser
                    show_dialog=False   # Skip permission dialog if already authorized
                )
                
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
                print("✅ Spotify connected with User Auth")
                
            else:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                print("✅ Spotify connected with Client Credentials")
        
        except Exception as e:
            if self.use_user_auth:
                print(f"❌ User auth failed: {str(e)}")
                print("🔄 Falling back to client credentials...")
                self.use_user_auth = False
                self._initialize_spotify()
            else:
                raise Exception(f"Spotify connection failed: {str(e)}")
    
    def get_auth_url(self):
        """Get authorization URL for user authentication"""
        if self.use_user_auth:
            scope = "user-read-private user-read-email playlist-read-private playlist-read-collaborative"
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=scope,
                cache_path=".spotify_cache"
            )
            return auth_manager.get_authorize_url()
        return None
    
    def extract_playlist_id(self, playlist_url: str) -> str:
        """Extract playlist ID from Spotify URL"""
        if 'playlist/' in playlist_url:
            return playlist_url.split('playlist/')[1].split('?')[0]
        return playlist_url
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """Get all tracks from a playlist"""
        try:
            print(f"🎵 Fetching playlist tracks for ID: {playlist_id}")
            
            # Get playlist info first
            try:
                playlist_info = self.sp.playlist(playlist_id, fields="name,public,tracks.total")
                print(f"📋 Playlist: {playlist_info['name']} ({playlist_info['tracks']['total']} tracks)")
            except Exception as e:
                if "404" in str(e):
                    raise Exception(f"Playlist not found (ID: {playlist_id}). Please check the URL and make sure the playlist is public or you have access to it.")
                elif "403" in str(e):
                    raise Exception(f"Access denied to playlist (ID: {playlist_id}). The playlist may be private or region-restricted.")
                else:
                    raise Exception(f"Error accessing playlist: {str(e)}")
            
            # Get tracks
            results = self.sp.playlist_tracks(playlist_id)
            tracks = []
            
            # Handle pagination
            while results:
                for item in results['items']:
                    if item['track'] and item['track']['id']:
                        # Get artist genres to help with mood estimation
                        artist_info = None
                        try:
                            artist_info = self.sp.artist(item['track']['artists'][0]['id'])
                        except:
                            pass
                        
                        track_info = {
                            'id': item['track']['id'],
                            'name': item['track']['name'],
                            'artist': ', '.join([artist['name'] for artist in item['track']['artists']]),
                            'album': item['track']['album']['name'],
                            'popularity': item['track']['popularity'],
                            'duration_ms': item['track']['duration_ms'],
                            'release_date': item['track']['album']['release_date'],
                            'artist_genres': artist_info['genres'] if artist_info else [],
                            'explicit': item['track']['explicit']
                        }
                        tracks.append(track_info)
                
                results = self.sp.next(results) if results['next'] else None
            
            print(f"✅ Retrieved {len(tracks)} valid tracks")
            return tracks
            
        except Exception as e:
            raise Exception(f"Error fetching playlist: {str(e)}")
    
    def estimate_mood_from_metadata(self, tracks: List[Dict]) -> pd.DataFrame:
        """Estimate mood features using AI-enhanced analysis or metadata fallback"""
        print("🎯 Audio features not available - using AI-enhanced mood estimation")
        
        # Use AI categorizer if available
        if self.ai_categorizer:
            print("🤖 Using AI mood categorization...")
            df = self.ai_categorizer.categorize_tracks_batch(tracks)
            
            # Ensure required columns exist (in case AI didn't provide them)
            if 'danceability' not in df.columns:
                df['danceability'] = df['energy'] * 0.8  # Estimate from energy
            if 'intensity' not in df.columns:
                df['intensity'] = np.sqrt((df['valence'] - 0.5)**2 + (df['energy'] - 0.5)**2)
            
            print("✅ AI mood categorization complete!")
            return df
        
        else:
            # Fallback to rule-based analysis
            print("🔄 Using rule-based mood estimation...")
            return self._estimate_mood_basic(tracks)
    
    def _estimate_mood_basic(self, tracks: List[Dict]) -> pd.DataFrame:
        """Basic rule-based mood estimation (fallback when AI unavailable)"""
        print("📊 Using basic metadata-based mood estimation")
        
        df = pd.DataFrame(tracks)
        
        # Create estimated mood features based on available data
        np.random.seed(42)  # For consistent results
        
        # Estimate energy based on genres and popularity
        def estimate_energy(row):
            energy = 0.5  # baseline
            if any(genre in ' '.join(row['artist_genres']).lower() for genre in ['rock', 'metal', 'punk', 'electronic', 'dance']):
                energy += 0.3
            if any(genre in ' '.join(row['artist_genres']).lower() for genre in ['acoustic', 'folk', 'ambient', 'classical']):
                energy -= 0.2
            if row['popularity'] > 70:
                energy += 0.1
            return np.clip(energy + np.random.normal(0, 0.1), 0, 1)
        
        # Estimate valence (positivity) based on genres
        def estimate_valence(row):
            valence = 0.5  # baseline
            if any(genre in ' '.join(row['artist_genres']).lower() for genre in ['pop', 'dance', 'happy', 'upbeat']):
                valence += 0.3
            if any(genre in ' '.join(row['artist_genres']).lower() for genre in ['sad', 'melancholy', 'blues', 'emo']):
                valence -= 0.3
            return np.clip(valence + np.random.normal(0, 0.15), 0, 1)
        
        # Estimate danceability
        def estimate_danceability(row):
            danceability = 0.5
            if any(genre in ' '.join(row['artist_genres']).lower() for genre in ['dance', 'electronic', 'pop', 'hip hop', 'disco']):
                danceability += 0.3
            if any(genre in ' '.join(row['artist_genres']).lower() for genre in ['classical', 'ambient', 'folk']):
                danceability -= 0.2
            return np.clip(danceability + np.random.normal(0, 0.1), 0, 1)
        
        # Apply estimations
        df['energy'] = df.apply(estimate_energy, axis=1)
        df['valence'] = df.apply(estimate_valence, axis=1)
        df['danceability'] = df.apply(estimate_danceability, axis=1)
        
        # Create other estimated features
        df['acousticness'] = np.random.beta(2, 5, len(df))  # Generally low
        df['instrumentalness'] = np.random.beta(1, 10, len(df))  # Very low for most songs
        df['speechiness'] = np.random.beta(1, 5, len(df))  # Low for most songs
        df['tempo'] = np.random.normal(120, 30, len(df))  # Around 120 BPM average
        df['loudness'] = np.random.normal(-8, 4, len(df))  # Typical loudness range
        
        # Calculate mood metrics
        df = self.calculate_mood_metrics(df)
        
        print(f"🎯 Estimated mood features for {len(df)} tracks using metadata")
        return df
    
    def analyze_playlist(self, playlist_url: str) -> pd.DataFrame:
        """Complete playlist analysis with fallback to metadata-based estimation"""
        playlist_id = self.extract_playlist_id(playlist_url)
        
        # Get tracks
        tracks = self.get_playlist_tracks(playlist_id)
        if not tracks:
            raise Exception("No tracks found in playlist")
        
        # Limit to first 100 tracks for performance
        if len(tracks) > 100:
            print(f"⚠️  Large playlist detected. Analyzing first 100 of {len(tracks)} tracks")
            tracks = tracks[:100]
        
        # Try to get audio features with multiple strategies
        try:
            print("🎵 Attempting to get audio features...")
            track_ids = [track['id'] for track in tracks]
            
            # Strategy 1: Test with first track
            test_features = self.sp.audio_features([track_ids[0]])
            if test_features and test_features[0]:
                print("✅ Audio features API working - getting full data...")
                # Get all features if the first one works
                all_features = []
                batch_size = 50
                for i in range(0, len(track_ids), batch_size):
                    batch = track_ids[i:i+batch_size]
                    features = self.sp.audio_features(batch)
                    if features:
                        all_features.extend([f for f in features if f is not None])
                
                if all_features:
                    df_tracks = pd.DataFrame(tracks)
                    df_features = pd.DataFrame(all_features)
                    df = pd.merge(df_tracks, df_features, left_on='id', right_on='id', how='inner')
                    df = self.calculate_mood_metrics(df)
                    print(f"🎯 Analysis complete: {len(df)} tracks with real audio features")
                    return df
                else:
                    raise Exception("No valid audio features")
            else:
                raise Exception("Initial audio features test failed")
                
        except Exception as e:
            print(f"⚠️  Primary audio features failed: {str(e)}")
            
            # Strategy 2: Try with client credentials if using user auth
            if self.use_user_auth:
                print("🔄 Trying with client credentials authentication...")
                try:
                    temp_client = spotipy.Spotify(
                        client_credentials_manager=SpotifyClientCredentials(
                            client_id=self.client_id,
                            client_secret=self.client_secret
                        )
                    )
                    
                    # Test first
                    test_features = temp_client.audio_features([track_ids[0]])
                    if test_features and test_features[0]:
                        print("✅ Client credentials working - getting audio features...")
                        all_features = []
                        batch_size = 50
                        for i in range(0, len(track_ids), batch_size):
                            batch = track_ids[i:i+batch_size]
                            features = temp_client.audio_features(batch)
                            if features:
                                all_features.extend([f for f in features if f is not None])
                        
                        if all_features:
                            df_tracks = pd.DataFrame(tracks)
                            df_features = pd.DataFrame(all_features)
                            df = pd.merge(df_tracks, df_features, left_on='id', right_on='id', how='inner')
                            df = self.calculate_mood_metrics(df)
                            print(f"🎯 Analysis complete: {len(df)} tracks with real audio features (client creds)")
                            return df
                            
                except Exception as cred_error:
                    print(f"⚠️  Client credentials also failed: {str(cred_error)}")
            
            # Strategy 3: Fallback to metadata estimation
            print("🔄 Falling back to metadata-based mood estimation...")
            return self.estimate_mood_from_metadata(tracks)
    
    def calculate_mood_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate mood-related metrics from audio features or estimates"""
        
        # Mood Score (0-1, higher = happier/more energetic)
        df['mood_score'] = (df['valence'] * 0.6 + df['energy'] * 0.4)
        
        # Mood Category
        def categorize_mood(row):
            if row['valence'] >= 0.6 and row['energy'] >= 0.6:
                return 'Happy & Energetic'
            elif row['valence'] >= 0.6 and row['energy'] < 0.6:
                return 'Happy & Calm'
            elif row['valence'] < 0.4 and row['energy'] >= 0.6:
                return 'Sad & Energetic'
            elif row['valence'] < 0.4 and row['energy'] < 0.4:
                return 'Sad & Calm'
            else:
                return 'Neutral'
        
        df['mood_category'] = df.apply(categorize_mood, axis=1)
        
        # Intensity (how extreme the emotions are)
        df['intensity'] = np.sqrt((df['valence'] - 0.5)**2 + (df['energy'] - 0.5)**2)
        
        return df
    
    def get_mood_summary(self, df: pd.DataFrame) -> Dict:
        """Generate mood summary statistics"""
        # Calculate emotional range (std deviation of mood scores)
        emotional_range = df['mood_score'].std() if len(df) > 1 else 0.0
        
        # Estimate total duration (assuming average 3.5 minutes per track)
        avg_track_duration_minutes = 3.5
        total_duration_hours = (len(df) * avg_track_duration_minutes) / 60.0
        
        return {
            'total_tracks': len(df),
            'mood_score': df['mood_score'].mean(),  # Fixed: changed from avg_mood_score
            'avg_mood_score': df['mood_score'].mean(),
            'energy_level': df['energy'].mean(),  # Fixed: changed from avg_energy
            'avg_energy': df['energy'].mean(),
            'valence': df['valence'].mean(),  # Fixed: changed from avg_valence
            'avg_valence': df['valence'].mean(),
            'avg_danceability': df['danceability'].mean(),
            'dominant_mood': df['mood_category'].mode().iloc[0] if not df['mood_category'].mode().empty else 'Unknown',  # Fixed: changed from most_common_mood
            'most_common_mood': df['mood_category'].mode().iloc[0] if not df['mood_category'].mode().empty else 'Unknown',
            'mood_distribution': df['mood_category'].value_counts().to_dict(),
            'avg_popularity': df['popularity'].mean(),
            'emotional_range': emotional_range,
            'total_duration_hours': total_duration_hours,
            'using_estimates': 'energy' in df.columns and df['energy'].std() < 0.3  # Low std suggests estimates
        }

if __name__ == "__main__":
    # Test the fallback analyzer with metadata-based analysis
    import pandas as pd
    
    analyzer = FallbackSpotifyAnalyzer(use_user_auth=False)
    
    # Create a test DataFrame with sample track data
    sample_tracks = [
        {
            'name': 'Teri Yaad',
            'artist': 'Goldy Desi Crew',
            'album': 'Teri Yaad',
            'popularity': 75,
            'release_date': '2023-01-15',
            'artist_genres': ['punjabi pop', 'indian pop'],
            'duration_ms': 180000
        },
        {
            'name': 'Blinding Lights',
            'artist': 'The Weeknd',
            'album': 'After Hours',
            'popularity': 90,
            'release_date': '2019-11-29',
            'artist_genres': ['pop', 'synth-pop'],
            'duration_ms': 200040
        },
        {
            'name': 'Someone Like You',
            'artist': 'Adele',
            'album': '21',
            'popularity': 85,
            'release_date': '2011-01-24',
            'artist_genres': ['pop', 'soul'],
            'duration_ms': 285000
        }
    ]
    
    print("\n🧪 Testing metadata-based mood analysis...")
    
    try:
        # Test metadata analysis
        analyzed_df = analyzer.estimate_mood_from_metadata(sample_tracks)
        summary = analyzer.get_mood_summary(analyzed_df)
        
        print("\n🎉 SUCCESS! Metadata analysis completed!")
        print(f"📊 Summary:")
        print(f"   Tracks: {summary['total_tracks']}")
        print(f"   Avg Mood Score: {summary.get('mood_score', 'N/A'):.2f}")
        print(f"   Most Common Mood: {summary['most_common_mood']}")
        print(f"   Using Estimates: {summary['using_estimates']}")
        
        print(f"\n📈 Track Details:")
        for _, track in analyzed_df.iterrows():
            print(f"   • {track['name']} by {track['artist']}: {track['mood_category']} (score: {track['mood_score']:.2f})")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
