"""
Process inbox messages from CSV and prepare for triage.
"""
import csv
import os
from datetime import datetime
from typing import List

import pandas as pd

from healthtriage.schemas import Message


class MessageProcessor:
    """Process and load inbox messages from CSV files."""
    
    def __init__(self, csv_path: str = None):
        """Initialize with optional CSV file path.
        
        Args:
            csv_path: Path to the CSV file containing messages
        """
        self.csv_path = csv_path
    
    def load_messages_from_csv(self, csv_path: str = None) -> List[Message]:
        """Load messages from a CSV file.
        
        Args:
            csv_path: Path to the CSV file (overrides the one set in __init__)
            
        Returns:
            List of Message objects
        """
        path = csv_path or self.csv_path
        if not path:
            raise ValueError("CSV file path not provided")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"CSV file not found: {path}")
        
        try:
            # Load the CSV file using pandas
            df = pd.read_csv(path)
            
            # Check for required columns
            required_columns = ['message_id', 'subject', 'message', 'datetime']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"CSV file missing required columns: {', '.join(missing_columns)}")
            
            # Convert to Message objects
            messages = []
            for _, row in df.iterrows():
                # Parse datetime from string
                try:
                    message_datetime = pd.to_datetime(row['datetime'])
                except:
                    # If datetime parsing fails, use current time
                    print(f"Warning: Could not parse datetime for message ID {row['message_id']}, using current time")
                    message_datetime = datetime.now()
                
                # Create Message object
                message = Message(
                    message_id=str(row['message_id']),
                    subject=str(row['subject']),
                    message=str(row['message']),
                    datetime=message_datetime
                )
                messages.append(message)
            
            return messages
            
        except Exception as e:
            raise Exception(f"Error loading messages from CSV: {e}")
    
    def save_messages_to_csv(self, messages: List[Message], output_path: str) -> None:
        """Save messages to a CSV file.
        
        Args:
            messages: List of Message objects to save
            output_path: Path to save the CSV file
        """
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['message_id', 'subject', 'message', 'datetime'])
                
                for message in messages:
                    writer.writerow([
                        message.message_id,
                        message.subject,
                        message.message,
                        message.datetime.isoformat()
                    ])
        except Exception as e:
            raise Exception(f"Error saving messages to CSV: {e}")
