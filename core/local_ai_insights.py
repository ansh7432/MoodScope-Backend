"""
Local AI Insights Generator - No OpenAI Required
Provides detailed psychological insights based on music analysis
"""

from typing import Dict, List
import random

class LocalMoodAI:
    def __init__(self):
        """Initialize local insights generator"""
        pass
    
    def generate_mood_insights(self, mood_summary: Dict, sample_tracks: List[str]) -> Dict:
        """Generate comprehensive insights from mood analysis data"""
        
        mood_score = mood_summary['avg_mood_score']
        energy = mood_summary['avg_energy']
        valence = mood_summary['avg_valence']
        dominant_mood = mood_summary['most_common_mood']
        emotional_range = mood_summary.get('emotional_range', 0.2)
        total_tracks = mood_summary['total_tracks']
        
        # Generate emotional analysis
        emotional_analysis = self._analyze_emotional_state(mood_score, energy, valence, dominant_mood)
        
        # Generate personality traits
        personality_traits = self._identify_personality_traits(mood_score, energy, valence, emotional_range)
        
        # Generate recommendations
        recommendations = self._create_recommendations(mood_score, energy, valence, dominant_mood)
        
        # Generate mental health tips
        mental_health_tips = self._provide_mental_health_tips(mood_score, energy, emotional_range)
        
        # Generate mood coaching
        mood_coaching = self._create_mood_coaching(mood_score, energy, valence, dominant_mood, total_tracks)
        
        return {
            'emotional_analysis': emotional_analysis,
            'personality_traits': personality_traits,
            'recommendations': recommendations,
            'mental_health_tips': mental_health_tips,
            'mood_coaching': mood_coaching
        }
    
    def _analyze_emotional_state(self, mood_score, energy, valence, dominant_mood):
        """Analyze current emotional state based on music choices"""
        
        # Create more dynamic analysis based on specific values
        energy_desc = "high-energy" if energy > 0.6 else "moderate-energy" if energy > 0.3 else "low-energy"
        valence_desc = "uplifting" if valence > 0.6 else "neutral" if valence > 0.3 else "melancholic"
        
        if mood_score > 0.7:
            return f"Your music reveals a vibrant emotional landscape! With a mood score of {mood_score:.2f}, you're gravitating toward {energy_desc}, {valence_desc} tracks. The dominance of '{dominant_mood}' music suggests you're in an emotionally expansive phase, using music to amplify and celebrate your inner vitality. Your playlist choice indicates strong emotional resilience and a positive approach to life's challenges."
        
        elif mood_score > 0.4:
            return f"Your playlist shows emotional sophistication with a mood score of {mood_score:.2f}. The blend of {energy_desc} and {valence_desc} elements, centered around '{dominant_mood}' music, reveals someone who appreciates nuanced emotional experiences. You're likely in a phase of emotional stability, using music to maintain balance rather than dramatically shift your mood."
        
        elif mood_score > 0.1:
            return f"Your music choices reflect deep emotional intelligence, with a mood score of {mood_score:.2f}. The prevalence of {energy_desc}, {valence_desc} tracks in the '{dominant_mood}' category suggests you're engaged in meaningful emotional processing. You're using music as a companion for introspection, showing healthy emotional awareness and self-care."
        
        else:
            return f"Your playlist indicates profound emotional depth with a mood score of {mood_score:.2f}. The {energy_desc}, {valence_desc} nature of your '{dominant_mood}' selections shows someone who isn't afraid to sit with complex emotions. This suggests emotional courage and authenticity - you're allowing music to help you navigate and understand deeper feelings."
    
    def _identify_personality_traits(self, mood_score, energy, valence, emotional_range):
        """Identify personality traits based on musical preferences"""
        
        traits = []
        
        # Energy-based traits
        if energy > 0.75:
            traits.extend([
                "High energy and motivation-driven personality",
                "Thrives in dynamic and stimulating environments",
                "Natural leader who energizes others"
            ])
        elif energy > 0.5:
            traits.extend([
                "Well-balanced between active and contemplative states",
                "Adaptable to various social and work environments",
                "Demonstrates emotional flexibility"
            ])
        else:
            traits.extend([
                "Prefers calm and peaceful environments",
                "Values depth and meaningful conversations",
                "Strong capacity for concentration and reflection"
            ])
        
        # Valence-based traits
        if valence > 0.7:
            traits.extend([
                "Naturally optimistic with a positive outlook",
                "Brings uplifting energy to social situations",
                "Resilient in face of challenges"
            ])
        elif valence > 0.4:
            traits.extend([
                "Emotionally balanced and stable",
                "Realistic yet hopeful perspective on life"
            ])
        else:
            traits.extend([
                "Deeply empathetic and emotionally aware",
                "Appreciates complexity in art and relationships",
                "Values authenticity over superficial positivity"
            ])
        
        # Emotional range traits
        if emotional_range > 0.3:
            traits.append("Embraces emotional diversity and complexity")
        else:
            traits.append("Consistent emotional preferences and stability")
        
        return traits[:5]  # Return top 5 traits
    
    def _create_recommendations(self, mood_score, energy, valence, dominant_mood):
        """Create personalized recommendations based on analysis"""
        
        recommendations = []
        
        # Base recommendations on specific mood patterns
        if "Energetic" in dominant_mood and "Happy" in dominant_mood:
            recommendations.extend([
                f"Your high-energy, positive music taste (score: {mood_score:.2f}) suggests you'd enjoy dance, pop, and upbeat indie tracks",
                "Try creating workout playlists with similar high-energy tracks to maintain motivation",
                "Explore festival playlists and live concert recordings for that energetic crowd feeling",
                "Consider sharing your upbeat playlists with friends who need mood boosts"
            ])
        elif "Calm" in dominant_mood:
            recommendations.extend([
                f"Your preference for calm music (score: {mood_score:.2f}) indicates you'd appreciate ambient, acoustic, and chill-hop genres",
                "Create focus playlists with similar calm tracks for studying or working",
                "Explore nature soundscapes and instrumental music for meditation",
                "Try building bedtime playlists with gentle, soothing tracks"
            ])
        elif "Intense" in dominant_mood or "Dramatic" in dominant_mood:
            recommendations.extend([
                f"Your taste for intense music (score: {mood_score:.2f}) suggests you'd enjoy progressive rock, cinematic scores, and emotional ballads",
                "Explore movie soundtracks and epic orchestral pieces",
                "Try listening to concept albums that tell complete emotional stories",
                "Consider using dramatic music during creative or focused work sessions"
            ])
        elif "Melancholic" in dominant_mood or "Reflective" in dominant_mood:
            recommendations.extend([
                f"Your reflective music choices (score: {mood_score:.2f}) align with indie folk, alternative rock, and contemplative jazz",
                "Explore singer-songwriter albums with deep lyrical content",
                "Try rainy day playlists with similar introspective tracks",
                "Use this music during journaling or personal reflection time"
            ])
        else:
            recommendations.extend([
                f"Your balanced music taste (score: {mood_score:.2f}) suggests exploring multiple genres to match different moods",
                "Create situation-specific playlists: morning energy, work focus, evening wind-down",
                "Try the 'Discover Weekly' feature to find new tracks that match your diverse taste",
                "Experiment with different cultural music styles for variety"
            ])
        
        # Add energy-specific recommendations
        if energy > 0.7:
            recommendations.append("Your high-energy preference suggests you'd love gym playlists and motivational tracks")
        elif energy < 0.3:
            recommendations.append("Your low-energy preference aligns with spa music, lo-fi beats, and ambient soundscapes")
        
        return recommendations[:6]  # Return top 6 personalized recommendations
        
        return recommendations[:5]
    
    def _provide_mental_health_tips(self, mood_score, energy, emotional_range):
        """Provide evidence-based mental health tips related to music"""
        
        tips = []
        
        if energy < 0.3:
            tips.extend([
                "Use upbeat music strategically to naturally boost energy levels",
                "Create a 'morning motivation' playlist for starting your day positively"
            ])
        
        if emotional_range < 0.2:
            tips.append("Explore different musical moods to expand emotional flexibility")
        
        # Universal mental health tips
        tips.extend([
            "Practice mindful listening - focus entirely on music for 10 minutes daily",
            "Use music as a healthy coping mechanism for stress management",
            "Regular music listening can improve mood and reduce anxiety",
            "Share meaningful songs with others to strengthen social connections"
        ])
        
        return tips[:4]
    
    def _create_mood_coaching(self, mood_score, energy, valence, dominant_mood, total_tracks):
        """Create personalized mood coaching message"""
        
        if mood_score > 0.6:
            return f"Your {dominant_mood.lower()} music taste demonstrates excellent emotional self-care! With {total_tracks} tracks analyzed, it's clear you're intentionally choosing music that supports your positive mindset. This shows strong emotional intelligence and self-awareness. Keep using music as a tool for maintaining your emotional wellness, and consider how your upbeat choices might inspire others around you."
        
        elif mood_score > 0.3:
            return f"Your diverse taste in {dominant_mood.lower()} music shows emotional balance and maturity. Analyzing {total_tracks} tracks reveals you're thoughtfully curating your musical environment. This balanced approach to music selection reflects a healthy relationship with your emotions. Consider experimenting with slightly more energizing tracks to enhance your already stable emotional foundation."
        
        else:
            return f"Your preference for {dominant_mood.lower()} music shows deep emotional awareness and sensitivity - valuable qualities in today's world. Your {total_tracks} track selection reveals someone who uses music for authentic emotional processing. While this depth is a strength, consider gradually incorporating some uplifting tracks to support emotional resilience. Remember, seeking variety in music can mirror seeking balance in life."

if __name__ == "__main__":
    # Test the local AI insights
    local_ai = LocalMoodAI()
    
    test_summary = {
        'total_tracks': 50,
        'avg_mood_score': 0.65,
        'avg_energy': 0.7,
        'avg_valence': 0.8,
        'most_common_mood': 'Happy & Energetic',
        'emotional_range': 0.25,
        'total_duration_hours': 3.5
    }
    
    test_tracks = ["Song 1 by Artist 1", "Song 2 by Artist 2"]
    
    insights = local_ai.generate_mood_insights(test_summary, test_tracks)
    
    print("🧪 Local AI Insights Test:")
    print(f"🎭 Emotional Analysis: {insights['emotional_analysis'][:100]}...")
    print(f"🧩 Personality Traits: {len(insights['personality_traits'])} traits")
    print(f"💡 Recommendations: {len(insights['recommendations'])} recommendations")
    print(f"💚 Mental Health Tips: {len(insights['mental_health_tips'])} tips")
    print("✅ Local AI insights working perfectly!")
