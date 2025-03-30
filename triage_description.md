# Healthcare Message Triage Classification System

## Overview
This document describes the message triage classification system used for healthcare provider inbox management. The system automatically classifies incoming patient messages into five priority categories, assigning each an urgency level to help healthcare providers prioritize their response efficiently.

## Classification Schema

### Urgency Levels
Messages are assigned an urgency level from 1 to 5, with higher numbers indicating greater urgency:
- Level 5: Highest urgency, requires immediate attention
- Level 4: High urgency, should be addressed promptly
- Level 3: Medium urgency, should be addressed within a normal timeframe
- Level 2: Low urgency, can be addressed when time permits
- Level 1: Minimal urgency, informational only

### Triage Categories

#### 1. URGENT_CLINICAL (Level 5)
Messages that require immediate clinical attention due to potential serious health concerns.

**Examples:**
- Reports of severe symptoms (chest pain, difficulty breathing, severe bleeding)
- Suspected serious adverse medication reactions
- Post-procedure complications
- Suicidal ideation or acute mental health crises
- Severe pain reports
- Potential stroke or heart attack symptoms

**Reasoning:**
These messages indicate potentially life-threatening conditions where delayed response could result in serious harm to the patient. The clinical team should be alerted immediately.

#### 2. CLINICAL (Level 4)
Messages that require clinical attention but not immediate intervention.

**Examples:**
- New or worsening symptoms that aren't immediately life-threatening
- Abnormal test results requiring follow-up
- Chronic condition management concerns
- Non-emergent mental health concerns
- Moderate pain reports
- Follow-up questions about diagnoses

**Reasoning:**
These messages require clinical expertise but don't represent immediate emergencies. They should be addressed promptly but don't require instantaneous response.

#### 3. PRESCRIPTION (Level 3)
Messages related to medications and prescriptions.

**Examples:**
- Prescription refill requests
- Questions about medication dosage or instructions
- Side effect inquiries
- Request for new medications
- Questions about medication interactions
- Insurance authorization for medications

**Reasoning:**
Medication-related messages have their own category due to their frequency and the specialized workflow often required for prescription handling.

#### 4. ADMINISTRATIVE (Level 2)
Non-urgent administrative requests or questions.

**Examples:**
- Appointment scheduling or changes
- Referral requests
- Insurance and billing questions
- Medical record requests
- Forms completion requests
- General administrative inquiries

**Reasoning:**
These messages don't require clinical expertise and can typically be handled by administrative staff rather than clinical providers.

#### 5. INFORMATIONAL (Level 1)
General information or updates that require minimal action.

**Examples:**
- General healthcare inquiries
- Thank you messages
- Status updates without specific requests
- Educational material requests
- Newsletter responses
- General feedback

**Reasoning:**
These messages require the least urgency as they don't involve specific patient care needs or clinical questions.

## Implementation Notes

### Classification Process
Each message undergoes Natural Language Processing (NLP) analysis to determine its appropriate category. The system considers:

1. **Content Analysis:**
   - Identification of medical terminology
   - Recognition of symptom descriptions
   - Detection of urgent phrases or keywords
   - Analysis of requested actions

2. **Contextual Factors:**
   - Time sensitivity indicated in the message
   - Patient history (when available)
   - Previous message patterns
   - Explicit urgency indicators

3. **Safety Protocol:**
   - The system applies a "safety margin" by escalating borderline cases to the higher urgency category
   - Messages with ambiguous intent but potentially serious implications are elevated in priority

### Confidence Scoring
Each classification includes a confidence score (0-1) indicating the system's certainty in the categorization. Messages with low confidence scores may be flagged for human review.

## Benefits of This Schema

1. **Clinical Safety:** Prioritizes patient safety by ensuring urgent clinical matters receive immediate attention.

2. **Workflow Efficiency:** Allows healthcare providers to focus on clinical matters while administrative staff can handle non-clinical requests.

3. **Resource Allocation:** Enables appropriate staffing based on message volume within each category.

4. **Response Time Management:** Facilitates appropriate response times based on message urgency.

5. **Audit and Quality Improvement:** Categorized messages allow for analysis of communication patterns and potential workflow improvements.

## System Limitations

1. The system cannot replace clinical judgment and should serve as a tool to assist healthcare providers.

2. Classification accuracy depends on the quality and clarity of the patient's message.

3. The system may not fully account for patient-specific contextual factors unless they are explicitly mentioned in the message.

4. Regular review and refinement of the classification algorithm is necessary to maintain optimal performance.
