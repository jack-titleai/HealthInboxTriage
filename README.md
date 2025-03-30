# HealthTriage

A healthcare provider inbox triage application using NLP to classify and prioritize messages with an interactive Streamlit dashboard.

## Overview

HealthTriage is a Python application designed to help healthcare providers efficiently manage their patient message inboxes. It uses Natural Language Processing (NLP) to automatically classify incoming messages into priority categories, helping providers focus on the most urgent communications first.

Key features:
- Automated message classification using NLP (powered by OpenAI)
- Interactive dashboard for message management
- Filtering by date and triage category
- Clear visual indicators of message urgency
- Easy message expansion to view full content
- Data persistence via SQLite

## Installation

### Prerequisites
- Python 3.9+
- OpenAI API key

### Setup

1. Clone the repository:
```
git clone https://github.com/yourusername/healthtriage.git
cd healthtriage
```

2. Install the package and dependencies:
```
pip install -e .
```

3. Set your OpenAI API key:
```
export OPENAI_API_KEY="your-api-key-here"
```
Or create a `.env` file in the project root with:
```
OPENAI_API_KEY=your-api-key-here
```

4. Run the application:
```
streamlit run healthtriage/app.py
```

## Usage

### Uploading Messages

1. Navigate to the "Upload Messages" tab
2. Upload a CSV file containing your patient messages with these columns:
   - `message_id`: Unique identifier for each message
   - `subject`: Message subject line
   - `message`: Full message body
   - `datetime`: Timestamp in ISO format (YYYY-MM-DDTHH:MM:SS)
3. Click "Triage Messages" to process and classify the messages

### Viewing the Dashboard

1. Switch to the "Dashboard" tab to see all processed messages
2. Use the date range picker and category filter to narrow down messages
3. Expand message categories to view individual messages
4. Messages are color-coded by urgency level

### Understanding the Classification System

The "Triage Information" tab provides details about the classification categories:

- **URGENT_CLINICAL (Level 5)**: Immediate clinical attention required
- **CLINICAL (Level 4)**: Clinical attention needed but not immediate
- **PRESCRIPTION (Level 3)**: Prescription refill or medication question
- **ADMINISTRATIVE (Level 2)**: Non-urgent administrative request
- **INFORMATIONAL (Level 1)**: General information, no action required

## Code Structure

The application is organized as a Python package with the following structure:

```
healthtriage/
├── __init__.py       # Package initialization
├── app.py            # Main Streamlit application
├── database.py       # Database operations and SQLite interface
├── processor.py      # CSV message loading and processing
├── schemas.py        # Data structures and models
├── triage.py         # NLP message classification with OpenAI
└── utils.py          # Helper functions and visualization tools
```

### Key Components

- **app.py**: Contains the Streamlit interface and user interaction logic
- **database.py**: Manages the SQLite database for message storage and retrieval
- **processor.py**: Handles the parsing and validation of CSV message files
- **triage.py**: Classifies messages using OpenAI's language models
- **schemas.py**: Defines data classes for messages and triaged messages
- **utils.py**: Provides visualization functions and helper utilities

## Customization

### Triage Categories

The triage categories and their corresponding urgency levels are defined in `triage.py`. You can modify these to match your specific healthcare workflow.

### Database Location

By default, the application uses a SQLite database named `triage.db` in the project root. You can specify a different path in the `Database` class initialization.

## Troubleshooting

### Missing Messages in Dashboard

If messages don't appear in the dashboard after uploading and triaging:
- Check the debug information in the sidebar for database stats
- Verify your CSV file has the correct column names and format
- Ensure the datetime values in your CSV are in ISO format

### OpenAI API Issues

If you encounter errors related to the OpenAI API:
- Verify your API key is correctly set
- Check your API account has sufficient quota remaining
- Ensure you have a stable internet connection

## License

This project is licensed under the MIT License - see the LICENSE file for details.

