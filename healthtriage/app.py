"""
Streamlit web application for healthcare provider inbox triage.
"""
import os
import tempfile
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from healthtriage.database import Database
from healthtriage.processor import MessageProcessor
from healthtriage.schemas import Message, TriagedMessage
from healthtriage.triage import MessageTriager
from healthtriage.utils import (create_triage_summary_chart,
                               create_triage_timeline_chart,
                               format_datetime, get_date_range_from_messages,
                               get_message_alert_color)


def main():
    """Main Streamlit application."""
    # Page config
    st.set_page_config(
        page_title="Healthcare Provider Inbox Triage",
        page_icon="🏥",
        layout="wide"
    )
    
    # Initialize database
    db = Database()
    
    # Initialize the message triager
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found in environment variables. Please set the OPENAI_API_KEY environment variable.")
        st.stop()
    
    triager = MessageTriager(api_key=api_key)
    
    # App title and introduction
    st.title("Healthcare Provider Inbox Triage")
    st.markdown("""
    This application uses Natural Language Processing to automatically classify and prioritize 
    patient messages, helping healthcare providers focus on the most urgent communications.
    """)
    
    # Application tabs
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Upload Messages", "Triage Information"])
    
    # Tab 1: Dashboard
    with tab1:
        show_dashboard(db)
    
    # Tab 2: Upload Messages
    with tab2:
        upload_messages(db, triager)
    
    # Tab 3: Triage Information
    with tab3:
        show_triage_info(triager)


def show_dashboard(db: Database):
    """Show the main dashboard with triaged messages.
    
    Args:
        db: Database instance
    """
    # Get all triaged messages
    all_messages = db.get_all_triaged_messages()
    
    if not all_messages:
        st.info("No triaged messages found. Upload messages in the 'Upload Messages' tab to get started.")
        return
    
    # Create filter section
    st.subheader("Filter Messages")
    
    col1, col2, col3 = st.columns(3)
    
    # Date range filter
    min_date, max_date = get_date_range_from_messages(all_messages)
    with col1:
        start_date = st.date_input("From", min_date.date(), min_value=min_date.date(), max_value=max_date.date())
    with col2:
        end_date = st.date_input("To", max_date.date(), min_value=min_date.date(), max_value=max_date.date())
    
    # Triage category filter
    with col3:
        categories = db.get_triage_categories()
        selected_category = st.selectbox("Triage Category", ["All"] + categories)
    
    # Convert dates to datetime objects for filtering
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Apply filters
    if selected_category == "All":
        filtered_messages = db.get_triaged_messages_by_filter(
            start_date=start_datetime,
            end_date=end_datetime
        )
    else:
        filtered_messages = db.get_triaged_messages_by_filter(
            start_date=start_datetime,
            end_date=end_datetime,
            triage_category=selected_category
        )
    
    # Dashboard metrics
    st.subheader("Dashboard")
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        urgent_count = sum(1 for m in filtered_messages if m.triage_level == 5)
        st.metric("Urgent Clinical", urgent_count)
    
    with col2:
        clinical_count = sum(1 for m in filtered_messages if m.triage_level == 4)
        st.metric("Clinical", clinical_count)
    
    with col3:
        prescription_count = sum(1 for m in filtered_messages if m.triage_level == 3)
        st.metric("Prescription", prescription_count)
    
    with col4:
        admin_count = sum(1 for m in filtered_messages if m.triage_level == 2)
        st.metric("Administrative", admin_count)
    
    with col5:
        info_count = sum(1 for m in filtered_messages if m.triage_level == 1)
        st.metric("Informational", info_count)
    
    # Display charts
    chart1, chart2 = st.columns(2)
    
    with chart1:
        summary_chart = create_triage_summary_chart(filtered_messages)
        st.plotly_chart(summary_chart, use_container_width=True)
    
    with chart2:
        timeline_chart = create_triage_timeline_chart(filtered_messages)
        st.plotly_chart(timeline_chart, use_container_width=True)
    
    # Display messages
    st.subheader(f"Messages ({len(filtered_messages)})")
    
    if not filtered_messages:
        st.info("No messages match the selected filters.")
        return
    
    # Group messages by triage level for display
    messages_by_level = {}
    for level in range(5, 0, -1):  # 5 to 1 in descending order
        level_messages = [m for m in filtered_messages if m.triage_level == level]
        if level_messages:
            messages_by_level[level] = level_messages
    
    # Create expandable sections for each triage level
    for level, messages in messages_by_level.items():
        # Map level to category name
        level_names = {
            5: "URGENT_CLINICAL",
            4: "CLINICAL",
            3: "PRESCRIPTION",
            2: "ADMINISTRATIVE",
            1: "INFORMATIONAL"
        }
        
        category_name = level_names.get(level, f"Level {level}")
        color = get_message_alert_color(level)
        
        # Create expandable section
        with st.expander(f"{category_name} ({len(messages)})", expanded=(level == 5)):
            # Display each message in this category
            for msg in messages:
                # Create message card with custom styling
                message_container = st.container()
                message_container.markdown(f"""
                <div style="border-left: 5px solid {color}; padding-left: 10px; margin-bottom: 20px;">
                    <h4 style="margin: 0;">{msg.subject}</h4>
                    <p style="color: gray; margin: 0;">{format_datetime(msg.datetime)}</p>
                    <p style="margin-top: 10px;">{msg.message}</p>
                </div>
                """, unsafe_allow_html=True)


