import json
import sqlite3
from datetime import datetime
from pathlib import Path

class MemorySystem:
    def __init__(self, db_path='reminder_memory.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events_completed (
                id INTEGER PRIMARY KEY,
                event_title TEXT,
                event_type TEXT,
                completed_date TIMESTAMP,
                days_to_complete INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders_ignored (
                id INTEGER PRIMARY KEY,
                reminder_text TEXT,
                ignored_date TIMESTAMP,
                ignored_count INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productivity_patterns (
                id INTEGER PRIMARY KEY,
                hour_of_day INTEGER,
                productivity_score REAL,
                event_type TEXT,
                sample_count INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_reasoning_history (
                id INTEGER PRIMARY KEY,
                query_date TIMESTAMP,
                events_analyzed INTEGER,
                ai_response TEXT,
                user_feedback TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_event_completed(self, event_title, event_type, days_to_complete):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events_completed (event_title, event_type, completed_date, days_to_complete)
            VALUES (?, ?, ?, ?)
        ''', (event_title, event_type, datetime.now(), days_to_complete))
        
        conn.commit()
        conn.close()
    
    def record_reminder_ignored(self, reminder_text):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ignored_count FROM reminders_ignored WHERE reminder_text = ?
        ''', (reminder_text,))
        
        result = cursor.fetchone()
        if result:
            cursor.execute('''
                UPDATE reminders_ignored 
                SET ignored_count = ?, ignored_date = ?
                WHERE reminder_text = ?
            ''', (result[0] + 1, datetime.now(), reminder_text))
        else:
            cursor.execute('''
                INSERT INTO reminders_ignored (reminder_text, ignored_date, ignored_count)
                VALUES (?, ?, ?)
            ''', (reminder_text, datetime.now(), 1))
        
        conn.commit()
        conn.close()
    
    def record_productivity_pattern(self, hour_of_day, event_type, productivity_score):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sample_count, productivity_score FROM productivity_patterns 
            WHERE hour_of_day = ? AND event_type = ?
        ''', (hour_of_day, event_type))
        
        result = cursor.fetchone()
        if result:
            new_count = result[1] + 1
            new_avg = (result[0] + productivity_score) / new_count
            cursor.execute('''
                UPDATE productivity_patterns
                SET productivity_score = ?, sample_count = ?
                WHERE hour_of_day = ? AND event_type = ?
            ''', (new_avg, new_count, hour_of_day, event_type))
        else:
            cursor.execute('''
                INSERT INTO productivity_patterns (hour_of_day, event_type, productivity_score, sample_count)
                VALUES (?, ?, ?, ?)
            ''', (hour_of_day, event_type, productivity_score, 1))
        
        conn.commit()
        conn.close()
    
    def get_user_profile(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM events_completed')
        events_completed = cursor.fetchone()[0]
        
        cursor.execute('SELECT event_type, COUNT(*) FROM events_completed GROUP BY event_type')
        event_types = dict(cursor.fetchall())
        
        cursor.execute('''
            SELECT AVG(days_to_complete) FROM events_completed
        ''')
        avg_days = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT reminder_text, ignored_count FROM reminders_ignored ORDER BY ignored_count DESC LIMIT 5
        ''')
        frequently_ignored = cursor.fetchall()
        
        cursor.execute('''
            SELECT hour_of_day, productivity_score FROM productivity_patterns ORDER BY productivity_score DESC LIMIT 5
        ''')
        peak_hours = cursor.fetchall()
        
        conn.close()
        
        return {
            'events_completed': events_completed,
            'event_types_distribution': event_types,
            'average_days_to_complete': round(avg_days, 1),
            'frequently_ignored_reminders': frequently_ignored,
            'peak_productivity_hours': peak_hours
        }
    
    def export_memory(self, filename='memory_export.json'):
        profile = self.get_user_profile()
        
        with open(filename, 'w') as f:
            json.dump(profile, f, indent=2)
        
        return filename