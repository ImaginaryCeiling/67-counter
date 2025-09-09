#!/usr/bin/env python3
"""
Flask API for 67 Counter Rankings - Vercel Serverless Version
Provides endpoints for rankings, user stats, and session data.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import tempfile
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=['*'], allow_headers=['Content-Type'], methods=['GET', 'POST'])

# Use in-memory storage for serverless
data_store = []

def load_actual_data():
    """Load actual data from crossing_results.json if available."""
    global data_store
    if not data_store:
        # Real data from your crossing_results.json
        data_store = [
            {
                "username": "ural",
                "timestamp": "2025-09-08 10:13:23",
                "total_crossings": 37,
                "counts_per_minute": 165.2,
                "session_duration_seconds": 13.4
            },
            {
                "username": "isaac",
                "timestamp": "2025-09-08 12:13:40",
                "total_crossings": 81,
                "counts_per_minute": 67.0,
                "session_duration_seconds": 74.2
            },
            {
                "username": "sibi",
                "timestamp": "2025-09-08 13:00:19",
                "total_crossings": 58,
                "counts_per_minute": 119.0,
                "session_duration_seconds": 29.3
            },
            {
                "username": "arham",
                "timestamp": "2025-09-08 13:08:33",
                "total_crossings": 61,
                "counts_per_minute": 202.8,
                "session_duration_seconds": 18.1
            },
            {
                "username": "arnav",
                "timestamp": "2025-09-08 10:00:09",
                "total_crossings": 21,
                "counts_per_minute": 107.3,
                "session_duration_seconds": 11.7
            },
            {
                "username": "arnav",
                "timestamp": "2025-09-08 10:07:36",
                "total_crossings": 18,
                "counts_per_minute": 99.4,
                "session_duration_seconds": 10.9
            },
            {
                "username": "ural",
                "timestamp": "2025-09-08 10:13:28",
                "total_crossings": 37,
                "counts_per_minute": 124.1,
                "session_duration_seconds": 17.9
            },
            {
                "username": "arav",
                "timestamp": "2025-09-08 10:31:45",
                "total_crossings": 23,
                "counts_per_minute": 97.0,
                "session_duration_seconds": 14.2
            },
            {
                "username": "sid",
                "timestamp": "2025-09-08 10:51:38",
                "total_crossings": 3,
                "counts_per_minute": 16.1,
                "session_duration_seconds": 11.2
            },
            {
                "username": "aiden",
                "timestamp": "2025-09-08 10:51:58",
                "total_crossings": 6,
                "counts_per_minute": 47.6,
                "session_duration_seconds": 7.6
            }
        ]

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/rankings', methods=['GET'])
def get_rankings():
    """Get overall rankings leaderboard."""
    try:
        load_actual_data()
        
        # Group by username and calculate stats
        user_stats = {}
        for session in data_store:
            username = session['username']
            if username not in user_stats:
                user_stats[username] = {
                    'sessions': [],
                    'best_rate': 0,
                    'best_crossings': 0
                }
            
            user_stats[username]['sessions'].append(session)
            user_stats[username]['best_rate'] = max(
                user_stats[username]['best_rate'], 
                session['counts_per_minute']
            )
            user_stats[username]['best_crossings'] = max(
                user_stats[username]['best_crossings'], 
                session['total_crossings']
            )
        
        # Create rankings
        rankings = []
        for username, stats in user_stats.items():
            avg_rate = sum(s['counts_per_minute'] for s in stats['sessions']) / len(stats['sessions'])
            rankings.append({
                "username": username,
                "best_rate": round(stats['best_rate'], 1),
                "best_crossings": stats['best_crossings'],
                "total_sessions": len(stats['sessions']),
                "avg_rate": round(avg_rate, 1)
            })
        
        # Sort by best rate
        rankings.sort(key=lambda x: x['best_rate'], reverse=True)
        
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
        load_actual_data()
        
        user_sessions = [s for s in data_store if s['username'] == username]
        
        if not user_sessions:
            return jsonify({"error": "User not found"}), 404
        
        # Calculate user stats
        best_rate = max(s["counts_per_minute"] for s in user_sessions)
        best_crossings = max(s["total_crossings"] for s in user_sessions)
        avg_rate = sum(s["counts_per_minute"] for s in user_sessions) / len(user_sessions)
        total_sessions = len(user_sessions)
        
        return jsonify({
            "username": username,
            "stats": {
                "best_rate": round(best_rate, 1),
                "best_crossings": best_crossings,
                "avg_rate": round(avg_rate, 1),
                "total_sessions": total_sessions
            },
            "sessions": user_sessions
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_global_stats():
    """Get global statistics."""
    try:
        load_actual_data()
        
        if not data_store:
            return jsonify({
                "total_sessions": 0,
                "total_users": 0,
                "global_best_rate": 0,
                "global_avg_rate": 0,
                "global_best_crossings": 0
            })
        
        total_sessions = len(data_store)
        total_users = len(set(s['username'] for s in data_store))
        global_best_rate = max(s['counts_per_minute'] for s in data_store)
        global_avg_rate = sum(s['counts_per_minute'] for s in data_store) / len(data_store)
        global_best_crossings = max(s['total_crossings'] for s in data_store)
        
        return jsonify({
            "total_sessions": total_sessions,
            "total_users": total_users,
            "global_best_rate": round(global_best_rate, 1),
            "global_avg_rate": round(global_avg_rate, 1),
            "global_best_crossings": global_best_crossings
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/submit', methods=['POST'])
def submit_session():
    """Submit a new session."""
    try:
        data = request.get_json()
        
        required_fields = ['username', 'total_crossings', 'counts_per_minute', 'session_duration_seconds']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400
        
        session_data = {
            'username': data['username'],
            'timestamp': data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'total_crossings': data['total_crossings'],
            'counts_per_minute': data['counts_per_minute'],
            'session_duration_seconds': data['session_duration_seconds']
        }
        
        data_store.append(session_data)
        
        return jsonify({"message": "Session submitted successfully"}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel expects the Flask app to be available as 'app'
if __name__ == '__main__':
    app.run(debug=True)