def upload_messages(db: Database, triager: MessageTriager):
    """Handle message uploads and triage.
    
    Args:
        db: Database instance
        triager: Message triager instance
    """
    st.subheader("Upload Messages")
    st.markdown("Upload a CSV file containing inbox messages to triage. The CSV should have the following columns: `message_id`, `subject`, `message`, `datetime`.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file:
        try:
            # Save to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Process the CSV file
            processor = MessageProcessor()
            messages = processor.load_messages_from_csv(tmp_path)
            
            # Clean up the temporary file
            os.unlink(tmp_path)
            
            # Display message count
            st.success(f"Successfully loaded {len(messages)} messages from CSV.")
            
            # Insert messages into the database
            db.insert_messages(messages)
            
            # Get untriaged messages
            untriaged_messages = db.get_untriaged_messages()
            
            if not untriaged_messages:
                st.info("All messages have already been triaged.")
                return
            
            st.write(f"Found {len(untriaged_messages)} messages that need to be triaged.")
            
            # Triage button
            if st.button("Triage Messages"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Process messages in batches to show progress
                total_messages = len(untriaged_messages)
                
                for i, message in enumerate(untriaged_messages):
                    # Update progress
                    progress = int((i / total_messages) * 100)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing message {i+1} of {total_messages}...")
                    
                    # Triage message
                    triaged_message = triager.triage_message(message)
                    
                    # Insert into database
                    db.insert_triaged_message(triaged_message)
                
                # Complete progress
                progress_bar.progress(100)
                status_text.text("Triage complete!")
                
                st.success(f"Successfully triaged {total_messages} messages.")
                st.info("Switch to the Dashboard tab to view results.")
            
        except Exception as e:
            st.error(f"Error processing CSV file: {str(e)}")


def show_triage_info(triager: MessageTriager):
    """Show information about the triage classification system.
    
    Args:
        triager: Message triager instance
    """
    st.subheader("Triage Classification System")
    
    # Get triage description from triager
    triage_description = triager.get_triage_description()
    st.markdown(triage_description)
    
    # Display triage level colors
    st.subheader("Triage Level Colors")
    
    cols = st.columns(5)
    
    with cols[0]:
        st.markdown("""
        <div style="background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px; text-align: center;">
            <strong>URGENT_CLINICAL</strong><br>Level 5
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown("""
        <div style="background-color: #f39c12; color: white; padding: 10px; border-radius: 5px; text-align: center;">
            <strong>CLINICAL</strong><br>Level 4
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown("""
        <div style="background-color: #3498db; color: white; padding: 10px; border-radius: 5px; text-align: center;">
            <strong>PRESCRIPTION</strong><br>Level 3
        </div>
        """, unsafe_allow_html=True)
    
    with cols[3]:
        st.markdown("""
        <div style="background-color: #2ecc71; color: white; padding: 10px; border-radius: 5px; text-align: center;">
            <strong>ADMINISTRATIVE</strong><br>Level 2
        </div>
        """, unsafe_allow_html=True)
    
    with cols[4]:
        st.markdown("""
        <div style="background-color: #95a5a6; color: white; padding: 10px; border-radius: 5px; text-align: center;">
            <strong>INFORMATIONAL</strong><br>Level 1
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
