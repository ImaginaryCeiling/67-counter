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

def load_demo_data():
    """Load some demo data for the deployment."""
    global data_store
    if not data_store:
        data_store = [
            {
                "username": "demo_user",
                "timestamp": "2025-09-08 10:00:00",
                "total_crossings": 50,
                "counts_per_minute": 75.5,
                "session_duration_seconds": 40.0
            },
            {
                "username": "test_player",
                "timestamp": "2025-09-08 11:00:00", 
                "total_crossings": 35,
                "counts_per_minute": 65.2,
                "session_duration_seconds": 32.0
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
        load_demo_data()
        
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
        load_demo_data()
        
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
        load_demo_data()
        
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