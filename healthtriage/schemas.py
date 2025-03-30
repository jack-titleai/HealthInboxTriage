"""
Schema definitions for the HealthTriage application.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    """Represents a message in the inbox."""
    message_id: str
    subject: str
    message: str
    datetime: datetime
    

@dataclass
class TriagedMessage(Message):
    """Represents a triaged message with classification details."""
    # Category is now independent (e.g., "CLINICAL", "ADMINISTRATIVE", "PRESCRIPTION")
    triage_category: str
    # Urgency level is now independent (1-5 scale, with 5 being most urgent)
    urgency_level: int
    confidence: float
    processed_at: Optional[datetime] = None
