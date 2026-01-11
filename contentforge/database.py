"""
Database Manager for ContentForge AI
SQLite local database for content history and templates
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from .config import DATABASE_PATH

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    """Get database connection, creating database if needed."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Content history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            network TEXT NOT NULL,
            content_type TEXT NOT NULL,
            topic TEXT NOT NULL,
            generated_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Templates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            network TEXT NOT NULL,
            content_type TEXT NOT NULL,
            template_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Knowledge base table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            UNIQUE(category, key)
        )
    """)
    
    # Network stats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS network_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            network TEXT NOT NULL,
            content_type TEXT NOT NULL,
            generation_count INTEGER DEFAULT 0,
            last_used TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


def save_content(network: str, content_type: str, topic: str, content: str) -> int:
    """Save generated content to history."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO content_history (network, content_type, topic, generated_content)
        VALUES (?, ?, ?, ?)
    """, (network, content_type, topic, content))
    
    content_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Update stats
    update_network_stats(network, content_type)
    
    return content_id


def get_content_history(limit: int = 50) -> List[Dict]:
    """Get recent content history."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM content_history 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def update_network_stats(network: str, content_type: str):
    """Update network usage statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO network_stats (network, content_type, generation_count, last_used)
        VALUES (?, ?, 1, ?)
        ON CONFLICT(network, content_type) DO UPDATE SET
            generation_count = generation_count + 1,
            last_used = ?
    """, (network, content_type, datetime.now(), datetime.now()))
    
    conn.commit()
    conn.close()


def get_network_stats() -> List[Dict]:
    """Get network usage statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT network, SUM(generation_count) as total
        FROM network_stats
        GROUP BY network
        ORDER BY total DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# Initialize database on import
init_database()
