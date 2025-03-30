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
    
    # Define the possible triage categories (independent of urgency)
    TRIAGE_CATEGORIES = [
        "CLINICAL",      # Clinical/medical issues
        "PRESCRIPTION",  # Medication and prescription related
        "ADMINISTRATIVE", # Admin issues like scheduling, records
        "INFORMATIONAL"   # General information, updates
    ]
    
    # Define the urgency levels (1-5, with 5 being most urgent)
    URGENCY_LEVELS = {
        "IMMEDIATE": 5,   # Needs immediate attention
        "URGENT": 4,      # Needs urgent attention
        "PRIORITY": 3,    # Higher than normal priority
        "ROUTINE": 2,     # Normal/routine priority
        "LOW": 1          # Low priority/no action required
    }
    
    def __init__(self, api_key: str = ""):
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
This system independently classifies incoming healthcare messages by:
1. Message category (what the message is about)
2. Urgency level (how quickly it needs attention)

## Message Categories

### CLINICAL
Messages related to clinical or medical concerns:
- Symptoms or health concerns
- Test results and their interpretation
- Follow-up on previous treatments
- Questions about medical conditions

### PRESCRIPTION
Messages specifically about medications and prescriptions:
- Prescription refill requests
- Questions about medication dosage or instructions
- Side effect inquiries
- Request for new medications

### ADMINISTRATIVE
Non-clinical administrative requests:
- Appointment scheduling or changes
- Referral requests
- Insurance and billing questions
- Medical record requests

### INFORMATIONAL
General information or updates:
- General healthcare inquiries
- Thank you messages
- Status updates without specific requests
- Educational material requests

## Urgency Levels

### Level 5 (IMMEDIATE)
Requires immediate attention, potentially life-threatening:
- Severe symptoms like chest pain or difficulty breathing
- Severe adverse reactions
- Situations requiring emergency intervention

### Level 4 (URGENT)
Urgent but not immediately life-threatening:
- Concerning symptoms that need prompt attention
- Problems requiring same-day response
- Significant health issues

### Level 3 (PRIORITY)
Higher priority than routine matters:
- Issues that should be addressed within 24-48 hours
- Problems that might worsen if left unattended
- Questions needing fairly prompt responses

### Level 2 (ROUTINE)
Normal/routine priority:
- Standard follow-up communication
- Questions that can be answered within normal timeframes
- Routine administrative matters

### Level 1 (LOW)
Low priority or no action required:
- Thank you messages
- FYI-type updates
- General information that doesn't require a response

## Implementation
Each message receives both a category and an urgency level, allowing staff to prioritize messages by urgency while also organizing workflow by category.
"""
        return description
    
    def triage_message(self, message: Message) -> TriagedMessage:
        """Classify a message into a triage category and assign an urgency level using NLP.
        
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
                urgency_level=result["urgency_level"],
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
                urgency_level=3,  # Medium urgency as a safe default
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
        categories = ", ".join(self.TRIAGE_CATEGORIES)
        urgency_levels = ", ".join([f"{k} ({v})" for k, v in self.URGENCY_LEVELS.items()])
        
        return f"""You are an expert healthcare message triage assistant. Your task is to independently analyze two aspects of each message:

1. CATEGORY: Classify the message into one of the following categories: {categories}
2. URGENCY LEVEL: Assign an urgency level from 1-5, with 5 being most urgent

Category definitions:
- CLINICAL: Medical issues, symptoms, test results, health concerns
- PRESCRIPTION: Medication-related issues, refill requests, dosage questions
- ADMINISTRATIVE: Appointments, billing, records, referrals
- INFORMATIONAL: General information, thank you notes, updates

Urgency level definitions:
- 5 (IMMEDIATE): Potentially life-threatening, requires immediate attention
- 4 (URGENT): Urgent but not immediately life-threatening
- 3 (PRIORITY): Higher priority than routine, should be addressed soon
- 2 (ROUTINE): Normal priority, can be handled within standard timeframes
- 1 (LOW): Low priority, informational only

Analyze both the subject and message content to determine both aspects.
Respond with a JSON object containing:
1. "category": The assigned category (one of the categories listed above)
2. "urgency_level": A number between 1 and 5 representing urgency
3. "confidence": A number between 0 and 1 indicating your confidence in the classification
4. "reasoning": A brief explanation of why you assigned this category and urgency level

Always err on the side of caution - if in doubt between two urgency levels, choose the higher one."""
    
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

Determine both the category and urgency level of this message."""