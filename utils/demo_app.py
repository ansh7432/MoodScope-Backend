"""
MoodScope Demo App - No API Keys Required
Demonstrates MoodScope functionality with sample data
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# Import visualization module
from visualizer import MoodVisualizer

# Page config
st.set_page_config(
    page_title="MoodScope Demo - AI Music Mood Analysis",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (same as main app)
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
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .demo-banner {
        background: #FFD700;
        color: #333;
        padding: 0.5rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def load_demo_data():
    """Load demo data from files"""
    try:
        df = pd.read_csv('data/demo_playlist.csv')
        
        with open('data/demo_mood_summary.json', 'r') as f:
            mood_summary = json.load(f)
        
        with open('data/demo_insights.json', 'r') as f:
            insights = json.load(f)
        
        return df, mood_summary, insights
    except FileNotFoundError:
        return None, None, None

def render_header():
    """Render the main header with demo banner"""
    st.markdown("""
    <div class="demo-banner">
        🚀 DEMO MODE - Experience MoodScope with sample data (No API keys required!)
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>🎵 MoodScope - AI Music Mood Analysis</h1>
        <p style="text-align: center; color: white; margin: 0;">
            Discover your emotional patterns through music • Powered by AI
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar for demo"""
    st.sidebar.title("🎛️ Demo Controls")
    
    st.sidebar.markdown("""
    ### 🎵 Sample Playlist Analysis
    This demo shows analysis of a curated playlist with 50 diverse tracks including:
    - Classic Rock (Queen, Led Zeppelin)
    - Modern Pop (The Weeknd, Billie Eilish)  
    - Alternative (Radiohead, Nirvana)
    - Soul & R&B (Aretha Franklin, Marvin Gaye)
    """)
    
    load_demo = st.sidebar.button("🔍 Load Demo Analysis", type="primary")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 🚀 Try Full Version
    To analyze your own playlists:
    1. Get Spotify API credentials
    2. Get OpenAI API key  
    3. Run `streamlit run app.py`
    """)
    
    show_detailed_insights = st.sidebar.checkbox("Detailed AI Insights", value=True)
    show_advanced_charts = st.sidebar.checkbox("Advanced Visualizations", value=True)
    
    return load_demo, show_detailed_insights, show_advanced_charts

def render_overview_metrics(mood_summary):
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

def render_insights_section(insights):
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

def render_visualizations(df, mood_summary, show_advanced, visualizer):
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
            fig_pie = visualizer.create_mood_distribution_pie(mood_summary)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            fig_gauge = visualizer.create_mood_gauge(mood_summary)
            st.plotly_chart(fig_gauge, use_container_width=True)
    
    with tab2:
        fig_radar = visualizer.create_emotion_radar(df)
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Top tracks by different metrics
        col1, col2 = st.columns(2)
        with col1:
            fig_energy = visualizer.create_top_tracks_chart(
                df, 'energy', '⚡ Most Energetic Tracks'
            )
            st.plotly_chart(fig_energy, use_container_width=True)
        with col2:
            fig_valence = visualizer.create_top_tracks_chart(
                df, 'valence', '😊 Most Positive Tracks'
            )
            st.plotly_chart(fig_valence, use_container_width=True)
    
    with tab3:
        fig_timeline = visualizer.create_mood_timeline(df)
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    if show_advanced:
        with tab4:
            fig_heatmap = visualizer.create_emotion_heatmap(df)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with tab5:
            fig_comparison = visualizer.create_comparison_charts(df)
            st.plotly_chart(fig_comparison, use_container_width=True)

def render_track_details(df):
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
        file_name=f"moodscope_demo_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def main():
    """Main demo application"""
    render_header()
    
    # Initialize visualizer
    visualizer = MoodVisualizer()
    
    # Sidebar
    load_demo, show_detailed_insights, show_advanced_charts = render_sidebar()
    
    # Check if demo data exists
    if not os.path.exists('data/demo_playlist.csv'):
        st.error("🚨 Demo data not found!")
        st.info("Please run: `python generate_demo_data.py` to create sample data")
        return
    
    # Load demo data automatically or on button press
    if load_demo or 'demo_loaded' not in st.session_state:
        df, mood_summary, insights = load_demo_data()
        
        if df is not None:
            st.session_state['demo_data'] = {
                'df': df,
                'mood_summary': mood_summary,
                'insights': insights
            }
            st.session_state['demo_loaded'] = True
            st.success("✅ Demo playlist analysis loaded!")
        else:
            st.error("Failed to load demo data")
            return
    
    # Display results if available
    if 'demo_data' in st.session_state:
        data = st.session_state['demo_data']
        df = data['df']
        mood_summary = data['mood_summary']
        insights = data['insights']
        
        # Overview metrics
        render_overview_metrics(mood_summary)
        
        # AI Insights
        if show_detailed_insights:
            render_insights_section(insights)
        
        # Visualizations
        render_visualizations(df, mood_summary, show_advanced_charts, visualizer)
        
        # Track details
        with st.expander("🎵 View Detailed Track Information", expanded=False):
            render_track_details(df)
    
    else:
        # Welcome message
        st.markdown("""
        ## 👋 Welcome to MoodScope Demo!
        
        **Experience the power of AI-driven music mood analysis with our sample data.**
        
        ### 🎵 Sample Playlist Features:
        - **50 Diverse Tracks**: From classic rock to modern pop
        - **Multiple Moods**: Happy anthems, contemplative ballads, intense rockers
        - **Real Analysis**: Actual audio feature calculations and AI insights
        
        ### 🚀 Demo Capabilities:
        - **Mood Distribution**: Visual breakdown of emotional categories
        - **AI Personality Analysis**: Insights based on music preferences
        - **Interactive Charts**: Explore emotional patterns and trends
        - **Track Details**: Complete analysis of each song
        
        ### 🎯 Ready for Your Music?
        To analyze your own playlists:
        1. Set up Spotify and OpenAI API credentials
        2. Run the full version with `streamlit run app.py`
        3. Paste any Spotify playlist URL and get instant insights!
        
        ---
        **Click "Load Demo Analysis" in the sidebar to get started! 🎵**
        """)

if __name__ == "__main__":
    main()
