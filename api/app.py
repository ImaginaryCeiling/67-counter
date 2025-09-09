#!/usr/bin/env python3
"""
Flask API for 67 Counter Rankings
Provides endpoints for rankings, user stats, and session data.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:3001'], 
     allow_headers=['Content-Type'], 
     methods=['GET', 'POST'])  # Enable CORS for Next.js frontend

DATABASE_PATH = 'rankings.db'
JSON_FILE_PATH = '../crossing_results.json'

def init_database():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            total_crossings INTEGER NOT NULL,
            counts_per_minute REAL NOT NULL,
            session_duration_seconds REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_username ON sessions (username)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp ON sessions (timestamp)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_counts_per_minute ON sessions (counts_per_minute)
    ''')
    
    conn.commit()
    conn.close()

def sync_from_json():
    """Sync data from JSON file to database."""
    if not os.path.exists(JSON_FILE_PATH):
        return
    
    try:
        with open(JSON_FILE_PATH, 'r') as f:
            data = json.load(f)
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Clear existing data (simple approach for now)
        cursor.execute('DELETE FROM sessions')
        
        # Insert all data from JSON
        for session in data:
            cursor.execute('''
                INSERT INTO sessions (username, timestamp, total_crossings, 
                                    counts_per_minute, session_duration_seconds)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session['username'],
                session['timestamp'],
                session['total_crossings'],
                session['counts_per_minute'],
                session['session_duration_seconds']
            ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error syncing from JSON: {e}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/rankings', methods=['GET'])
def get_rankings():
    """Get overall rankings leaderboard."""
    try:
        # Sync from JSON file first
        sync_from_json()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get top sessions by counts per minute
        cursor.execute('''
            SELECT username, MAX(counts_per_minute) as best_rate,
                   MAX(total_crossings) as best_crossings,
                   COUNT(*) as total_sessions,
                   AVG(counts_per_minute) as avg_rate
            FROM sessions
            GROUP BY username
            ORDER BY best_rate DESC
            LIMIT 50
        ''')
        
        rankings = []
        for row in cursor.fetchall():
            rankings.append({
                "username": row[0],
                "best_rate": round(row[1], 1),
                "best_crossings": row[2],
                "total_sessions": row[3],
                "avg_rate": round(row[4], 1)
            })
        
        conn.close()
        
        return jsonify({
            "rankings": rankings,
            "total_users": len(rankings)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rankings/user/<username>', methods=['GET'])
def get_user_stats(username: str):
    """Get detailed stats for a specific user."""
    try:
        sync_from_json()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get user's session history
        cursor.execute('''
            SELECT timestamp, total_crossings, counts_per_minute, session_duration_seconds
            FROM sessions
            WHERE username = ?
            ORDER BY timestamp DESC
        ''', (username,))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "timestamp": row[0],
                "total_crossings": row[1],
                "counts_per_minute": row[2],
                "session_duration_seconds": row[3]
            })
        
        if not sessions:
            conn.close()
            return jsonify({"error": "User not found"}), 404
        
        # Calculate user stats
        best_rate = max(s["counts_per_minute"] for s in sessions)
        best_crossings = max(s["total_crossings"] for s in sessions)
        avg_rate = sum(s["counts_per_minute"] for s in sessions) / len(sessions)
        total_sessions = len(sessions)
        
        conn.close()
        
        return jsonify({
            "username": username,
            "stats": {
                "best_rate": round(best_rate, 1),
                "best_crossings": best_crossings,
                "avg_rate": round(avg_rate, 1),
                "total_sessions": total_sessions
            },
            "sessions": sessions
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_global_stats():
    """Get global statistics."""
    try:
        sync_from_json()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Global stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(DISTINCT username) as total_users,
                MAX(counts_per_minute) as global_best_rate,
                AVG(counts_per_minute) as global_avg_rate,
                MAX(total_crossings) as global_best_crossings
            FROM sessions
        ''')
        
        row = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            "total_sessions": row[0],
            "total_users": row[1],
            "global_best_rate": round(row[2] if row[2] else 0, 1),
            "global_avg_rate": round(row[3] if row[3] else 0, 1),
            "global_best_crossings": row[4] if row[4] else 0
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/submit', methods=['POST'])
def submit_session():
    """Submit a new session (alternative to JSON file)."""
    try:
        data = request.get_json()
        
        required_fields = ['username', 'total_crossings', 'counts_per_minute', 'session_duration_seconds']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (username, timestamp, total_crossings, 
                                counts_per_minute, session_duration_seconds)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['username'],
            data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            data['total_crossings'],
            data['counts_per_minute'],
            data['session_duration_seconds']
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Session submitted successfully"}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_database()
    print("🚀 Starting 67 Counter API...")
    print("📊 API will be available at https://67-counter-api.vercel.app")
    print("🔄 Database will sync from crossing_results.json on each request")
    app.run(debug=True, host='0.0.0.0', port=5002)