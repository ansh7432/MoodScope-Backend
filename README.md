# 🎵 MoodScope Backend API

A standalone FastAPI backend for analyzing Spotify playlists and providing AI-powered music mood insights. This backend serves the MoodScope frontend and provides real-time playlist analysis.

## ✨ Features

- **🎧 Spotify Integration** - Direct playlist analysis using Spotipy
- **📊 Audio Feature Analysis** - Extract valence, energy, danceability, etc.
- **🤖 AI-Powered Insights** - Generate mood coaching and personality traits
- **⚡ Fast API** - Built with FastAPI for high performance
- **🌐 CORS Enabled** - Ready for frontend integration
- **☁️ Cloud Ready** - Deployed on Railway

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **Language**: Python 3.12+
- **HTTP Server**: Uvicorn
- **Music API**: Spotipy (Spotify Web API)
- **Deployment**: Railway
- **Environment**: python-dotenv

## 🚀 Live API

- **Base URL**: https://moodscale-production.up.railway.app
- **Health Check**: https://moodscale-production.up.railway.app/health
- **API Docs**: https://moodscale-production.up.railway.app/docs

## 📋 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and status |
| `GET` | `/health` | Health check for monitoring |
| `POST` | `/analyze` | Analyze Spotify playlist |
| `GET` | `/demo` | Demo data for testing |
| `GET` | `/docs` | Interactive API documentation |

### Example Usage

#### Analyze Playlist
```bash
curl -X POST "https://moodscale-production.up.railway.app/analyze" \
  -H "Content-Type: application/json" \
  -d '{"playlist_url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"}'
```

#### Health Check
```bash
curl "https://moodscale-production.up.railway.app/health"
```

## 🏁 Local Development

### Prerequisites

- Python 3.12+ installed
- Spotify Developer Account (for API credentials)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ansh7432/moodscope-backend.git
   cd moodscope-backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**:
   ```bash
   export SPOTIPY_CLIENT_ID="your_spotify_client_id"
   export SPOTIPY_CLIENT_SECRET="your_spotify_client_secret"
   ```

5. **Run the server**:
   ```bash
   python -m uvicorn api_bridge:app --host=0.0.0.0 --port=8000 --reload
   ```

6. **Access the API**:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

## 🔧 Configuration Files

### `requirements.txt`
```
fastapi==0.115.6
uvicorn==0.32.1
spotipy==2.25.1
requests==2.32.4
python-dotenv==1.1.1
```

### `Procfile` (Railway)
```
web: python -m uvicorn api_bridge:app --host=0.0.0.0 --port=${PORT:-8000}
```

### `railway.json`
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python -m uvicorn api_bridge:app --host=0.0.0.0 --port=${PORT:-8000}",
    "healthcheckPath": "/health"
  }
}
```

## 📊 Response Format

### Successful Analysis Response
```json
{
  "tracks": [
    {
      "name": "Track Name",
      "artist": "Artist Name",
      "mood_score": 0.75,
      "energy": 0.8,
      "valence": 0.7,
      "danceability": 0.65,
      "acousticness": 0.2,
      "speechiness": 0.1,
      "instrumentalness": 0.0,
      "popularity": 75,
      "mood_category": "Energetic & Happy"
    }
  ],
  "mood_summary": {
    "total_tracks": 50,
    "mood_score": 0.65,
    "avg_energy": 0.68,
    "avg_valence": 0.62,
    "dominant_mood": "Upbeat & Positive",
    "mood_distribution": {
      "Energetic & Happy": 15,
      "Upbeat & Positive": 20,
      "Calm & Content": 10,
      "Melancholic & Introspective": 5
    }
  },
  "ai_insights": {
    "emotional_analysis": "Your playlist shows a balanced mix...",
    "personality_traits": ["Music enthusiast", "Emotionally aware"],
    "recommendations": ["Explore similar artists", "Try mood-based playlists"],
    "mood_coaching": "Your music choice reflects..."
  },
  "playlist_name": "My Awesome Playlist"
}
```

## 🌐 CORS Configuration

The API is configured to accept requests from:
- `https://moodscope-ai.vercel.app` (Production frontend)
- `http://localhost:3000-3002` (Local development)
- All Vercel deployment URLs

## 🚀 Deployment

### Railway Deployment

This backend is deployed on Railway with:

1. **Automatic deployments** from GitHub
2. **Environment variables** for Spotify API
3. **Health checks** on `/health` endpoint
4. **Custom domain** available

### Environment Variables (Railway)

Set these in your Railway dashboard:

```env
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
```

## 🔒 Security Features

- **Environment variable protection** for API keys
- **CORS properly configured** for security
- **Input validation** using Pydantic models
- **Error handling** with proper HTTP status codes

## 📈 Performance

- **Fast response times** with async FastAPI
- **Efficient Spotify API usage** with batched requests
- **Lightweight deployment** with minimal dependencies
- **Auto-scaling** on Railway platform

## 🤝 Frontend Integration

This backend pairs with the MoodScope Next.js frontend:
- **Frontend Repo**: https://github.com/ansh7432/MoodScope
- **Live Frontend**: https://moodscope-ai.vercel.app

## 🐛 Error Handling

The API provides detailed error messages for:
- Invalid Spotify URLs
- Private/inaccessible playlists
- Network connectivity issues
- Rate limiting from Spotify API

## 📝 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: https://moodscale-production.up.railway.app/docs
- **ReDoc**: https://moodscale-production.up.railway.app/redoc

## 🏆 Features

✅ **Real Spotify Analysis** - Direct integration with Spotify Web API  
✅ **AI Insights** - Generated mood coaching and personality traits  
✅ **Fast Performance** - Optimized for quick response times  
✅ **Production Ready** - Deployed and monitored on Railway  
✅ **Well Documented** - Comprehensive API docs and examples  
✅ **Error Resilient** - Graceful handling of edge cases  

## 📄 License

This project is licensed under the MIT License.

---

**Power your music mood analysis with MoodScope Backend** 🎵⚡

Built with FastAPI and deployed on Railway for optimal performance.
