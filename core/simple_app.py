"""
MoodScope - Simplified App WITHOUT Authentication
Analyzes public playlists only - no login required
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
import sqlite3
from typing import Optional
import urllib.parse

# Import our custom modules
from fallback_spotify import FallbackSpotifyAnalyzer
from ai_insights import MoodAI
from local_ai_insights import LocalMoodAI
from visualizer import MoodVisualizer

# Page config
st.set_page_config(
    page_title="MoodScope - AI Music Mood Analysis",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
    }
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .info-box {
        background: #d1ecf1;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .mood-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        color: white;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

class SimpleMoodScope:
    def __init__(self):
        """Initialize SimpleMoodScope without authentication"""
        self.spotify_analyzer = None
        self.mood_ai = None
        self.visualizer = MoodVisualizer()
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing analysis history"""
        conn = sqlite3.connect('data/mood_analysis.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_url TEXT,
                timestamp DATETIME,
                mood_score REAL,
                dominant_mood TEXT,
                total_tracks INTEGER,
                analysis_data TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def initialize_services(self):
        """Initialize Spotify and AI services - NO AUTH REQUIRED"""
        try:
            # Always use client credentials (no user auth needed)
            if not self.spotify_analyzer:
                self.spotify_analyzer = FallbackSpotifyAnalyzer(use_user_auth=False)
            
            if not self.mood_ai:
                try:
                    # Try Hugging Face AI first
                    from huggingface_ai_insights import HuggingFaceMoodAI
                    self.mood_ai = HuggingFaceMoodAI()
                    print("✅ Hugging Face AI loaded!")
                except Exception as hf_error:
                    try:
                        # Fall back to OpenAI if available
                        self.mood_ai = MoodAI()
                        print("✅ OpenAI loaded!")
                    except Exception as ai_error:
                        print(f"⚠️ Both AI services unavailable: HF={hf_error}, OpenAI={ai_error}")
                        self.mood_ai = None
            
            return True
        except Exception as e:
            st.error(f"🚨 Service initialization failed: {str(e)}")
            return False
    
    def render_header(self):
        """Render the main header"""
        st.markdown("""
        <div class="main-header">
            <h1>🎵 MoodScope - Simplified Analysis</h1>
            <p style="text-align: center; color: white; margin: 0;">
                Public Playlist Analysis • No Login Required • AI Insights
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_playlist_analyzer(self):
        """Render the playlist analysis interface"""
        st.markdown("### 🎶 Analyze Any Public Spotify Playlist")
        
        # Information box
        st.markdown("""
        <div class="info-box">
            <h4>📋 How to Use:</h4>
            <ol>
                <li>Go to Spotify and find any <strong>public</strong> playlist</li>
                <li>Click "Share" → "Copy link to playlist"</li>
                <li>Paste the URL below and click "Analyze"</li>
            </ol>
            <p><strong>Note:</strong> Only public playlists can be analyzed without login.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # URL input
        playlist_url = st.text_input(
            "Spotify Playlist URL",
            placeholder="https://open.spotify.com/playlist/...",
            key="playlist_url"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Analyze Playlist", type="primary", use_container_width=True):
                if playlist_url:
                    self.analyze_playlist(playlist_url)
                else:
                    st.error("Please enter a playlist URL")
    
    def analyze_playlist(self, playlist_url):
        """Analyze the playlist and display results"""
        if not self.initialize_services():
            st.error("Failed to initialize services. Please check your configuration.")
            return
        
        try:
            with st.spinner("🎵 Analyzing playlist..."):
                # Get playlist data
                df = self.spotify_analyzer.analyze_playlist(playlist_url)
                
                if df.empty:
                    st.error("Could not analyze this playlist. Make sure it's public and the URL is correct.")
                    return
                
                # Get mood summary
                mood_summary = self.spotify_analyzer.get_mood_summary(df)
                
                # Display results
                self.display_analysis_results(df, mood_summary, playlist_url)
                
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            st.info("💡 Try using the demo mode: `streamlit run utils/demo_app.py --server.port 8502`")
    
    def display_analysis_results(self, df, mood_summary, playlist_url):
        """Display the complete analysis results"""
        # Success message
        st.markdown(f"""
        <div class="success-box">
            <h4>✅ Analysis Complete!</h4>
            <p>Successfully analyzed <strong>{len(df)} tracks</strong> from your playlist.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key metrics
        st.markdown("### 📊 Key Mood Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <h3 style="color: #667eea;">{mood_summary['mood_score']:.2f}</h3>
                <p>Mood Score</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <h3 style="color: #28a745;">{mood_summary['energy_level']:.2f}</h3>
                <p>Energy Level</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <h3 style="color: #ffc107;">{mood_summary['valence']:.2f}</h3>
                <p>Positivity</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-container">
                <h3 style="color: #dc3545;">{len(df)}</h3>
                <p>Total Tracks</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Mood categories
        st.markdown("### 🎭 Mood Distribution")
        if 'mood_category' in df.columns:
            mood_counts = df['mood_category'].value_counts()
            
            # Create mood badges
            mood_badges = ""
            colors = {
                'Happy & Energetic': '#28a745',
                'Happy & Calm': '#17a2b8', 
                'Neutral': '#6c757d',
                'Sad & Calm': '#fd7e14',
                'Sad & Energetic': '#dc3545'
            }
            
            for mood, count in mood_counts.items():
                color = colors.get(mood, '#6c757d')
                mood_badges += f'<span class="mood-badge" style="background-color: {color};">{mood}: {count}</span>'
            
            st.markdown(mood_badges, unsafe_allow_html=True)
        
        # Enhanced Visualizations
        st.markdown("### 📈 Comprehensive Mood Visualizations")
        
        # Create tabs for different visualization types
        viz_tab1, viz_tab2, viz_tab3 = st.tabs(["🎭 Mood Distribution", "📊 Audio Features", "📈 Track Analysis"])
        
        with viz_tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                if 'mood_category' in df.columns:
                    st.markdown("#### Mood Distribution")
                    try:
                        # Debug info
                        st.write(f"Debug: visualizer type = {type(self.visualizer)}")
                        st.write(f"Debug: has method = {hasattr(self.visualizer, 'create_mood_distribution')}")
                        
                        fig = self.visualizer.create_mood_distribution(df)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Visualization error: {e}")
                        # Fallback - create a simple mood distribution
                        mood_counts = df['mood_category'].value_counts()
                        st.bar_chart(mood_counts)
            
            with col2:
                if 'valence' in df.columns and 'energy' in df.columns:
                    st.markdown("#### Valence vs Energy")
                    fig = self.visualizer.create_valence_energy_scatter(df)
                    st.plotly_chart(fig, use_container_width=True)
        
        with viz_tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Audio Features Profile")
                fig = self.visualizer.create_audio_features_radar(mood_summary)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if len(df) > 1:
                    st.markdown("#### Feature Trends")
                    fig = self.visualizer.create_audio_features_heatmap(df)
                    st.plotly_chart(fig, use_container_width=True)
        
        with viz_tab3:
            if len(df) > 2:
                st.markdown("#### Track-by-Track Analysis")
                fig = self.visualizer.create_track_timeline(df)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Need more tracks for timeline visualization")
        
        # AI Insights
        self.display_ai_insights(mood_summary, df.to_dict('records')[:5])
        
        # Track details
        with st.expander("🎵 Track Details"):
            st.dataframe(df[['name', 'artist', 'mood_score', 'energy', 'valence']], use_container_width=True)
        
        # Save analysis
        self.save_analysis(playlist_url, mood_summary, len(df))
    
    def display_ai_insights(self, mood_summary, sample_tracks):
        """Display comprehensive AI-generated insights"""
        st.markdown("### 🧠 AI-Powered Music Analysis")
        
        try:
            # Generate insights using available AI
            if self.mood_ai:
                insights = self.mood_ai.generate_mood_insights(mood_summary, sample_tracks)
                ai_type = "Hugging Face AI"
            else:
                # Use local AI fallback
                local_ai = LocalMoodAI()
                insights = local_ai.generate_mood_insights(mood_summary, sample_tracks)
                ai_type = "Local AI"
            
            # Display AI type
            st.info(f"🤖 Analysis powered by {ai_type}")
            
            # Main insights in tabs
            tab1, tab2, tab3, tab4 = st.tabs(["🎭 Emotional Profile", "💡 Insights & Tips", "🎵 Recommendations", "📊 Technical Analysis"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🧠 Emotional Analysis")
                    emotional_analysis = insights.get('emotional_analysis', 'Your music reflects a unique emotional landscape.')
                    st.markdown(f"""
                    <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 4px solid #4682b4;">
                        <p style="margin: 0; font-size: 16px; line-height: 1.6;">{emotional_analysis}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Mood coaching
                    st.markdown("#### � Mood Coaching")
                    mood_coaching = insights.get('mood_coaching', 'Your musical journey shows great emotional awareness!')
                    st.markdown(f"""
                    <div style="background-color: #f0fff0; padding: 15px; border-radius: 10px; border-left: 4px solid #32cd32;">
                        <p style="margin: 0; font-size: 16px; line-height: 1.6;">{mood_coaching}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("#### 👤 Personality Insights")
                    traits = insights.get('personality_traits', ['Music lover', 'Emotionally expressive'])
                    if isinstance(traits, list):
                        for i, trait in enumerate(traits[:4]):
                            icon = ["🌟", "💫", "✨", "🎭"][i % 4]
                            st.markdown(f"**{icon} {trait}**")
                    else:
                        st.write(traits)
                    
                    # Emotional metrics
                    st.markdown("#### 📈 Emotional Metrics")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Mood Score", f"{mood_summary.get('mood_score', 0.5):.2f}", "Positivity Level")
                        st.metric("Energy Level", f"{mood_summary.get('avg_energy', 0.5):.2f}", "Activity Level")
                    with col_b:
                        st.metric("Emotional Range", f"{mood_summary.get('emotional_range', 0.2):.2f}", "Variety")
                        st.metric("Total Tracks", mood_summary.get('total_tracks', 0))
            
            with tab2:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 💡 Personalized Recommendations")
                    recommendations = insights.get('recommendations', ['Explore new music genres'])
                    if isinstance(recommendations, list):
                        for i, rec in enumerate(recommendations[:4]):
                            st.markdown(f"**{i+1}.** {rec}")
                    else:
                        st.write(recommendations)
                
                with col2:
                    st.markdown("#### 🧘 Mental Health & Wellness")
                    tips = insights.get('mental_health_tips', ['Music supports emotional wellbeing'])
                    if isinstance(tips, list):
                        for tip in tips[:3]:
                            st.markdown(f"🌱 {tip}")
                    else:
                        st.write(tips)
            
            with tab3:
                st.markdown("#### 🎵 Curated Song Recommendations")
                
                # Generate different types of recommendations
                rec_types = ["improve", "relax", "energize"]
                cols = st.columns(3)
                
                for i, rec_type in enumerate(rec_types):
                    with cols[i]:
                        if rec_type == "improve":
                            st.markdown("##### 😊 Mood Boosters")
                            icon = "⬆️"
                        elif rec_type == "relax":
                            st.markdown("##### 😌 Relaxation")
                            icon = "🧘"
                        else:
                            st.markdown("##### ⚡ Energizers")
                            icon = "🔥"
                        
                        try:
                            if self.mood_ai:
                                song_recs = self.mood_ai.generate_song_recommendations(mood_summary, rec_type)
                            else:
                                song_recs = [f"Explore {rec_type} music genres", f"Try {rec_type} playlists", f"Discover {rec_type} artists"]
                            
                            for rec in song_recs[:3]:
                                st.markdown(f"{icon} {rec}")
                        except:
                            st.markdown(f"{icon} Explore {rec_type} music")
            
            with tab4:
                st.markdown("#### 📊 Technical Music Analysis")
                
                # Advanced metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 🎵 Audio Features")
                    features = {
                        "Valence (Positivity)": mood_summary.get('avg_valence', 0.5),
                        "Energy": mood_summary.get('avg_energy', 0.5),
                        "Danceability": mood_summary.get('avg_danceability', 0.5),
                        "Popularity": mood_summary.get('avg_popularity', 50)
                    }
                    
                    for feature, value in features.items():
                        if feature == "Popularity":
                            st.progress(value/100, text=f"{feature}: {value:.1f}/100")
                        else:
                            st.progress(value, text=f"{feature}: {value:.2f}")
                
                with col2:
                    st.markdown("##### 🎭 Mood Breakdown")
                    mood_dist = mood_summary.get('mood_distribution', {})
                    total = sum(mood_dist.values()) if mood_dist else 1
                    
                    for mood, count in mood_dist.items():
                        percentage = (count / total) * 100
                        st.markdown(f"**{mood}**: {count} tracks ({percentage:.1f}%)")
                
                # Analysis quality indicator
                st.markdown("##### 🔍 Analysis Quality")
                using_estimates = mood_summary.get('using_estimates', False)
                if using_estimates:
                    st.warning("🤖 Analysis based on AI estimation (Spotify audio features unavailable)")
                else:
                    st.success("✅ Analysis based on Spotify audio features")
                
        except Exception as e:
            st.error(f"⚠️ AI insights unavailable: {str(e)}")
            # Show basic fallback insights
            st.markdown("#### 📊 Basic Analysis")
            st.write(f"Analyzed {mood_summary.get('total_tracks', 0)} tracks")
            st.write(f"Average mood score: {mood_summary.get('mood_score', 0.5):.2f}")
            st.write(f"Dominant mood: {mood_summary.get('most_common_mood', 'Unknown')}")
    
    def save_analysis(self, playlist_url, mood_summary, total_tracks):
        """Save analysis to database"""
        try:
            conn = sqlite3.connect('data/mood_analysis.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analyses (playlist_url, timestamp, mood_score, dominant_mood, total_tracks, analysis_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                playlist_url,
                datetime.now(),
                mood_summary['mood_score'],
                mood_summary.get('dominant_mood', 'Unknown'),
                total_tracks,
                str(mood_summary)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.warning(f"Could not save analysis: {str(e)}")
    
    def render_sidebar(self):
        """Render sidebar with info and controls"""
        st.sidebar.markdown("### 🎵 MoodScope Simple")
        
        st.sidebar.markdown("""
        **No Authentication Required!** 
        
        ✅ Analyze any public playlist  
        ✅ No login needed  
        ✅ Instant results  
        ✅ AI insights included  
        """)
        
        st.sidebar.markdown("---")
        
        # Demo section
        st.sidebar.markdown("### 🎮 Try Demo Mode")
        st.sidebar.markdown("Want to see features without a playlist?")
        
        if st.sidebar.button("🚀 Launch Demo App"):
            st.sidebar.markdown("""
            Run this command in terminal:
            ```bash
            streamlit run utils/demo_app.py --server.port 8502
            ```
            Then visit: http://localhost:8502
            """)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Quick Stats")
        
        # Show recent analyses count
        try:
            conn = sqlite3.connect('data/mood_analysis.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM analyses')
            count = cursor.fetchone()[0]
            conn.close()
            
            st.sidebar.metric("Total Analyses", count)
        except:
            st.sidebar.metric("Total Analyses", "0")

def main():
    """Main application function"""
    app = SimpleMoodScope()
    
    # Render components
    app.render_header()
    app.render_sidebar()
    app.render_playlist_analyzer()

if __name__ == "__main__":
    main()
