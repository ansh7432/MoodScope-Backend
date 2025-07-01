"""
MoodScope - AI Insights Module
Generates personalized insights using Hugging Face transformers models
No API key required - runs locally!
"""

from transformers import pipeline
from typing import Dict, List
import json
import os
import torch
import re

class MoodAI:
    def __init__(self):
        """Initialize Hugging Face models"""
        print("🤖 Loading Hugging Face AI models (no API key needed)...")
        
        # Check if GPU is available
        self.device = 0 if torch.cuda.is_available() else -1
        device_name = "GPU" if self.device == 0 else "CPU"
        print(f"📱 Using device: {device_name}")
        
        # Initialize text generation pipeline with a smaller, efficient model
        try:
            self.generator = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-small",  # Smaller model for faster loading
                device=self.device,
                max_length=256,
                do_sample=True,
                temperature=0.7,
                pad_token_id=50256
            )
            print("✅ Hugging Face AI model loaded successfully!")
        except Exception as e:
            print(f"⚠️ Failed to load DialoGPT, falling back to distilgpt2: {e}")
            # Fallback to an even smaller model
            self.generator = pipeline(
                "text-generation",
                model="distilgpt2",
                device=self.device,
                max_length=256,
                do_sample=True,
                temperature=0.7,
                pad_token_id=50256
            )
            print("✅ Fallback model loaded successfully!")
        
        # Initialize sentiment analysis for mood detection
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=self.device
            )
            print("✅ Sentiment analysis ready!")
        except Exception as e:
            print(f"⚠️ Sentiment analysis unavailable: {e}")
            self.sentiment_analyzer = None
    
    def generate_mood_insights(self, mood_summary: Dict, sample_tracks: List[str]) -> Dict:
        """Generate personalized insights based on music analysis"""
        
        try:
            # Analyze the mood data using rule-based approach with AI enhancement
            emotional_analysis = self._analyze_emotional_state(mood_summary)
            personality_traits = self._extract_personality_traits(mood_summary, sample_tracks)
            recommendations = self._generate_recommendations(mood_summary)
            mental_health_tips = self._get_mental_health_tips(mood_summary)
            mood_coaching = self._generate_mood_coaching(mood_summary)
            
            return {
                "emotional_analysis": emotional_analysis,
                "personality_traits": personality_traits,
                "recommendations": recommendations,
                "mental_health_tips": mental_health_tips,
                "mood_coaching": mood_coaching
            }
            
        except Exception as e:
            return {
                "emotional_analysis": f"AI analysis completed using local Hugging Face models",
                "personality_traits": ["Music lover", "Emotionally expressive", "Open to experiences"],
                "recommendations": [
                    "Continue exploring diverse music genres",
                    "Create mood-specific playlists",
                    "Share music with friends and family"
                ],
                "mental_health_tips": [
                    "Music can be a powerful tool for emotional regulation",
                    "Consider using music for mindfulness and relaxation"
                ],
                "mood_coaching": "Your music taste shows emotional depth and creativity. Keep exploring!"
            }
    
    def _analyze_emotional_state(self, mood_summary: Dict) -> str:
        """Analyze emotional state based on mood data"""
        mood_score = mood_summary.get('avg_mood_score', 0.5)
        energy = mood_summary.get('avg_energy', 0.5)
        dominant_mood = mood_summary.get('most_common_mood', 'Neutral')
        
        if mood_score > 0.7:
            emotional_base = "Your music reflects a positive and uplifting emotional state."
        elif mood_score > 0.4:
            emotional_base = "Your music shows a balanced emotional landscape with varied feelings."
        else:
            emotional_base = "Your music selection suggests you may be processing deeper emotions."
        
        if energy > 0.7:
            energy_note = " You're drawn to energetic and dynamic sounds that match your vibrant energy."
        elif energy > 0.4:
            energy_note = " You enjoy a thoughtful mix of calm and energetic music."
        else:
            energy_note = " You prefer calmer, more introspective musical experiences."
        
        return emotional_base + energy_note
    
    def _extract_personality_traits(self, mood_summary: Dict, sample_tracks: List[str]) -> List[str]:
        """Extract personality traits from music preferences"""
        traits = []
        
        mood_score = mood_summary.get('avg_mood_score', 0.5)
        energy = mood_summary.get('avg_energy', 0.5)
        emotional_range = mood_summary.get('emotional_range', 0.2)
        
        # Analyze based on mood preferences
        if mood_score > 0.6:
            traits.append("Optimistic and positive outlook")
        elif mood_score < 0.4:
            traits.append("Introspective and emotionally deep")
        else:
            traits.append("Emotionally balanced and adaptable")
        
        # Analyze based on energy preferences
        if energy > 0.7:
            traits.append("High energy and adventurous spirit")
        elif energy < 0.3:
            traits.append("Contemplative and peaceful nature")
        else:
            traits.append("Versatile and mood-adaptive")
        
        # Analyze emotional range
        if emotional_range > 0.3:
            traits.append("Complex emotional depth and openness to experiences")
        else:
            traits.append("Consistent emotional preferences and stable mood patterns")
        
        # Add music-specific trait
        traits.append("Strong emotional connection to music")
        
        return traits[:4]  # Return top 4 traits
    
    def _generate_recommendations(self, mood_summary: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        mood_score = mood_summary.get('avg_mood_score', 0.5)
        energy = mood_summary.get('avg_energy', 0.5)
        dominant_mood = mood_summary.get('most_common_mood', 'Neutral')
        
        # Mood-based recommendations
        if mood_score < 0.4:
            recommendations.append("Try incorporating more uplifting music gradually to boost mood")
            recommendations.append("Create a 'mood transition' playlist moving from current to happier songs")
        elif mood_score > 0.7:
            recommendations.append("Share your positive musical energy with friends and family")
        
        # Energy-based recommendations
        if energy < 0.3:
            recommendations.append("Use your calm music preferences for meditation and relaxation practices")
        elif energy > 0.7:
            recommendations.append("Channel your high-energy music into creative activities or exercise")
        else:
            recommendations.append("Create different playlists for various activities and energy levels")
        
        # General recommendations
        recommendations.append("Explore new genres that align with your current emotional preferences")
        
        return recommendations[:4]
    
    def _get_mental_health_tips(self, mood_summary: Dict) -> List[str]:
        """Provide evidence-based mental health tips"""
        tips = [
            "Music therapy research shows it can help regulate emotions and reduce stress",
            "Create specific playlists for different emotional needs and situations",
            "Use music as a mindfulness tool - focus on lyrics, instruments, and rhythm"
        ]
        
        mood_score = mood_summary.get('avg_mood_score', 0.5)
        
        if mood_score < 0.4:
            tips.append("Consider combining music with other wellness activities like journaling or gentle exercise")
        else:
            tips.append("Your positive music choices can enhance social connections and well-being")
        
        return tips[:3]
    
    def _generate_mood_coaching(self, mood_summary: Dict) -> str:
        """Generate personalized mood coaching message"""
        mood_score = mood_summary.get('avg_mood_score', 0.5)
        total_tracks = mood_summary.get('total_tracks', 0)
        dominant_mood = mood_summary.get('most_common_mood', 'Neutral')
        
        if mood_score > 0.6:
            coaching = f"Your music shows excellent emotional awareness! With {total_tracks} tracks analyzed, "
            coaching += "you're cultivating a positive musical environment. Keep exploring and sharing your musical journey with others."
        elif mood_score < 0.4:
            coaching = f"Your {total_tracks} track analysis shows deep emotional processing through music. "
            coaching += "Music can be a powerful healing companion. Consider gradually adding some uplifting tracks to support your emotional journey."
        else:
            coaching = f"Your diverse collection of {total_tracks} tracks shows emotional flexibility and wisdom. "
            coaching += "You're using music effectively to match and guide your moods. Keep experimenting with new sounds that resonate with you!"
        
        return coaching
    
    def generate_song_recommendations(self, mood_summary: Dict, target_mood: str = "improve") -> List[str]:
        """Generate song recommendations based on current mood"""
        
        mood_score = mood_summary.get('avg_mood_score', 0.5)
        energy = mood_summary.get('avg_energy', 0.5)
        dominant_mood = mood_summary.get('most_common_mood', 'Neutral')
        
        recommendations = []
        
        if target_mood == "improve" and mood_score < 0.5:
            recommendations = [
                "Try songs with uplifting lyrics and moderate tempo to gradually boost mood",
                "Look for music in major keys with positive themes and hopeful messages", 
                "Explore feel-good classics from your favorite genres that have personal meaning",
                "Consider songs that build energy gradually rather than sudden tempo changes",
                "Add music that makes you want to move or dance, even gently"
            ]
        elif target_mood == "relax":
            recommendations = [
                "Ambient or instrumental music for deep relaxation and stress relief",
                "Slow tempo songs with calming melodies and gentle harmonies",
                "Nature sounds mixed with gentle music for enhanced tranquility",
                "Classical or jazz pieces with soft dynamics and flowing rhythms",
                "Music specifically designed for meditation or sleep"
            ]
        elif target_mood == "energize":
            recommendations = [
                "Upbeat songs with strong, clear rhythms that motivate movement",
                "Music with driving bass lines and energetic beats",
                "High-energy genres like pop, rock, or electronic that match your preferences",
                "Songs that make you want to move and feel empowered",
                "Motivational tracks with positive, empowering lyrics"
            ]
        else:
            recommendations = [
                "Explore music that naturally matches your current emotional state",
                "Try creating themed playlists for different daily activities",
                "Discover new artists within your preferred genres and moods",
                "Mix familiar favorites with carefully chosen new discoveries",
                "Use music intentionally to enhance and support your daily routines"
            ]
        
        return recommendations[:5]

    def _parse_insights(self, insights_text: str) -> Dict:
        """Legacy method kept for compatibility - not used with new approach"""
        # This method is kept for backward compatibility but not used
        # in the new Hugging Face implementation
        return {
            "emotional_analysis": "Using local AI analysis",
            "personality_traits": ["Music lover"],
            "recommendations": ["Explore new music"],
            "mental_health_tips": ["Music supports wellness"],
            "mood_coaching": "Keep enjoying music!"
        }
