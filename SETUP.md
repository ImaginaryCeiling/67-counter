# 67 Counter Rankings System

A complete system for tracking hand crossing performance with real-time rankings and web interface.

## Features

- **Hand Tracking**: Real-time hand crossing detection using MediaPipe
- **User Accounts**: Username-based tracking for competitive rankings
- **JSON Storage**: Local data storage in `crossing_results.json`
- **Flask API**: RESTful API for rankings and statistics
- **Next.js Frontend**: Beautiful web interface for viewing rankings
- **Auto Sync**: Automatic synchronization between JSON and database

## Quick Start

### 1. Install Python Dependencies

```bash
pip install opencv-python mediapipe numpy requests
```

### 2. Run the Hand Tracking Counter

```bash
python hand_crossing_counter.py
```

- Enter your username when prompted
- Position hands in front of camera
- Cross your hands to increase count
- Press 's' to save results
- Press 'r' to reset counter
- Press 'q' to quit

### 3. Start the Flask API (Optional - for web rankings)

```bash
cd api
pip install -r requirements.txt
python app.py
```

API will be available at `http://localhost:5000`

**API Endpoints:**
- `GET /api/rankings` - Overall leaderboard
- `GET /api/rankings/user/{username}` - User statistics
- `GET /api/stats` - Global statistics
- `POST /api/submit` - Submit new session
- `GET /api/health` - Health check

### 4. Launch the Web Interface (Optional)

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to view the rankings website.

## System Architecture

```
Python Script → JSON File → Flask API → SQLite DB → Next.js Frontend
     ↓              ↓           ↓           ↓            ↓
  Captures      Stores       Serves      Queries    Displays
   Data         Locally      API        Database   Rankings
```

## File Structure

```
67-counter/
├── hand_crossing_counter.py   # Main tracking script
├── crossing_results.json      # Local data storage
├── requirements.txt           # Python dependencies
├── api/
│   ├── app.py                # Flask API server
│   ├── requirements.txt      # API dependencies
│   └── rankings.db           # SQLite database
├── frontend/
│   ├── app/
│   │   └── page.tsx         # Main rankings page
│   ├── package.json
│   └── ...
└── README.md
```

## How It Works

1. **Data Collection**: Python script captures hand crossing events and stores in JSON
2. **API Layer**: Flask server reads JSON, syncs to SQLite, provides REST endpoints
3. **Web Interface**: Next.js frontend fetches data from API and displays rankings
4. **Real-time Updates**: Each session automatically submits to API if available

## Development

### Adding New Features

- **New API endpoints**: Edit `api/app.py`
- **Frontend components**: Edit `frontend/app/page.tsx`
- **Tracking logic**: Edit `hand_crossing_counter.py`

### Database Schema

```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    total_crossings INTEGER NOT NULL,
    counts_per_minute REAL NOT NULL,
    session_duration_seconds REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## Troubleshooting

### Common Issues

1. **Camera not working**: Check privacy settings, quit other camera apps
2. **API connection failed**: Make sure Flask server is running on port 5000
3. **No rankings showing**: Ensure you've saved at least one session with 's' key
4. **Frontend not loading**: Check if Next.js dev server is running on port 3000

### Required Permissions

- **Camera access** for hand tracking
- **Network access** for API communication

## Competition Features

- **Best Rate/Minute**: Highest crossing rate achieved
- **Best Total**: Most crossings in a single session
- **Average Performance**: Consistency across sessions
- **Session Count**: Total number of attempts

## Future Enhancements

- User profiles with avatars
- Session replay and analysis
- Real-time multiplayer competitions
- Mobile app support
- Advanced statistics and charts