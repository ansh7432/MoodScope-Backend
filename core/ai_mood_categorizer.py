"""
MoodScope - AI-Powered Mood Categorization
Uses Hugging Face models for accurate music mood analysis
"""

from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import pandas as pd
import numpy as np
import torch
import re
from typing import Dict, List, Tuple
import json

class HuggingFaceMoodCategorizer:
    def __init__(self):
        """Initialize Hugging Face models for mood analysis"""
        print("🤖 Loading AI mood categorization models...")
        
        self.device = 0 if torch.cuda.is_available() else -1
        
        # Emotion classification model
        try:
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=self.device,
                truncation=True,
                max_length=512
            )
            print("✅ Emotion classifier loaded!")
        except Exception as e:
            print(f"⚠️ Using fallback emotion model: {e}")
            self.emotion_classifier = pipeline(
                "text-classification", 
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=self.device
            )
        
        # Sentiment analysis for deeper understanding
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=self.device
            )
            print("✅ Sentiment analyzer loaded!")
        except Exception as e:
            print(f"⚠️ Sentiment analysis unavailable: {e}")
            self.sentiment_analyzer = None
        
        # Music genre mood associations (based on music psychology research)
        self.genre_moods = {
            # High Energy & Positive
            'pop': {'valence': 0.7, 'energy': 0.7, 'emotions': ['joy', 'optimism']},
            'dance': {'valence': 0.8, 'energy': 0.9, 'emotions': ['joy', 'excitement']},
            'electronic': {'valence': 0.6, 'energy': 0.8, 'emotions': ['excitement', 'anticipation']},
            'hip hop': {'valence': 0.6, 'energy': 0.8, 'emotions': ['confidence', 'excitement']},
            'disco': {'valence': 0.8, 'energy': 0.8, 'emotions': ['joy', 'nostalgia']},
            
            # Medium Energy & Positive  
            'indie': {'valence': 0.6, 'energy': 0.5, 'emotions': ['contentment', 'introspection']},
            'alternative': {'valence': 0.5, 'energy': 0.6, 'emotions': ['contemplation', 'authenticity']},
            'folk': {'valence': 0.6, 'energy': 0.4, 'emotions': ['nostalgia', 'warmth']},
            'country': {'valence': 0.6, 'energy': 0.5, 'emotions': ['nostalgia', 'storytelling']},
            
            # High Energy & Variable Mood
            'rock': {'valence': 0.5, 'energy': 0.8, 'emotions': ['power', 'rebellion']},
            'metal': {'valence': 0.4, 'energy': 0.9, 'emotions': ['intensity', 'release']},
            'punk': {'valence': 0.4, 'energy': 0.9, 'emotions': ['anger', 'rebellion']},
            
            # Low Energy & Emotional
            'blues': {'valence': 0.3, 'energy': 0.4, 'emotions': ['melancholy', 'catharsis']},
            'classical': {'valence': 0.5, 'energy': 0.3, 'emotions': ['contemplation', 'transcendence']},
            'ambient': {'valence': 0.5, 'energy': 0.2, 'emotions': ['peace', 'meditation']},
            'sad': {'valence': 0.2, 'energy': 0.3, 'emotions': ['sadness', 'reflection']},
            
            # Cultural & Specific
            'jazz': {'valence': 0.6, 'energy': 0.5, 'emotions': ['sophistication', 'improvisation']},
            'reggae': {'valence': 0.7, 'energy': 0.4, 'emotions': ['peace', 'unity']},
            'latin': {'valence': 0.7, 'energy': 0.7, 'emotions': ['passion', 'celebration']},
            'world': {'valence': 0.6, 'energy': 0.5, 'emotions': ['cultural', 'exploration']}
        }
        
        # Emotional keywords for song analysis
        self.emotion_keywords = {
            'joy': ['happy', 'joy', 'smile', 'laugh', 'bright', 'sunshine', 'celebrate', 'party', 'fun', 'dance'],
            'love': ['love', 'heart', 'romance', 'kiss', 'together', 'forever', 'beloved', 'darling', 'honey'],
            'sadness': ['sad', 'cry', 'tear', 'lonely', 'miss', 'lost', 'broken', 'hurt', 'pain', 'goodbye'],
            'anger': ['angry', 'hate', 'mad', 'rage', 'fight', 'war', 'destroy', 'revenge', 'fury'],
            'fear': ['afraid', 'scared', 'worry', 'anxiety', 'panic', 'terror', 'nightmare', 'danger'],
            'hope': ['hope', 'dream', 'future', 'tomorrow', 'believe', 'faith', 'trust', 'optimism'],
            'nostalgia': ['memory', 'remember', 'past', 'yesterday', 'childhood', 'home', 'mother', 'father'],
            'energy': ['power', 'strong', 'fast', 'run', 'jump', 'alive', 'electric', 'fire', 'energy']
        }
    
    def analyze_track_mood(self, track_info: Dict) -> Dict:
        """Analyze a single track's mood using AI"""
        
        # Extract text for analysis
        text_content = self._extract_text_content(track_info)
        
        # AI emotion analysis
        ai_emotions = self._analyze_emotions_ai(text_content)
        
        # Genre-based analysis
        genre_analysis = self._analyze_genre_mood(track_info.get('artist_genres', []))
        
        # Keyword-based analysis
        keyword_analysis = self._analyze_keywords(text_content)
        
        # Combine all analyses
        final_mood = self._combine_analyses(ai_emotions, genre_analysis, keyword_analysis, track_info)
        
        return final_mood
    
    def _extract_text_content(self, track_info: Dict) -> str:
        """Extract text content for analysis"""
        text_parts = []
        
        # Song title
        if 'name' in track_info:
            text_parts.append(track_info['name'])
        
        # Artist name  
        if 'artist' in track_info:
            text_parts.append(track_info['artist'])
        
        # Album name
        if 'album' in track_info:
            text_parts.append(track_info['album'])
        
        return " ".join(text_parts)
    
    def _analyze_emotions_ai(self, text: str) -> Dict:
        """Use AI to analyze emotions in song text"""
        if not text or not self.emotion_classifier:
            return {'emotion': 'neutral', 'confidence': 0.5}
        
        try:
            # Clean text
            text = re.sub(r'[^\w\s]', '', text.lower())
            if len(text) < 3:
                return {'emotion': 'neutral', 'confidence': 0.5}
            
            # Get emotion prediction
            result = self.emotion_classifier(text[:512])  # Limit text length
            
            if isinstance(result, list) and len(result) > 0:
                emotion = result[0]['label'].lower()
                confidence = result[0]['score']
                
                # Map emotions to our mood system
                emotion_mapping = {
                    'joy': 'happy',
                    'happiness': 'happy', 
                    'love': 'romantic',
                    'sadness': 'sad',
                    'anger': 'intense',
                    'fear': 'anxious',
                    'surprise': 'excited',
                    'disgust': 'negative',
                    'positive': 'happy',
                    'negative': 'sad',
                    'neutral': 'neutral'
                }
                
                mapped_emotion = emotion_mapping.get(emotion, 'neutral')
                
                return {
                    'emotion': mapped_emotion,
                    'confidence': confidence,
                    'original_emotion': emotion
                }
            
        except Exception as e:
            print(f"⚠️ AI emotion analysis failed: {e}")
        
        return {'emotion': 'neutral', 'confidence': 0.5}
    
    def _analyze_genre_mood(self, genres: List[str]) -> Dict:
        """Analyze mood based on music genres"""
        if not genres:
            return {'valence': 0.5, 'energy': 0.5, 'confidence': 0.3}
        
        # Find matching genres
        total_valence = 0
        total_energy = 0
        matches = 0
        
        for genre in genres:
            genre_lower = genre.lower()
            for known_genre, mood_data in self.genre_moods.items():
                if known_genre in genre_lower or any(word in genre_lower for word in known_genre.split()):
                    total_valence += mood_data['valence']
                    total_energy += mood_data['energy']
                    matches += 1
                    break
        
        if matches > 0:
            avg_valence = total_valence / matches
            avg_energy = total_energy / matches
            confidence = min(0.8, matches * 0.3)  # Higher confidence with more genre matches
        else:
            # Default for unknown genres
            avg_valence = 0.5
            avg_energy = 0.5
            confidence = 0.2
        
        return {
            'valence': avg_valence,
            'energy': avg_energy,
            'confidence': confidence
        }
    
    def _analyze_keywords(self, text: str) -> Dict:
        """Analyze emotional keywords in song text"""
        if not text:
            return {'emotions': [], 'valence': 0.5, 'energy': 0.5}
        
        text_lower = text.lower()
        found_emotions = {}
        
        # Count emotional keywords
        for emotion, keywords in self.emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                found_emotions[emotion] = count
        
        if not found_emotions:
            return {'emotions': [], 'valence': 0.5, 'energy': 0.5}
        
        # Calculate mood based on found emotions
        valence = 0.5
        energy = 0.5
        
        # Positive emotions increase valence
        positive_emotions = ['joy', 'love', 'hope']
        negative_emotions = ['sadness', 'anger', 'fear']
        energetic_emotions = ['joy', 'anger', 'energy']
        calm_emotions = ['love', 'sadness', 'nostalgia']
        
        total_weight = sum(found_emotions.values())
        
        for emotion, count in found_emotions.items():
            weight = count / total_weight
            
            if emotion in positive_emotions:
                valence += weight * 0.3
            elif emotion in negative_emotions:
                valence -= weight * 0.3
            
            if emotion in energetic_emotions:
                energy += weight * 0.3
            elif emotion in calm_emotions:
                energy -= weight * 0.2
        
        # Normalize
        valence = max(0.0, min(1.0, valence))
        energy = max(0.0, min(1.0, energy))
        
        return {
            'emotions': list(found_emotions.keys()),
            'valence': valence,
            'energy': energy
        }
    
    def _combine_analyses(self, ai_emotions: Dict, genre_analysis: Dict, keyword_analysis: Dict, track_info: Dict) -> Dict:
        """Combine all analyses into final mood assessment"""
        
        # Weight the different analyses based on confidence
        ai_weight = ai_emotions.get('confidence', 0.5)
        genre_weight = genre_analysis.get('confidence', 0.3)
        keyword_weight = 0.4 if keyword_analysis['emotions'] else 0.2
        
        # Normalize weights
        total_weight = ai_weight + genre_weight + keyword_weight
        if total_weight > 0:
            ai_weight /= total_weight
            genre_weight /= total_weight  
            keyword_weight /= total_weight
        else:
            ai_weight = genre_weight = keyword_weight = 0.33
        
        # Calculate weighted valence and energy
        valence = (
            genre_analysis['valence'] * genre_weight +
            keyword_analysis['valence'] * keyword_weight +
            self._emotion_to_valence(ai_emotions.get('emotion', 'neutral')) * ai_weight
        )
        
        energy = (
            genre_analysis['energy'] * genre_weight +
            keyword_analysis['energy'] * keyword_weight +
            self._emotion_to_energy(ai_emotions.get('emotion', 'neutral')) * ai_weight
        )
        
        # Ensure values are in valid range
        valence = max(0.0, min(1.0, valence))
        energy = max(0.0, min(1.0, energy))
        
        # Calculate mood score and category
        mood_score = valence * 0.6 + energy * 0.4
        mood_category = self._categorize_mood_advanced(valence, energy, ai_emotions.get('emotion', 'neutral'))
        
        return {
            'valence': valence,
            'energy': energy,
            'mood_score': mood_score,
            'mood_category': mood_category,
            'ai_emotion': ai_emotions.get('emotion', 'neutral'),
            'ai_confidence': ai_emotions.get('confidence', 0.5),
            'detected_emotions': keyword_analysis['emotions'],
            'analysis_method': 'AI-Enhanced'
        }
    
    def _emotion_to_valence(self, emotion: str) -> float:
        """Convert emotion to valence value"""
        emotion_valence = {
            'happy': 0.8,
            'romantic': 0.7,
            'excited': 0.8,
            'sad': 0.2,
            'intense': 0.4,
            'anxious': 0.3,
            'negative': 0.2,
            'neutral': 0.5
        }
        return emotion_valence.get(emotion, 0.5)
    
    def _emotion_to_energy(self, emotion: str) -> float:
        """Convert emotion to energy value"""
        emotion_energy = {
            'happy': 0.7,
            'romantic': 0.4,
            'excited': 0.9,
            'sad': 0.3,
            'intense': 0.8,
            'anxious': 0.6,
            'negative': 0.4,
            'neutral': 0.5
        }
        return emotion_energy.get(emotion, 0.5)
    
    def _categorize_mood_advanced(self, valence: float, energy: float, ai_emotion: str) -> str:
        """Advanced mood categorization with AI emotion context"""
        
        # Use AI emotion to refine categories
        if ai_emotion == 'romantic':
            return 'Romantic & Loving'
        elif ai_emotion == 'excited':
            return 'Excited & Energetic'
        elif ai_emotion == 'intense':
            return 'Intense & Powerful'
        elif ai_emotion == 'anxious':
            return 'Anxious & Uncertain'
        
        # Traditional categorization with more nuance
        if valence >= 0.7:
            if energy >= 0.7:
                return 'Happy & Energetic'
            elif energy >= 0.4:
                return 'Happy & Uplifting'
            else:
                return 'Happy & Calm'
        elif valence >= 0.5:
            if energy >= 0.7:
                return 'Energetic & Motivating'
            elif energy >= 0.4:
                return 'Balanced & Stable'
            else:
                return 'Calm & Peaceful'
        elif valence >= 0.3:
            if energy >= 0.7:
                return 'Intense & Brooding'
            elif energy >= 0.4:
                return 'Melancholic & Thoughtful'
            else:
                return 'Sad & Reflective'
        else:
            if energy >= 0.6:
                return 'Dark & Intense'
            else:
                return 'Sad & Despondent'
    
    def categorize_tracks_batch(self, tracks: List[Dict]) -> pd.DataFrame:
        """Categorize multiple tracks efficiently"""
        print(f"🎯 AI-analyzing mood for {len(tracks)} tracks...")
        
        results = []
        for i, track in enumerate(tracks):
            if i % 10 == 0:
                print(f"   Processing track {i+1}/{len(tracks)}...")
            
            mood_data = self.analyze_track_mood(track)
            
            # Combine original track data with mood analysis
            result = {**track, **mood_data}
            results.append(result)
        
        df = pd.DataFrame(results)
        print(f"✅ AI mood analysis complete! Enhanced {len(df)} tracks")
        
        return df

# For integration with existing code
def create_ai_mood_categorizer():
    """Factory function to create AI mood categorizer"""
    return HuggingFaceMoodCategorizer()
