# Healthcare Message Triage Classification System

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

## Implementation Notes

### Classification Process
Each message undergoes Natural Language Processing (NLP) analysis to independently determine both:
1. Its appropriate category (what it's about)
2. Its urgency level (how quickly it needs attention)

The system considers:

1. **Content Analysis:**
   - Identification of medical terminology
   - Recognition of symptom descriptions
   - Detection of urgent phrases or keywords
   - Analysis of requested actions

2. **Contextual Factors:**
   - Time sensitivity indicated in the message
   - Nature of the concern
   - Explicit urgency indicators

3. **Safety Protocol:**
   - The system applies a "safety margin" by escalating borderline cases to the higher urgency level
   - Messages with ambiguous intent but potentially serious implications are elevated in priority

### Confidence Scoring
Each classification includes a confidence score (0-1) indicating the system's certainty in the categorization. Messages with low confidence scores may be flagged for human review.

## Benefits of This Schema

1. **Dual Classification:** Separating category and urgency provides more nuanced triage, allowing a clinical message to be urgent or routine, or an administrative message to be high priority when appropriate.

2. **Workflow Management:** Categories can be used to route messages to appropriate teams (clinical vs. administrative), while urgency levels determine response time priority.

3. **Resource Allocation:** Enables appropriate staffing based on message volume within each category and urgency level.

4. **Response Time Management:** Facilitates appropriate response times based on urgency level regardless of message category.

5. **Audit and Quality Improvement:** Categorized messages allow for analysis of communication patterns and potential workflow improvements.

## System Limitations

1. The system cannot replace clinical judgment and should serve as a tool to assist healthcare providers.

2. Classification accuracy depends on the quality and clarity of the patient's message.

3. The system may not fully account for patient-specific contextual factors unless they are explicitly mentioned in the message.

4. Regular review and refinement of the classification algorithm is necessary to maintain optimal performance.