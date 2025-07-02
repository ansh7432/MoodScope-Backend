"""
Hugging Face AI Insights Generator - Online API
Provides detailed psychological insights using Hugging Face sentiment analysis
"""

import requests
from typing import Dict, List
import random
import json
import os
from dotenv import load_dotenv

load_dotenv()

class HuggingFaceAI:
    def __init__(self):
        """Initialize Hugging Face AI with API token"""
        self.api_token = os.getenv('HUGGINGFACE_API_TOKEN', 'your_token_here')
        self.api_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
    
    def _call_huggingface_api(self, text: str) -> Dict:
        """Call Hugging Face sentiment analysis API"""
        try:
            payload = {"inputs": text}
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                    # Parse sentiment scores - LABEL_0=negative, LABEL_1=neutral, LABEL_2=positive
                    sentiments = result[0]
                    sentiment_map = {"positive": 0.33, "negative": 0.33, "neutral": 0.33}
                    
                    for sentiment in sentiments:
                        label = sentiment.get('label', '')
                        score = sentiment.get('score', 0)
                        
                        if label == 'LABEL_0':  # Negative
                            sentiment_map['negative'] = score
                        elif label == 'LABEL_1':  # Neutral
                            sentiment_map['neutral'] = score
                        elif label == 'LABEL_2':  # Positive
                            sentiment_map['positive'] = score
                    
                    return sentiment_map
                else:
                    print(f"⚠️ Unexpected API response format: {result}")
                    return {"positive": 0.5, "negative": 0.25, "neutral": 0.25}
            else:
                print(f"⚠️ Hugging Face API error {response.status_code}: {response.text}")
                return {"positive": 0.5, "negative": 0.25, "neutral": 0.25}
                
        except Exception as e:
            print(f"⚠️ Hugging Face API call failed: {e}")
            return {"positive": 0.5, "negative": 0.25, "neutral": 0.25}
    
    def generate_mood_insights(self, mood_summary: Dict, sample_tracks: List[str]) -> Dict:
        """Generate comprehensive insights from mood analysis data using AI"""
        
        mood_score = mood_summary.get('avg_mood_score', mood_summary.get('mood_score', 0.5))
        energy = mood_summary.get('avg_energy', 0.5)
        valence = mood_summary.get('avg_valence', 0.5)
        dominant_mood = mood_summary.get('most_common_mood', mood_summary.get('dominant_mood', 'Mixed'))
        emotional_range = mood_summary.get('emotional_range', 0.2)
        total_tracks = mood_summary.get('total_tracks', len(sample_tracks) if sample_tracks else 10)
        
        # Create a text description for AI analysis
        music_context = self._create_music_context(mood_score, energy, valence, dominant_mood, total_tracks, sample_tracks)
        
        # Get AI sentiment analysis
        sentiment_analysis = self._call_huggingface_api(music_context)
        
        # Generate insights based on AI analysis and music data
        emotional_analysis = self._analyze_emotional_state_with_ai(
            mood_score, energy, valence, dominant_mood, sentiment_analysis
        )
        
        personality_traits = self._identify_personality_traits_with_ai(
            mood_score, energy, valence, emotional_range, sentiment_analysis
        )
        
        recommendations = self._create_recommendations_with_ai(
            mood_score, energy, valence, dominant_mood, sentiment_analysis
        )
        
        mood_coaching = self._create_mood_coaching_with_ai(
            mood_score, energy, valence, dominant_mood, total_tracks, sentiment_analysis
        )
        
        return {
            'emotional_analysis': emotional_analysis,
            'personality_traits': personality_traits,
            'recommendations': recommendations,
            'mood_coaching': mood_coaching
        }
    
    def _create_music_context(self, mood_score, energy, valence, dominant_mood, total_tracks, sample_tracks):
        """Create a text context for AI analysis"""
        track_names = []
        if sample_tracks:
            for track in sample_tracks[:5]:  # Use first 5 tracks
                if isinstance(track, dict):
                    name = track.get('name', 'Unknown')
                    artist = track.get('artist', 'Unknown Artist')
                    track_names.append(f"{name} by {artist}")
                else:
                    track_names.append(str(track))
        
        tracks_text = ", ".join(track_names) if track_names else "various songs"
        
        energy_desc = "high-energy" if energy > 0.6 else "moderate-energy" if energy > 0.3 else "low-energy"
        valence_desc = "uplifting" if valence > 0.6 else "neutral" if valence > 0.3 else "melancholic"
        
        context = f"A music listener has chosen a playlist of {total_tracks} {energy_desc}, {valence_desc} songs including {tracks_text}. The dominant mood is {dominant_mood} with an overall mood score of {mood_score:.2f}. This music selection reflects their current emotional state and personality."
        
        return context
    
    def _analyze_emotional_state_with_ai(self, mood_score, energy, valence, dominant_mood, sentiment_analysis):
        """Analyze emotional state using AI sentiment and music data"""
        positive_score = sentiment_analysis.get('positive', 0.5)
        negative_score = sentiment_analysis.get('negative', 0.25)
        
        energy_desc = "high-energy" if energy > 0.6 else "moderate-energy" if energy > 0.3 else "low-energy"
        valence_desc = "uplifting" if valence > 0.6 else "neutral" if valence > 0.3 else "melancholic"
        
        if positive_score > 0.6 or mood_score > 0.7:
            return f"Your music reveals a vibrant emotional landscape! With a mood score of {mood_score:.2f}, you're gravitating toward {energy_desc}, {valence_desc} tracks. The dominance of '{dominant_mood}' music suggests you're in an emotionally expansive phase, using music to amplify and celebrate your inner vitality. AI analysis indicates strong positive sentiment ({positive_score:.2f}) in your music choices, showing emotional resilience and a positive approach to life's challenges."
        
        elif positive_score > 0.4 or mood_score > 0.4:
            return f"Your playlist shows emotional sophistication with a mood score of {mood_score:.2f}. The blend of {energy_desc} and {valence_desc} elements, centered around '{dominant_mood}' music, reveals someone who appreciates nuanced emotional experiences. AI sentiment analysis ({positive_score:.2f} positive, {negative_score:.2f} negative) suggests you're in a phase of emotional stability, using music to maintain balance rather than dramatically shift your mood."
        
        elif mood_score > 0.1:
            return f"Your music choices reflect deep emotional intelligence, with a mood score of {mood_score:.2f}. The prevalence of {energy_desc}, {valence_desc} tracks in the '{dominant_mood}' category suggests you're engaged in meaningful emotional processing. AI analysis shows balanced sentiment, indicating you're using music as a companion for introspection, showing healthy emotional awareness and self-care."
        
        else:
            return f"Your playlist indicates profound emotional depth with a mood score of {mood_score:.2f}. The {energy_desc}, {valence_desc} nature of your '{dominant_mood}' selections shows someone who isn't afraid to sit with complex emotions. AI sentiment analysis reveals introspective patterns, suggesting emotional courage and authenticity - you're allowing music to help you navigate and understand deeper feelings."
    
    def _identify_personality_traits_with_ai(self, mood_score, energy, valence, emotional_range, sentiment_analysis):
        """Identify personality traits using AI sentiment and music preferences"""
        positive_score = sentiment_analysis.get('positive', 0.5)
        traits = []
        
        # Energy-based traits enhanced with AI
        if energy > 0.75:
            if positive_score > 0.6:
                traits.extend([
                    "High energy and motivation-driven personality",
                    "Thrives in dynamic and stimulating environments", 
                    "Natural leader who energizes others"
                ])
            else:
                traits.extend([
                    "Intense and passionate personality",
                    "Channels energy into meaningful pursuits",
                    "Strong-willed and determined"
                ])
        elif energy > 0.5:
            traits.extend([
                "Well-balanced between active and contemplative states",
                "Adaptable to various social and work environments",
                "Demonstrates emotional flexibility"
            ])
        else:
            if positive_score > 0.5:
                traits.extend([
                    "Prefers calm and peaceful environments",
                    "Values depth and meaningful conversations",
                    "Strong capacity for concentration and reflection"
                ])
            else:
                traits.extend([
                    "Introspective and thoughtful nature",
                    "Comfortable with solitude and quiet moments",
                    "Deep thinker who processes emotions carefully"
                ])
        
        # Valence-based traits with AI enhancement
        if valence > 0.7:
            traits.extend([
                "Naturally optimistic with a positive outlook",
                "Brings uplifting energy to social situations",
                "Resilient in face of challenges"
            ])
        elif valence > 0.4:
            traits.extend([
                "Emotionally balanced and stable",
                "Realistic perspective on life's ups and downs",
                "Steady and reliable in relationships"
            ])
        else:
            if sentiment_analysis.get('negative', 0) < 0.7:  # Not overwhelmingly negative
                traits.extend([
                    "Deep emotional sensitivity",
                    "Values authenticity and genuine connections",
                    "Artist-like appreciation for emotional complexity"
                ])
            else:
                traits.extend([
                    "Currently processing deep emotions",
                    "Uses music for emotional healing",
                    "Strong capacity for empathy and understanding"
                ])
        
        # Emotional range insights
        if emotional_range > 0.5:
            traits.append("Embraces full spectrum of human emotions")
        
        return traits[:5]  # Return top 5 traits
    
    def _create_recommendations_with_ai(self, mood_score, energy, valence, dominant_mood, sentiment_analysis):
        """Create personalized recommendations using AI insights"""
        positive_score = sentiment_analysis.get('positive', 0.5)
        recommendations = []
        
        if positive_score > 0.6 and energy > 0.6:
            recommendations = [
                "Perfect for energizing workouts and morning routines",
                "Great soundtrack for social gatherings and celebrations",
                "Try exploring upbeat genres like pop, dance, or funk",
                "Consider creating workout or motivation playlists"
            ]
        elif positive_score > 0.4 and valence > 0.5:
            recommendations = [
                "Ideal for productive work sessions and focus time",
                "Great for background music during creative activities",
                "Explore indie, alternative, or feel-good classics",
                "Perfect for road trips and casual listening"
            ]
        elif energy < 0.4:
            recommendations = [
                "Perfect for relaxation and unwinding after busy days",
                "Great for meditation, reading, or quiet contemplation",
                "Try ambient, classical, or acoustic genres",
                "Consider evening wind-down or sleep playlists"
            ]
        else:
            recommendations = [
                "Excellent for emotional processing and self-reflection",
                "Great for journaling or creative expression",
                "Explore singer-songwriter, folk, or introspective genres",
                "Consider creating themed playlists for different moods"
            ]
        
        # Add AI-enhanced recommendation
        if dominant_mood and dominant_mood != "Mixed":
            recommendations.append(f"Your '{dominant_mood}' preference suggests exploring similar artists in this style")
        
        return recommendations[:4]  # Return top 4 recommendations
    
    def _create_mood_coaching_with_ai(self, mood_score, energy, valence, dominant_mood, total_tracks, sentiment_analysis):
        """Create mood coaching advice using AI sentiment analysis"""
        positive_score = sentiment_analysis.get('positive', 0.5)
        negative_score = sentiment_analysis.get('negative', 0.25)
        
        if positive_score > 0.6:
            return f"Your music choices show excellent emotional self-awareness! With {total_tracks} tracks reflecting positive sentiment, you're using music effectively to maintain and boost your mood. This indicates strong emotional regulation skills and a proactive approach to mental wellness. Keep using music as your emotional ally!"
        
        elif positive_score > 0.4:
            return f"You demonstrate balanced emotional intelligence through your {total_tracks}-track selection. AI analysis shows you appreciate both uplifting and contemplative music, indicating emotional maturity. You understand that different situations call for different moods - this is a sign of sophisticated emotional regulation."
        
        elif negative_score < 0.6:
            return f"Your playlist shows you're comfortable exploring the full range of human emotions. This emotional honesty is actually a strength - research shows that people who acknowledge difficult feelings tend to be more resilient. Your {total_tracks} songs suggest you use music for healthy emotional processing."
        
        else:
            return f"Music can be a powerful tool for emotional healing, and your {total_tracks}-track selection shows you're using it wisely for processing complex feelings. Consider gradually introducing some higher-valence tracks to support emotional balance. Remember, it's healthy to feel all emotions - you're showing courage in facing them through music."

# Maintain compatibility with existing code
LocalMoodAI = HuggingFaceAI
HuggingFaceMoodAI = HuggingFaceAI
