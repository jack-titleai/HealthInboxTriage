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
    triage_category: str
    triage_level: int
    confidence: float
    processed_at: Optional[datetime] = None
