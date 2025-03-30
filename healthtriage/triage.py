"""
Message triage classification using NLP.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

from openai import OpenAI

from healthtriage.schemas import Message, TriagedMessage


class MessageTriager:
    """Classify and triage healthcare messages using NLP."""
    
    # Define the triage categories and their urgency levels
    TRIAGE_CATEGORIES = {
        "URGENT_CLINICAL": 5,  # Immediate clinical attention required
        "CLINICAL": 4,         # Clinical attention needed but not immediate
        "PRESCRIPTION": 3,     # Prescription refill or medication question
        "ADMINISTRATIVE": 2,   # Non-urgent administrative request
        "INFORMATIONAL": 1     # General information, no action required
    }
    
    def __init__(self, api_key: str = None):
        """Initialize the message triager.
        
        Args:
            api_key: OpenAI API key (defaults to env var)
        """
        # Get the API key from the environment if not provided
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and not found in environment variables")
        
        # Initialize the OpenAI client
        # The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # Do not change this unless explicitly requested by the user
        self.openai_client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"
    
    def get_triage_description(self) -> str:
        """Get a description of the triage classification schema.
        
        Returns:
            Markdown description of the triage schema
        """
        description = """# Healthcare Message Triage Classification System

## Overview
This system classifies incoming healthcare messages into five priority categories, each with an assigned urgency level (1-5, with 5 being the most urgent).

## Triage Categories

### 1. URGENT_CLINICAL (Level 5)
Messages requiring immediate clinical attention. Examples include:
- Reports of severe symptoms (chest pain, difficulty breathing, severe bleeding)
- Adverse medication reactions
- Post-procedure complications
- Suicidal ideation or acute mental health crises

### 2. CLINICAL (Level 4)
Messages requiring clinical attention but not immediate intervention. Examples include:
- New or worsening symptoms that aren't life-threatening
- Abnormal test results requiring follow-up
- Chronic condition management concerns
- Non-emergent mental health concerns

### 3. PRESCRIPTION (Level 3)
Messages related to medications and prescriptions. Examples include:
- Prescription refill requests
- Questions about medication dosage or instructions
- Side effect inquiries
- Request for new medications

### 4. ADMINISTRATIVE (Level 2)
Non-urgent administrative requests or questions. Examples include:
- Appointment scheduling or changes
- Referral requests
- Insurance and billing questions
- Medical record requests

### 5. INFORMATIONAL (Level 1)
General information or updates that require minimal action. Examples include:
- General healthcare inquiries
- Thank you messages
- Updates without specific requests
- Educational material requests

## Implementation Notes
Each message is analyzed using NLP to determine its appropriate category and assigned the corresponding urgency level. The system considers:
- Type of medical concern mentioned
- Presence of urgent terminology
- Explicit time-sensitivity
- Patient context when available
"""
        return description
    
    def triage_message(self, message: Message) -> TriagedMessage:
        """Classify a message into a triage category using NLP.
        
        Args:
            message: The message to classify
            
        Returns:
            TriagedMessage with classification details
        """
        # Construct prompt for the NLP model
        prompt = self._construct_triage_prompt(message)
        
        # Call OpenAI API to classify the message
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Create a triaged message with the classification
            triaged_message = TriagedMessage(
                message_id=message.message_id,
                subject=message.subject,
                message=message.message,
                datetime=message.datetime,
                triage_category=result["category"],
                triage_level=self.TRIAGE_CATEGORIES[result["category"]],
                confidence=result["confidence"],
                processed_at=datetime.now()
            )
            
            return triaged_message
            
        except Exception as e:
            # In case of error, assign to CLINICAL category as a safe default
            # In a production system, you might want to handle this differently
            print(f"Error triaging message: {e}")
            return TriagedMessage(
                message_id=message.message_id,
                subject=message.subject,
                message=message.message,
                datetime=message.datetime,
                triage_category="CLINICAL",
                triage_level=self.TRIAGE_CATEGORIES["CLINICAL"],
                confidence=0.5,
                processed_at=datetime.now()
            )
    
    def batch_triage_messages(self, messages: List[Message]) -> List[TriagedMessage]:
        """Triage multiple messages in batch.
        
        Args:
            messages: List of messages to triage
            
        Returns:
            List of triaged messages
        """
        return [self.triage_message(message) for message in messages]
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the NLP model.
        
        Returns:
            System prompt explaining the triage task
        """
        categories = ", ".join(self.TRIAGE_CATEGORIES.keys())
        
        return f"""You are an expert healthcare message triage assistant. Your task is to classify incoming patient messages 
into one of the following categories: {categories}.

URGENT_CLINICAL (Level 5): Messages requiring immediate clinical attention (severe symptoms, adverse reactions, etc.)
CLINICAL (Level 4): Messages requiring clinical attention but not immediate intervention (non-urgent symptoms, test results)
PRESCRIPTION (Level 3): Messages related to medications and prescriptions
ADMINISTRATIVE (Level 2): Non-urgent administrative requests (appointments, billing, referrals)
INFORMATIONAL (Level 1): General information or updates requiring minimal action

Analyze both the subject and message content to determine the appropriate category.
Respond with a JSON object containing:
1. "category": The assigned triage category (one of the categories listed above)
2. "confidence": A number between 0 and 1 indicating your confidence in the classification
3. "reasoning": A brief explanation of why you assigned this category

Always err on the side of caution - if in doubt between two categories, choose the higher urgency one."""
    
    def _construct_triage_prompt(self, message: Message) -> str:
        """Construct the prompt for the triage classification.
        
        Args:
            message: The message to classify
            
        Returns:
            Prompt text for the NLP model
        """
        return f"""Please classify the following healthcare message:

Subject: {message.subject}

Message:
{message.message}

Date/Time: {message.datetime.strftime('%Y-%m-%d %H:%M:%S')}

Classify this message into the most appropriate triage category."""
