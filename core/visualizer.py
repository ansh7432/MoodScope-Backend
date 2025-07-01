"""
MoodScope - Data Visualization Module
Creates interactive charts and visualizations for mood analysis
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List

class MoodVisualizer:
    def __init__(self):
        """Initialize the visualizer with color schemes"""
        self.mood_colors = {
            "Energetic & Happy": "#FFD700",      # Gold
            "Calm & Content": "#87CEEB",         # Sky Blue
            "Intense & Dramatic": "#FF6B6B",     # Red
            "Melancholic & Reflective": "#9370DB", # Purple
            "Neutral & Balanced": "#98FB98"       # Pale Green
        }
        
        self.emotion_colors = {
            'valence': '#FF69B4',    # Hot Pink
            'energy': '#32CD32',     # Lime Green
            'danceability': '#FF4500', # Orange Red
            'acousticness': '#4169E1', # Royal Blue
            'instrumentalness': '#8A2BE2' # Blue Violet
        }
    
    def create_mood_distribution_pie(self, mood_summary: Dict) -> go.Figure:
        """Create pie chart showing mood distribution"""
        mood_dist = mood_summary['mood_distribution']
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(mood_dist.keys()),
                values=list(mood_dist.values()),
                hole=0.4,
                marker_colors=[self.mood_colors.get(mood, '#CCCCCC') for mood in mood_dist.keys()],
                textinfo='label+percent',
                textfont_size=12
            )
        ])
        
        fig.update_layout(
            title={
                'text': "🎭 Mood Distribution in Your Music",
                'x': 0.5,
                'font': {'size': 20}
            },
            showlegend=True,
            height=500,
            font=dict(size=14)
        )
        
        return fig
    
    def create_mood_distribution(self, df: pd.DataFrame) -> go.Figure:
        """Create mood distribution chart from DataFrame"""
        # Calculate mood distribution from DataFrame
        mood_counts = df['mood_category'].value_counts().to_dict()
        mood_summary = {'mood_distribution': mood_counts}
        return self.create_mood_distribution_pie(mood_summary)
    
    def create_emotion_radar(self, df: pd.DataFrame) -> go.Figure:
        """Create radar chart showing emotional profile"""
        emotions = ['valence', 'energy', 'danceability', 'acousticness', 'speechiness', 'instrumentalness']
        avg_values = [df[emotion].mean() for emotion in emotions]
        
        # Create radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=avg_values,
            theta=emotions,
            fill='toself',
            name='Your Music Profile',
            line_color='rgba(50, 205, 50, 0.8)',
            fillcolor='rgba(50, 205, 50, 0.2)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title={
                'text': "🧠 Your Musical Emotional Profile",
                'x': 0.5,
                'font': {'size': 20}
            },
            height=500,
            font=dict(size=14)
        )
        
        return fig
    
    def create_mood_timeline(self, df: pd.DataFrame) -> go.Figure:
        """Create timeline showing mood progression through playlist"""
        # Add track index for timeline
        df_plot = df.copy()
        df_plot['track_index'] = range(len(df_plot))
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Mood Score Over Time', 'Energy vs Positivity'),
            vertical_spacing=0.1
        )
        
        # Timeline plot
        fig.add_trace(
            go.Scatter(
                x=df_plot['track_index'],
                y=df_plot['mood_score'],
                mode='lines+markers',
                name='Mood Score',
                line=dict(color='#FF69B4', width=3),
                marker=dict(size=6),
                hovertemplate='<b>%{text}</b><br>Mood Score: %{y:.2f}<extra></extra>',
                text=df_plot['name']
            ),
            row=1, col=1
        )
        
        # Scatter plot
        fig.add_trace(
            go.Scatter(
                x=df_plot['energy'],
                y=df_plot['valence'],
                mode='markers',
                name='Tracks',
                marker=dict(
                    size=8,
                    color=df_plot['mood_score'],
                    colorscale='RdYlBu',
                    showscale=True,
                    colorbar=dict(title="Mood Score")
                ),
                hovertemplate='<b>%{text}</b><br>Energy: %{x:.2f}<br>Positivity: %{y:.2f}<extra></extra>',
                text=df_plot['name']
            ),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Track Number", row=1, col=1)
        fig.update_yaxes(title_text="Mood Score", row=1, col=1)
        fig.update_xaxes(title_text="Energy", row=2, col=1)
        fig.update_yaxes(title_text="Positivity (Valence)", row=2, col=1)
        
        fig.update_layout(
            title={
                'text': "📈 Mood Journey Through Your Playlist",
                'x': 0.5,
                'font': {'size': 20}
            },
            height=700,
            showlegend=False
        )
        
        return fig
    
    def create_emotion_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Create heatmap of emotional features"""
        emotions = ['valence', 'energy', 'danceability', 'acousticness', 'speechiness', 'instrumentalness']
        
        # Get top 20 tracks for visibility
        df_subset = df.head(20) if len(df) > 20 else df
        
        # Create matrix
        emotion_matrix = df_subset[emotions].values
        track_names = [f"{row['name'][:30]}..." if len(row['name']) > 30 else row['name'] 
                      for _, row in df_subset.iterrows()]
        
        fig = go.Figure(data=go.Heatmap(
            z=emotion_matrix,
            x=emotions,
            y=track_names,
            colorscale='Viridis',
            hoverongaps=False,
            hovertemplate='Track: %{y}<br>Feature: %{x}<br>Value: %{z:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': "🌡️ Emotional Heatmap of Your Music",
                'x': 0.5,
                'font': {'size': 20}
            },
            xaxis_title="Emotional Features",
            yaxis_title="Tracks",
            height=600,
            font=dict(size=12)
        )
        
        return fig
    
    def create_mood_gauge(self, mood_summary: Dict) -> go.Figure:
        """Create gauge showing overall mood score"""
        mood_score = mood_summary['avg_mood_score']
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=mood_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Mood Score"},
            delta={'reference': 0},
            gauge={
                'axis': {'range': [-1, 1]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [-1, -0.5], 'color': "red"},
                    {'range': [-0.5, 0], 'color': "orange"},
                    {'range': [0, 0.5], 'color': "lightgreen"},
                    {'range': [0.5, 1], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.5
                }
            }
        ))
        
        fig.update_layout(
            title={
                'text': "🎯 Your Mood Meter",
                'x': 0.5,
                'font': {'size': 20}
            },
            height=400,
            font={'color': "darkblue", 'family': "Arial"}
        )
        
        return fig
    
    def create_top_tracks_chart(self, df: pd.DataFrame, metric: str, title: str) -> go.Figure:
        """Create bar chart of top tracks by specific metric"""
        top_tracks = df.nlargest(10, metric)
        
        fig = go.Figure(data=[
            go.Bar(
                x=top_tracks[metric],
                y=[f"{row['name'][:25]}..." if len(row['name']) > 25 else row['name'] 
                   for _, row in top_tracks.iterrows()],
                orientation='h',
                marker=dict(
                    color=top_tracks[metric],
                    colorscale='Plasma',
                    showscale=True
                ),
                hovertemplate='<b>%{y}</b><br>%{x:.2f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'font': {'size': 20}
            },
            xaxis_title=metric.title(),
            yaxis_title="Tracks",
            height=500,
            font=dict(size=12)
        )
        
        return fig
    
    def create_comparison_charts(self, df: pd.DataFrame) -> go.Figure:
        """Create comparison charts showing different emotional aspects"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Energy Distribution', 
                'Valence Distribution',
                'Danceability vs Energy',
                'Acousticness vs Instrumentalness'
            )
        )
        
        # Energy histogram
        fig.add_trace(
            go.Histogram(x=df['energy'], nbinsx=20, name='Energy', marker_color='lightgreen'),
            row=1, col=1
        )
        
        # Valence histogram
        fig.add_trace(
            go.Histogram(x=df['valence'], nbinsx=20, name='Valence', marker_color='lightcoral'),
            row=1, col=2
        )
        
        # Danceability vs Energy scatter
        fig.add_trace(
            go.Scatter(
                x=df['energy'], 
                y=df['danceability'],
                mode='markers',
                name='Dance vs Energy',
                marker=dict(color='purple', size=6)
            ),
            row=2, col=1
        )
        
        # Acousticness vs Instrumentalness
        fig.add_trace(
            go.Scatter(
                x=df['acousticness'], 
                y=df['instrumentalness'],
                mode='markers',
                name='Acoustic vs Instrumental',
                marker=dict(color='orange', size=6)
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title={
                'text': "📊 Detailed Musical Analysis",
                'x': 0.5,
                'font': {'size': 20}
            },
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_valence_energy_scatter(self, df: pd.DataFrame) -> go.Figure:
        """Create valence vs energy scatter plot"""
        if 'valence' not in df.columns or 'energy' not in df.columns:
            # Return empty figure
            fig = go.Figure()
            fig.add_annotation(text="Valence/Energy data not available", 
                             xref="paper", yref="paper", x=0.5, y=0.5)
            return fig
        
        fig = go.Figure()
        
        # Add scatter plot
        fig.add_trace(go.Scatter(
            x=df['valence'],
            y=df['energy'],
            mode='markers+text',
            text=df['name'].str[:20] + '...',
            textposition='top center',
            marker=dict(
                size=12,
                color=df['mood_score'] if 'mood_score' in df.columns else 'blue',
                colorscale='RdYlBu_r',
                showscale=True,
                colorbar=dict(title="Mood Score")
            ),
            hovertemplate='<b>%{text}</b><br>Valence: %{x:.2f}<br>Energy: %{y:.2f}<extra></extra>'
        ))
        
        # Add quadrant lines
        fig.add_hline(y=0.5, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=0.5, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Add quadrant labels
        fig.add_annotation(x=0.75, y=0.75, text="Happy & Energetic", showarrow=False, bgcolor="rgba(255,255,255,0.8)")
        fig.add_annotation(x=0.25, y=0.75, text="Sad & Energetic", showarrow=False, bgcolor="rgba(255,255,255,0.8)")
        fig.add_annotation(x=0.75, y=0.25, text="Happy & Calm", showarrow=False, bgcolor="rgba(255,255,255,0.8)")
        fig.add_annotation(x=0.25, y=0.25, text="Sad & Calm", showarrow=False, bgcolor="rgba(255,255,255,0.8)")
        
        fig.update_layout(
            title="🎭 Valence vs Energy Distribution",
            xaxis_title="Valence (Positivity)",
            yaxis_title="Energy Level",
            height=500
        )
        
        return fig
    
    def create_audio_features_radar(self, mood_summary: Dict) -> go.Figure:
        """Create radar chart for audio features"""
        features = ['Energy', 'Valence', 'Danceability']
        values = [
            mood_summary.get('avg_energy', 0.5),
            mood_summary.get('avg_valence', 0.5), 
            mood_summary.get('avg_danceability', 0.5)
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=features,
            fill='toself',
            name='Your Music Profile',
            line_color='rgba(50, 205, 50, 0.8)',
            fillcolor='rgba(50, 205, 50, 0.2)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title="🎵 Audio Features Profile",
            height=400
        )
        
        return fig
    
    def create_audio_features_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Create heatmap of audio features correlation"""
        features = ['valence', 'energy', 'danceability']
        available_features = [f for f in features if f in df.columns]
        
        if len(available_features) < 2:
            fig = go.Figure()
            fig.add_annotation(text="Insufficient data for correlation analysis", 
                             xref="paper", yref="paper", x=0.5, y=0.5)
            return fig
        
        # Calculate correlation matrix
        corr_matrix = df[available_features].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate="%{text}",
            textfont={"size": 12},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="🔥 Feature Correlation Heatmap",
            height=400
        )
        
        return fig
    
    def create_track_timeline(self, df: pd.DataFrame) -> go.Figure:
        """Create timeline of tracks with mood scores"""
        fig = go.Figure()
        
        # Add mood score line
        fig.add_trace(go.Scatter(
            x=list(range(len(df))),
            y=df['mood_score'] if 'mood_score' in df.columns else [0.5]*len(df),
            mode='lines+markers',
            name='Mood Score',
            line=dict(color='blue', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{text}</b><br>Mood Score: %{y:.2f}<extra></extra>',
            text=df['name']
        ))
        
        # Add energy line
        if 'energy' in df.columns:
            fig.add_trace(go.Scatter(
                x=list(range(len(df))),
                y=df['energy'],
                mode='lines+markers',
                name='Energy',
                line=dict(color='red', width=2),
                marker=dict(size=6)
            ))
        
        fig.update_layout(
            title="📈 Track Mood Timeline",
            xaxis_title="Track Number",
            yaxis_title="Score (0-1)",
            height=400,
            hovermode='x unified'
        )
        
        return fig
