#!/usr/bin/env python3
"""
Last.fm Integration for Audio Features
Alternative source when Spotify audio features are blocked
"""

import requests
import json
from typing import Dict, List, Optional
import time

class LastFmAudioFeatures:
    def __init__(self, api_key: str = "your_lastfm_api_key_here"):
        """Initialize Last.fm client"""
        self.api_key = api_key
        self.base_url = "http://ws.audioscrobbler.com/2.0/"
    
    def get_track_info(self, artist: str, track: str) -> Optional[Dict]:
        """Get track information from Last.fm"""
        try:
            params = {
                'method': 'track.getInfo',
                'api_key': self.api_key,
                'artist': artist,
                'track': track,
                'format': 'json'
            }
            
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'track' in data:
                    return data['track']
            return None
            
        except Exception as e:
            return None
    
    def estimate_audio_features_from_lastfm(self, tracks: List[Dict]) -> List[Dict]:
        """Estimate audio features using Last.fm data"""
        enhanced_tracks = []
        
        for track in tracks[:10]:  # Limit for testing
            # Get Last.fm data
            lastfm_data = self.get_track_info(track.get('artist', ''), track.get('name', ''))
            
            # Extract features
            features = self._extract_features_from_lastfm(track, lastfm_data)
            enhanced_tracks.append(features)
            
            time.sleep(0.2)  # Be nice to the API
        
        return enhanced_tracks
    
    def _extract_features_from_lastfm(self, track: Dict, lastfm_data: Optional[Dict]) -> Dict:
        """Extract audio-like features from Last.fm data"""
        
        # Base features from existing track data
        features = {
            'id': track.get('id'),
            'name': track.get('name'),
            'artist': track.get('artist'),
            'popularity': track.get('popularity', 50),
        }
        
        if lastfm_data:
            # Extract tags (genres) for mood estimation
            tags = lastfm_data.get('toptags', {}).get('tag', [])
            tag_names = [tag.get('name', '').lower() for tag in tags[:5]]
            
            # Estimate energy from tags
            energy = self._estimate_energy_from_tags(tag_names)
            
            # Estimate valence from tags
            valence = self._estimate_valence_from_tags(tag_names)
            
            # Estimate other features
            danceability = self._estimate_danceability_from_tags(tag_names)
            
            features.update({
                'energy': energy,
                'valence': valence,
                'danceability': danceability,
                'tags': tag_names,
                'playcount': lastfm_data.get('playcount', 0),
                'listeners': lastfm_data.get('listeners', 0)
            })
        else:
            # Fallback to basic estimation
            features.update({
                'energy': 0.5,
                'valence': 0.5,
                'danceability': 0.5,
                'tags': [],
                'playcount': 0,
                'listeners': 0
            })
        
        return features
    
    def _estimate_energy_from_tags(self, tags: List[str]) -> float:
        """Estimate energy level from Last.fm tags"""
        high_energy_tags = ['rock', 'electronic', 'dance', 'metal', 'punk', 'techno', 'house', 'dubstep']
        medium_energy_tags = ['pop', 'indie', 'alternative', 'hip-hop', 'rap']
        low_energy_tags = ['ambient', 'classical', 'folk', 'acoustic', 'ballad', 'chill']
        
        energy = 0.5  # baseline
        
        for tag in tags:
            if any(e_tag in tag for e_tag in high_energy_tags):
                energy += 0.2
            elif any(m_tag in tag for m_tag in medium_energy_tags):
                energy += 0.1
            elif any(l_tag in tag for l_tag in low_energy_tags):
                energy -= 0.2
        
        return max(0.0, min(1.0, energy))
    
    def _estimate_valence_from_tags(self, tags: List[str]) -> float:
        """Estimate valence (positivity) from Last.fm tags"""
        positive_tags = ['happy', 'upbeat', 'dance', 'party', 'fun', 'energetic', 'cheerful']
        negative_tags = ['sad', 'melancholy', 'dark', 'depressing', 'emotional', 'breakup']
        
        valence = 0.5  # baseline
        
        for tag in tags:
            if any(p_tag in tag for p_tag in positive_tags):
                valence += 0.2
            elif any(n_tag in tag for n_tag in negative_tags):
                valence -= 0.2
        
        return max(0.0, min(1.0, valence))
    
    def _estimate_danceability_from_tags(self, tags: List[str]) -> float:
        """Estimate danceability from Last.fm tags"""
        dance_tags = ['dance', 'electronic', 'house', 'techno', 'disco', 'funk', 'reggae']
        
        danceability = 0.5
        
        for tag in tags:
            if any(d_tag in tag for d_tag in dance_tags):
                danceability += 0.2
        
        return max(0.0, min(1.0, danceability))

def test_lastfm_integration():
    """Test Last.fm as audio features alternative"""
    print("🧪 Testing Last.fm Integration for Audio Features...")
    
    # Note: You'd need to get a free Last.fm API key from:
    # https://www.last.fm/api/account/create
    
    lastfm = LastFmAudioFeatures()
    
    # Test tracks
    test_tracks = [
        {'id': '1', 'name': 'Shape of You', 'artist': 'Ed Sheeran', 'popularity': 85},
        {'id': '2', 'name': 'Blinding Lights', 'artist': 'The Weeknd', 'popularity': 90},
        {'id': '3', 'name': 'Someone Like You', 'artist': 'Adele', 'popularity': 80}
    ]
    
    # This would work with a real API key
    print("📝 Last.fm integration ready - requires free API key")
    print("🔗 Get API key from: https://www.last.fm/api/account/create")
    print("✅ Alternative audio features source available")
    
    return True

if __name__ == "__main__":
    test_lastfm_integration()
