"""
Database operations for the HealthTriage application.
"""
import os
import sqlite3
from datetime import datetime
from typing import List, Optional

from healthtriage.schemas import Message, TriagedMessage


class Database:
    """Handle all database operations for the HealthTriage application."""
    
    def __init__(self, db_path: str = "triage.db"):
        """Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        
        # Create the tables if they don't exist
        # (SQLite will create the database file if it doesn't exist)
        self._create_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a connection to the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables(self) -> None:
        """Create the necessary tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            datetime TEXT NOT NULL
        )
        ''')
        
        # Create triaged_messages table with separated urgency_level and category
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS triaged_messages (
            message_id TEXT PRIMARY KEY,
            triage_category TEXT NOT NULL,
            urgency_level INTEGER NOT NULL,
            confidence REAL NOT NULL,
            processed_at TEXT NOT NULL,
            FOREIGN KEY (message_id) REFERENCES messages (message_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_message(self, message: Message) -> None:
        """Insert a message into the database.
        
        Args:
            message: The message to insert
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR REPLACE INTO messages (message_id, subject, message, datetime) VALUES (?, ?, ?, ?)",
            (message.message_id, message.subject, message.message, message.datetime.isoformat())
        )
        
        conn.commit()
        conn.close()
    
    def insert_messages(self, messages: List[Message]) -> None:
        """Insert multiple messages into the database.
        
        Args:
            messages: List of messages to insert
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        for message in messages:
            cursor.execute(
                "INSERT OR REPLACE INTO messages (message_id, subject, message, datetime) VALUES (?, ?, ?, ?)",
                (message.message_id, message.subject, message.message, message.datetime.isoformat())
            )
        
        conn.commit()
        conn.close()
    
    def insert_triaged_message(self, triaged_message: TriagedMessage) -> None:
        """Insert a triaged message into the database.
        
        Args:
            triaged_message: The triaged message to insert
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # First, insert the message if it doesn't exist
        cursor.execute(
            "INSERT OR IGNORE INTO messages (message_id, subject, message, datetime) VALUES (?, ?, ?, ?)",
            (triaged_message.message_id, triaged_message.subject, triaged_message.message, 
             triaged_message.datetime.isoformat())
        )
        
        # Then insert the triage information
        processed_at = triaged_message.processed_at or datetime.now()
        cursor.execute(
            """INSERT OR REPLACE INTO triaged_messages 
               (message_id, triage_category, urgency_level, confidence, processed_at) 
               VALUES (?, ?, ?, ?, ?)""",
            (triaged_message.message_id, triaged_message.triage_category, 
             triaged_message.urgency_level, triaged_message.confidence, processed_at.isoformat())
        )
        
        conn.commit()
        conn.close()
    
    def get_all_triaged_messages(self) -> List[TriagedMessage]:
        """Get all triaged messages from the database.
        
        Returns:
            List of triaged messages
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT m.message_id, m.subject, m.message, m.datetime, 
               t.triage_category, t.urgency_level, t.confidence, t.processed_at
        FROM messages m
        JOIN triaged_messages t ON m.message_id = t.message_id
        ORDER BY t.urgency_level DESC, m.datetime DESC
        """)
        
        results = cursor.fetchall()
        triaged_messages = []
        
        for row in results:
            try:
                # Handle potential datetime parsing issues
                try:
                    msg_datetime = datetime.fromisoformat(row['datetime'])
                except ValueError:
                    # Try to handle different date formats
                    msg_datetime = datetime.strptime(row['datetime'], "%Y-%m-%dT%H:%M:%S")
                
                try:
                    processed_at = datetime.fromisoformat(row['processed_at'])
                except ValueError:
                    # Try to handle different date formats
                    processed_at = datetime.strptime(row['processed_at'], "%Y-%m-%dT%H:%M:%S")
                
                triaged_message = TriagedMessage(
                    message_id=row['message_id'],
                    subject=row['subject'],
                    message=row['message'],
                    datetime=msg_datetime,
                    triage_category=row['triage_category'],
                    urgency_level=row['urgency_level'],
                    confidence=row['confidence'],
                    processed_at=processed_at
                )
                triaged_messages.append(triaged_message)
            except Exception as e:
                print(f"Error processing message {row['message_id']}: {e}")
                # Continue with other messages even if one fails
                continue
        
        conn.close()
        return triaged_messages
    
    def get_triaged_messages_by_filter(self, 
                                     start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None,
                                     triage_category: Optional[str] = None,
                                     urgency_level: Optional[int] = None) -> List[TriagedMessage]:
        """Get triaged messages filtered by criteria.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            triage_category: Optional triage category for filtering
            urgency_level: Optional urgency level for filtering
            
        Returns:
            List of filtered triaged messages
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT m.message_id, m.subject, m.message, m.datetime, 
               t.triage_category, t.urgency_level, t.confidence, t.processed_at
        FROM messages m
        JOIN triaged_messages t ON m.message_id = t.message_id
        WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND m.datetime >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND m.datetime <= ?"
            params.append(end_date.isoformat())
        
        if triage_category:
            query += " AND t.triage_category = ?"
            params.append(triage_category)
        
        if urgency_level is not None:
            query += " AND t.urgency_level = ?"
            params.append(urgency_level)
        
        query += " ORDER BY t.urgency_level DESC, m.datetime DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        triaged_messages = []
        
        for row in results:
            try:
                # Handle potential datetime parsing issues
                try:
                    msg_datetime = datetime.fromisoformat(row['datetime'])
                except ValueError:
                    # Try to handle different date formats
                    msg_datetime = datetime.strptime(row['datetime'], "%Y-%m-%dT%H:%M:%S")
                
                try:
                    processed_at = datetime.fromisoformat(row['processed_at'])
                except ValueError:
                    # Try to handle different date formats
                    processed_at = datetime.strptime(row['processed_at'], "%Y-%m-%dT%H:%M:%S")
                
                triaged_message = TriagedMessage(
                    message_id=row['message_id'],
                    subject=row['subject'],
                    message=row['message'],
                    datetime=msg_datetime,
                    triage_category=row['triage_category'],
                    urgency_level=row['urgency_level'],
                    confidence=row['confidence'],
                    processed_at=processed_at
                )
                triaged_messages.append(triaged_message)
            except Exception as e:
                print(f"Error processing filtered message {row['message_id']}: {e}")
                # Continue with other messages even if one fails
                continue
        
        conn.close()
        return triaged_messages
    
    def get_untriaged_messages(self) -> List[Message]:
        """Get messages that haven't been triaged yet.
        
        Returns:
            List of untriaged messages
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT m.message_id, m.subject, m.message, m.datetime
        FROM messages m
        LEFT JOIN triaged_messages t ON m.message_id = t.message_id
        WHERE t.message_id IS NULL
        """)
        
        results = cursor.fetchall()
        messages = []
        
        for row in results:
            try:
                # Handle potential datetime parsing issues
                try:
                    msg_datetime = datetime.fromisoformat(row['datetime'])
                except ValueError:
                    # Try to handle different date formats
                    msg_datetime = datetime.strptime(row['datetime'], "%Y-%m-%dT%H:%M:%S")
                
                message = Message(
                    message_id=row['message_id'],
                    subject=row['subject'],
                    message=row['message'],
                    datetime=msg_datetime
                )
                messages.append(message)
            except Exception as e:
                print(f"Error processing untriaged message {row['message_id']}: {e}")
                # Continue with other messages even if one fails
                continue
        
        conn.close()
        return messages
    
    def get_triage_categories(self) -> List[str]:
        """Get all unique triage categories from the database.
        
        Returns:
            List of unique triage categories
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT triage_category FROM triaged_messages")
        results = cursor.fetchall()
        
        categories = [row['triage_category'] for row in results]
        conn.close()
        
        return categories
    
    def get_urgency_levels(self) -> List[int]:
        """Get all unique urgency levels from the database.
        
        Returns:
            List of unique urgency levels
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT urgency_level FROM triaged_messages ORDER BY urgency_level")
        results = cursor.fetchall()
        
        levels = [row['urgency_level'] for row in results]
        conn.close()
        
        return levels