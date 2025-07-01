"""
MoodScope - Enhanced App with User Authentication
Supports full Spotify API access with user login
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

# Custom CSS (same as before)
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
    .auth-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .insight-box {
        background: #e3f2fd;
        color: #0d47a1;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    .insight-box h4 {
        margin-top: 0;
        color: #0d47a1;
    }
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class EnhancedMoodScopeApp:
    def __init__(self):
        """Initialize the enhanced MoodScope application"""
        self.setup_database()
        self.spotify_analyzer = None
        self.mood_ai = None
        self.local_ai = LocalMoodAI()  # Always available fallback
        self.visualizer = MoodVisualizer()
        
        # Handle Spotify callback
        self.handle_spotify_callback()
    
    def setup_database(self):
        """Setup SQLite database for storing analysis history"""
        os.makedirs('data', exist_ok=True)
        self.db_path = 'data/moodscope.db'
        
        conn = sqlite3.connect(self.db_path)
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
    
    def handle_spotify_callback(self):
        """Handle Spotify OAuth callback"""
        query_params = st.query_params
        
        if 'code' in query_params:
            st.success("🎉 Successfully connected to Spotify!")
            # Clear the URL parameters by rerunning
            st.rerun()
    
    def initialize_services(self, force_user_auth=False):
        """Initialize Spotify and AI services"""
        try:
            # Default to client credentials for better web app experience
            if not self.spotify_analyzer or force_user_auth:
                self.spotify_analyzer = FallbackSpotifyAnalyzer(use_user_auth=force_user_auth)
            
            if not self.mood_ai:
                try:
                    self.mood_ai = MoodAI()
                except Exception as ai_error:
                    st.warning(f"⚠️ OpenAI service unavailable: {ai_error}")
                    self.mood_ai = None
            
            return True
        except Exception as e:
            st.error(f"🚨 Service initialization failed: {str(e)}")
            return False
    
    def render_header(self):
        """Render the main header"""
        st.markdown("""
        <div class="main-header">
            <h1>🎵 MoodScope - Enhanced Real-Time Analysis</h1>
            <p style="text-align: center; color: white; margin: 0;">
                Full Spotify Integration • User Authentication • AI Insights
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_auth_section(self):
        """Render Spotify authentication section"""
        st.sidebar.subheader("🔐 Spotify Authentication")
        
        # Check if user is authenticated
        if os.path.exists('.spotify_cache'):
            st.sidebar.success("✅ Connected to Spotify")
            
            if st.sidebar.button("🔄 Refresh Connection"):
                if os.path.exists('.spotify_cache'):
                    os.remove('.spotify_cache')
                st.rerun()
        else:
            st.sidebar.warning("⚠️ Not connected to Spotify")
            
            if st.sidebar.button("🔗 Connect to Spotify", type="primary"):
                try:
                    analyzer = FallbackSpotifyAnalyzer(use_user_auth=True)
                    auth_url = analyzer.get_auth_url()
                    if auth_url:
                        st.sidebar.markdown(f"""
                        <div class="auth-box">
                            <p><strong>🎯 Step 1:</strong> Click the link below</p>
                            <p><strong>🎯 Step 2:</strong> Login to Spotify</p>
                            <p><strong>🎯 Step 3:</strong> Come back here</p>
                            <br>
                            <a href="{auth_url}" target="_blank">
                                <button style="background: #1DB954; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                                    🎵 Connect Spotify Account
                                </button>
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.sidebar.error(f"Auth error: {str(e)}")
    
    def render_sidebar(self):
        """Render the sidebar with controls"""
        st.sidebar.title("🎛️ Enhanced Controls")
        
        # Authentication section
        self.render_auth_section()
        
        # API Status
        st.sidebar.subheader("🔧 API Status")
        
        spotify_configured = bool(os.getenv('SPOTIFY_CLIENT_ID') and os.getenv('SPOTIFY_CLIENT_SECRET'))
        openai_configured = bool(os.getenv('OPENAI_API_KEY'))
        spotify_connected = os.path.exists('.spotify_cache')
        
        st.sidebar.success("✅ Spotify Config") if spotify_configured else st.sidebar.error("❌ Spotify Config")
        st.sidebar.success("✅ Spotify Connected") if spotify_connected else st.sidebar.warning("⚠️ Spotify Not Connected")
        st.sidebar.success("✅ OpenAI API") if openai_configured else st.sidebar.error("❌ OpenAI API")
        
        # Playlist input
        st.sidebar.subheader("🎵 Playlist Analysis")
        
        # Example playlists
        st.sidebar.markdown("**🎯 Try these verified working playlists:**")
        example_playlists = {
            "Bollywood Pop (459 tracks)": "https://open.spotify.com/playlist/67kbhvyUfnMbzgX6zRxrPg",
            "Hindi Hits (104 tracks)": "https://open.spotify.com/playlist/4stlIpoPS7uKCsmUA7D8KZ",
            "Workout Playlist (146 tracks)": "https://open.spotify.com/playlist/26v8JjOQz1RCCJzJNZz5ht"
        }
        
        for name, url in example_playlists.items():
            if st.sidebar.button(f"📋 {name}", key=f"example_{name}"):
                st.session_state['playlist_url'] = url
        
        playlist_url = st.sidebar.text_input(
            "Or paste your own Spotify Playlist URL",
            value=st.session_state.get('playlist_url', ''),
            placeholder="https://open.spotify.com/playlist/...",
            help="Paste any public Spotify playlist URL"
        )
        
        analyze_button = st.sidebar.button("🔍 Analyze Playlist", type="primary")
        
        # Analysis options
        st.sidebar.subheader("⚙️ Options")
        show_detailed_insights = st.sidebar.checkbox("Detailed AI Insights", value=True)
        show_advanced_charts = st.sidebar.checkbox("Advanced Visualizations", value=True)
        force_user_auth = st.sidebar.checkbox("Force User Authentication", value=False, help="Use full Spotify user auth for better access (may require manual setup)")
        
        return playlist_url, analyze_button, show_detailed_insights, show_advanced_charts, force_user_auth
    
    def analyze_playlist(self, playlist_url: str, force_user_auth: bool) -> Optional[tuple]:
        """Analyze a Spotify playlist and return results"""
        if not self.initialize_services(force_user_auth=force_user_auth):
            return None
        
        try:
            with st.spinner("🎵 Analyzing your playlist with enhanced access..."):
                # Get playlist data
                df = self.spotify_analyzer.analyze_playlist(playlist_url)
                mood_summary = self.spotify_analyzer.get_mood_summary(df)
                
                # Generate AI insights (with robust fallback system)
                insights = None
                if self.mood_ai:
                    try:
                        sample_tracks = [f"{row['name']} by {row['artist']}" for _, row in df.head(10).iterrows()]
                        insights = self.mood_ai.generate_mood_insights(mood_summary, sample_tracks)
                        st.info("🤖 **AI Insights**: Generated using GPT-3.5-turbo")
                    except Exception as ai_error:
                        st.warning(f"⚠️ OpenAI API unavailable: {str(ai_error)[:100]}...")
                        insights = None
                
                # Use local AI as fallback if OpenAI fails
                if not insights:
                    try:
                        sample_tracks = [f"{row['name']} by {row['artist']}" for _, row in df.head(10).iterrows()]
                        insights = self.local_ai.generate_mood_insights(mood_summary, sample_tracks)
                        st.info("🧠 **Smart Insights**: Generated using advanced local analysis")
                    except Exception as local_error:
                        st.warning(f"⚠️ Local insights failed: {str(local_error)}")
                        # Final fallback with basic insights
                        insights = {
                            'emotional_analysis': f"Your playlist shows a {mood_summary['most_common_mood'].lower()} mood with an average mood score of {mood_summary['avg_mood_score']:.2f}.",
                            'personality_traits': [f"You enjoy {mood_summary['most_common_mood'].lower()} music"],
                            'recommendations': ["Keep exploring music that matches your mood!"],
                            'mood_coaching': f"Your music taste reflects a {mood_summary['most_common_mood'].lower()} personality."
                        }
                
                # Save analysis
                try:
                    self.save_analysis(playlist_url, mood_summary, df.to_json())
                except Exception as save_error:
                    st.warning(f"⚠️ Could not save analysis: {save_error}")
                
                return df, mood_summary, insights
        
        except Exception as e:
            error_msg = str(e)
            st.error(f"🚨 Analysis failed: {error_msg}")
            
            # Provide specific suggestions based on error type
            if "not found" in error_msg or "404" in error_msg:
                st.warning("💡 **Playlist Not Found Solutions:**")
                st.write("• Check the playlist URL is correct")
                st.write("• Make sure the playlist is public")
                st.write("• Try one of the verified playlists in the sidebar")
            elif "Access denied" in error_msg or "403" in error_msg or "regional restrictions" in error_msg.lower():
                st.warning("💡 **Regional Restriction / Access Issue:**")
                st.write("• This playlist may not be available in your region")
                st.write("• Try creating your own playlist on Spotify")
                st.write("• Use the demo mode for guaranteed functionality:")
                st.code("streamlit run demo_app.py --server.port 8502")
                st.write("• Demo mode works perfectly and shows all features!")
            elif "401" in error_msg:
                st.warning("💡 **Authentication Issue:**")
                st.write("• Click 'Connect to Spotify' in the sidebar")
                st.write("• Complete the OAuth flow in your browser")
            else:
                st.warning("💡 **General Troubleshooting:**")
                st.write("• Try creating your own Spotify playlist (guaranteed to work)")
                st.write("• Use demo mode: `streamlit run demo_app.py --server.port 8502`")
                st.write("• Check your internet connection")
            
            return None
    
    def save_analysis(self, playlist_url: str, mood_summary: dict, analysis_data: str):
        """Save analysis to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analyses (playlist_url, timestamp, mood_score, dominant_mood, total_tracks, analysis_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            playlist_url,
            datetime.now().isoformat(),  # Convert datetime to string
            mood_summary['avg_mood_score'],
            mood_summary['most_common_mood'],
            mood_summary['total_tracks'],
            analysis_data
        ))
        
        conn.commit()
        conn.close()
    
    def render_overview_metrics(self, mood_summary):
        """Render overview metrics"""
        st.subheader("📊 Quick Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🎵 Total Tracks",
                mood_summary['total_tracks'],
                help="Number of tracks analyzed"
            )
        
        with col2:
            mood_score = mood_summary['avg_mood_score']
            mood_emoji = "😊" if mood_score > 0.2 else "😐" if mood_score > -0.2 else "😔"
            st.metric(
                f"{mood_emoji} Mood Score",
                f"{mood_score:.2f}",
                help="Average mood score (-1 to 1)"
            )
        
        with col3:
            energy_level = mood_summary['avg_energy']
            energy_emoji = "⚡" if energy_level > 0.7 else "🔋" if energy_level > 0.4 else "🔋"
            st.metric(
                f"{energy_emoji} Energy Level",
                f"{energy_level:.2f}",
                help="Average energy level (0 to 1)"
            )
        
        with col4:
            listening_time = mood_summary['total_duration_hours']
            st.metric(
                "⏱️ Total Duration",
                f"{listening_time:.1f}h",
                help="Total playlist duration"
            )

    def render_insights_section(self, insights):
        """Render AI insights section"""
        st.subheader("🧠 AI-Powered Insights")
        
        # Emotional Analysis
        if insights.get('emotional_analysis'):
            st.markdown(f"""
            <div class="insight-box">
                <h4>🎭 Emotional Analysis</h4>
                <p>{insights['emotional_analysis']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Two column layout for insights
        col1, col2 = st.columns(2)
        
        with col1:
            if insights.get('personality_traits'):
                st.markdown("**🧩 Personality Traits**")
                for trait in insights['personality_traits']:
                    st.write(f"• {trait}")
            
            if insights.get('mental_health_tips'):
                st.markdown("**💚 Mental Health Tips**")
                for tip in insights['mental_health_tips']:
                    st.write(f"• {tip}")
        
        with col2:
            if insights.get('recommendations'):
                st.markdown("**💡 Recommendations**")
                for rec in insights['recommendations']:
                    st.write(f"• {rec}")
        
        # Mood Coaching
        if insights.get('mood_coaching'):
            st.markdown(f"""
            <div class="insight-box">
                <h4>🎯 Personal Mood Coaching</h4>
                <p>{insights['mood_coaching']}</p>
            </div>
            """, unsafe_allow_html=True)

    def render_visualizations(self, df, mood_summary, show_advanced):
        """Render all visualizations"""
        st.subheader("📈 Visual Analysis")
        
        # Create tabs for different visualizations
        if show_advanced:
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🎭 Mood Overview", 
                "🧠 Emotional Profile", 
                "📊 Timeline", 
                "🌡️ Heatmap", 
                "📈 Advanced"
            ])
        else:
            tab1, tab2, tab3 = st.tabs([
                "🎭 Mood Overview", 
                "🧠 Emotional Profile", 
                "📊 Timeline"
            ])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                fig_pie = self.visualizer.create_mood_distribution_pie(mood_summary)
                st.plotly_chart(fig_pie, use_container_width=True)
            with col2:
                fig_gauge = self.visualizer.create_mood_gauge(mood_summary)
                st.plotly_chart(fig_gauge, use_container_width=True)
        
        with tab2:
            fig_radar = self.visualizer.create_emotion_radar(df)
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # Top tracks by different metrics
            col1, col2 = st.columns(2)
            with col1:
                fig_energy = self.visualizer.create_top_tracks_chart(
                    df, 'energy', '⚡ Most Energetic Tracks'
                )
                st.plotly_chart(fig_energy, use_container_width=True)
            with col2:
                fig_valence = self.visualizer.create_top_tracks_chart(
                    df, 'valence', '😊 Most Positive Tracks'
                )
                st.plotly_chart(fig_valence, use_container_width=True)
        
        with tab3:
            fig_timeline = self.visualizer.create_mood_timeline(df)
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        if show_advanced:
            with tab4:
                fig_heatmap = self.visualizer.create_emotion_heatmap(df)
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            with tab5:
                fig_comparison = self.visualizer.create_comparison_charts(df)
                st.plotly_chart(fig_comparison, use_container_width=True)

    def render_track_details(self, df):
        """Render detailed track information"""
        st.subheader("🎵 Track Details")
        
        # Sort options
        sort_by = st.selectbox(
            "Sort tracks by:",
            ['mood_score', 'energy', 'valence', 'popularity', 'danceability'],
            help="Choose how to sort the track list"
        )
        
        ascending = st.checkbox("Ascending order", value=False)
        
        # Sort dataframe
        df_sorted = df.sort_values(sort_by, ascending=ascending)
        
        # Display tracks
        display_cols = ['name', 'artist', 'mood_category', 'mood_score', 'energy', 'valence', 'popularity']
        st.dataframe(
            df_sorted[display_cols].round(3),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = df_sorted.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Analysis (CSV)",
            data=csv,
            file_name=f"moodscope_enhanced_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    def run(self):
        """Main application runner"""
        self.render_header()
        
        # Sidebar
        playlist_url, analyze_button, show_detailed_insights, show_advanced_charts, force_user_auth = self.render_sidebar()
        
        # Main content
        if analyze_button and playlist_url:
            # Store URL in session state
            st.session_state['playlist_url'] = playlist_url
            
            # Analyze playlist
            result = self.analyze_playlist(playlist_url, force_user_auth)
            
            if result:
                df, mood_summary, insights = result
                
                # Store in session state
                st.session_state['analysis_data'] = {
                    'df': df,
                    'mood_summary': mood_summary,
                    'insights': insights
                }
                
                st.success(f"✅ Successfully analyzed {len(df)} tracks!")
                
                # Show if using estimates
                if mood_summary.get('using_estimates', False):
                    st.info("🎯 **Smart Analysis**: Using metadata-based mood estimation (audio features API restricted in your region)")
                else:
                    st.info("🎵 **Full Analysis**: Using real Spotify audio features")
        
        # Display results if available
        if 'analysis_data' in st.session_state:
            data = st.session_state['analysis_data']
            df = data['df']
            mood_summary = data['mood_summary']
            insights = data['insights']
            
            # Show success message
            st.markdown("""
            <div class="success-box">
                <h4>🎉 Real-Time Analysis Complete!</h4>
                <p>Successfully connected to Spotify and analyzed your playlist with full API access.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show results sections
            col1, col2 = st.columns([2, 1])
            
            with col1:
                self.render_overview_metrics(mood_summary)
            
            with col2:
                st.markdown("### 🎯 Quick Stats")
                st.write(f"**Dominant Mood:** {mood_summary['most_common_mood']}")
                st.write(f"**Avg Energy:** {mood_summary['avg_energy']:.2f}")
                st.write(f"**Avg Valence:** {mood_summary['avg_valence']:.2f}")
                if mood_summary.get('using_estimates'):
                    st.write("**Method:** Metadata-based estimation")
                else:
                    st.write("**Method:** Real audio features")
            
            # AI Insights
            if show_detailed_insights and insights:
                self.render_insights_section(insights)
            
            # Visualizations
            if show_advanced_charts:
                self.render_visualizations(df, mood_summary, show_advanced_charts)
            
            # Track details
            self.render_track_details(df)
        
        else:
            # Welcome message with setup instructions
            st.markdown("""
            ## 👋 Welcome to Enhanced MoodScope!
            
            **Real-time Spotify playlist analysis with full user authentication.**
            
            ### 🚀 Getting Started:
            1. **Connect Spotify**: Use the sidebar to authenticate with your Spotify account
            2. **Paste Playlist URL**: Any public Spotify playlist works
            3. **Get Real-Time Analysis**: Live data from Spotify's API
            
            ### 🔐 Enhanced Features:
            - **User Authentication** - Full Spotify API access
            - **Real-Time Data** - Live playlist analysis
            - **AI Insights** - GPT-4 powered mood coaching
            - **Advanced Visualizations** - Interactive charts and heatmaps
            
            ### 📋 Setup Requirements:
            1. **Spotify Developer App** with HTTPS redirect URI
            2. **User Authorization** for full API access
            3. **OpenAI API Key** for AI insights
            
            **Connect your Spotify account in the sidebar to get started! 🎵**
            """)

# Initialize and run the application
if __name__ == "__main__":
    app = EnhancedMoodScopeApp()
    app.run()
