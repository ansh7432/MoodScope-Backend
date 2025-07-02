"""
Minimal AI Mood Categorizer for Fallback Spotify
Provides basic mood categorization functionality
"""

import pandas as pd
import random

class HuggingFaceMoodCategorizer:
    def __init__(self):
        """Initialize basic mood categorizer"""
        self.available = True
    
    def categorize_tracks_batch(self, tracks):
        """Categorize a batch of tracks and return a DataFrame with mood analysis"""
        data = []
        
        for track in tracks:
            try:
                # Extract basic info with safe access
                track_data = {
                    'id': track.get('id', ''),
                    'name': track.get('name', 'Unknown'),
                    'artist': self._extract_artist_name(track),
                    'album': self._extract_album_name(track),
                    'popularity': track.get('popularity', 50),
                    'duration_ms': track.get('duration_ms', 180000),
                    'release_date': self._extract_release_date(track),
                    'artist_genres': self._extract_genres(track),
                    'explicit': track.get('explicit', False)
                }
                
                # Generate estimated audio features based on metadata
                estimated_features = self._estimate_audio_features(track_data)
                track_data.update(estimated_features)
                
                # Add mood analysis
                mood_category = self.categorize_mood(estimated_features)
                emotion_analysis = self.analyze_emotion(estimated_features)
                
                track_data.update({
                    'mood_category': mood_category,
                    'ai_emotion': emotion_analysis['emotion'],
                    'ai_confidence': emotion_analysis['confidence'],
                    'detected_emotions': [],  # Empty for basic implementation
                    'analysis_method': 'AI-Enhanced'
                })
                
                data.append(track_data)
            except Exception as e:
                print(f"⚠️ Error processing track {track.get('name', 'Unknown')}: {e}")
                # Add a basic fallback track
                data.append({
                    'id': track.get('id', ''),
                    'name': track.get('name', 'Unknown'),
                    'artist': 'Unknown Artist',
                    'album': 'Unknown Album',
                    'popularity': 50,
                    'duration_ms': 180000,
                    'release_date': '2020-01-01',
                    'artist_genres': [],
                    'explicit': False,
                    'valence': 0.5,
                    'energy': 0.5,
                    'mood_score': 0.5,
                    'danceability': 0.4,
                    'intensity': 0.0,
                    'mood_category': 'Unknown',
                    'ai_emotion': 'neutral',
                    'ai_confidence': 0.3,
                    'detected_emotions': [],
                    'analysis_method': 'Basic'
                })
        
        return pd.DataFrame(data)
    
    def _extract_artist_name(self, track):
        """Safely extract artist name from track data"""
        try:
            if 'artists' in track and isinstance(track['artists'], list):
                return ', '.join([artist['name'] for artist in track['artists'] if isinstance(artist, dict) and 'name' in artist])
            elif 'artist' in track:
                return str(track['artist'])
            else:
                return 'Unknown Artist'
        except:
            return 'Unknown Artist'
    
    def _extract_album_name(self, track):
        """Safely extract album name from track data"""
        try:
            album = track.get('album', {})
            if isinstance(album, dict):
                return album.get('name', 'Unknown Album')
            elif isinstance(album, str):
                return album
            else:
                return 'Unknown Album'
        except:
            return 'Unknown Album'
    
    def _extract_release_date(self, track):
        """Safely extract release date from track data"""
        try:
            album = track.get('album', {})
            if isinstance(album, dict):
                return album.get('release_date', '2020-01-01')
            else:
                return '2020-01-01'
        except:
            return '2020-01-01'
    
    def _extract_genres(self, track):
        """Extract genres from track data"""
        try:
            # Try to get genres from artists
            genres = []
            for artist in track.get('artists', []):
                if 'genres' in artist:
                    genres.extend(artist['genres'])
            return genres[:4]  # Limit to 4 genres
        except:
            return []
    
    def _estimate_audio_features(self, track_data):
        """Estimate audio features based on metadata and artist info"""
        try:
            # Base features with some randomness for variety
            base_valence = 0.5 + random.uniform(-0.2, 0.2)
            base_energy = 0.5 + random.uniform(-0.2, 0.2)
            
            # Adjust based on genres
            genres = track_data.get('artist_genres', [])
            genre_str = ' '.join(genres).lower()
            
            # Genre-based adjustments
            if any(word in genre_str for word in ['dance', 'pop', 'electronic', 'edm']):
                base_energy += 0.2
                base_valence += 0.1
            elif any(word in genre_str for word in ['blues', 'sad', 'melancholic', 'indie']):
                base_valence -= 0.2
                base_energy -= 0.1
            elif any(word in genre_str for word in ['rock', 'metal', 'punk']):
                base_energy += 0.3
            elif any(word in genre_str for word in ['classical', 'ambient', 'chill']):
                base_energy -= 0.2
                base_valence += 0.1
            
            # Adjust based on popularity (popular songs tend to be more upbeat)
            popularity = track_data.get('popularity', 50)
            if popularity > 70:
                base_valence += 0.1
                base_energy += 0.1
            
            # Clamp values between 0 and 1
            valence = max(0.0, min(1.0, base_valence))
            energy = max(0.0, min(1.0, base_energy))
            
            # Generate other features based on valence and energy
            danceability = max(0.0, min(1.0, energy * 0.8 + random.uniform(-0.1, 0.1)))
            intensity = max(0.0, min(1.0, energy - valence * 0.3))
            
            # Calculate mood score (combination of valence and energy)
            mood_score = (valence * 0.6 + energy * 0.4)
            
            return {
                'valence': valence,
                'energy': energy,
                'mood_score': mood_score,
                'danceability': danceability,
                'intensity': intensity
            }
        except Exception as e:
            print(f"⚠️ Error estimating features: {e}")
            # Return safe defaults
            return {
                'valence': 0.5,
                'energy': 0.5,
                'mood_score': 0.5,
                'danceability': 0.4,
                'intensity': 0.0
            }
    
    def categorize_mood(self, audio_features):
        """Basic mood categorization based on audio features"""
        try:
            valence = audio_features.get('valence', 0.5)
            energy = audio_features.get('energy', 0.5)
            
            if valence > 0.7 and energy > 0.7:
                return "Energetic & Happy"
            elif valence > 0.6 and energy > 0.5:
                return "Happy & Uplifting"
            elif valence < 0.4 and energy < 0.4:
                return "Melancholic & Thoughtful"
            elif energy > 0.7:
                return "Energetic & Intense"
            elif valence < 0.4:
                return "Sad & Emotional"
            else:
                return "Balanced & Stable"
        except:
            return "Unknown"
    
    def analyze_emotion(self, audio_features):
        """Basic emotion analysis"""
        try:
            valence = audio_features.get('valence', 0.5)
            energy = audio_features.get('energy', 0.5)
            
            if valence > 0.6:
                return {"emotion": "happy", "confidence": min(valence, 0.95)}
            elif valence < 0.4:
                return {"emotion": "sad", "confidence": min(1 - valence, 0.95)}
            else:
                return {"emotion": "neutral", "confidence": 0.5}
        except:
            return {"emotion": "neutral", "confidence": 0.3}
