"""
Utility functions for the HealthTriage application.
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from healthtriage.schemas import TriagedMessage


def get_date_range_from_messages(messages: List[TriagedMessage]) -> Tuple[datetime, datetime]:
    """Get the minimum and maximum dates from a list of messages.
    
    Args:
        messages: List of triaged messages
        
    Returns:
        Tuple of (min_date, max_date)
    """
    if not messages:
        # Default to last 30 days if no messages
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return start_date, end_date
    
    dates = [msg.datetime for msg in messages]
    return min(dates), max(dates)


def create_triage_summary_chart(messages: List[TriagedMessage]) -> go.Figure:
    """Create a summary chart of triaged messages by category.
    
    Args:
        messages: List of triaged messages
        
    Returns:
        Plotly figure object
    """
    if not messages:
        # Return empty figure if no messages
        return go.Figure()
    
    # Count messages by category
    category_counts = {}
    for msg in messages:
        category_counts[msg.triage_category] = category_counts.get(msg.triage_category, 0) + 1
    
    # Create DataFrame for plotting
    df = pd.DataFrame([
        {"Category": category, "Count": count} 
        for category, count in category_counts.items()
    ])
    
    # Define color scheme for triage levels
    color_map = {
        "URGENT_CLINICAL": "#e74c3c",    # Red
        "CLINICAL": "#f39c12",           # Orange
        "PRESCRIPTION": "#3498db",       # Blue
        "ADMINISTRATIVE": "#2ecc71",     # Green
        "INFORMATIONAL": "#95a5a6"       # Gray
    }
    
    # Create bar chart
    fig = px.bar(
        df, 
        x="Category", 
        y="Count",
        color="Category",
        color_discrete_map=color_map,
        title="Message Distribution by Triage Category",
        labels={"Count": "Number of Messages", "Category": "Triage Category"}
    )
    
    # Improve styling
    fig.update_layout(
        xaxis_title="Triage Category",
        yaxis_title="Number of Messages",
        plot_bgcolor="white",
        font=dict(family="Arial", size=14)
    )
    
    return fig


def create_triage_timeline_chart(messages: List[TriagedMessage]) -> go.Figure:
    """Create a timeline chart of triaged messages by date.
    
    Args:
        messages: List of triaged messages
        
    Returns:
        Plotly figure object
    """
    if not messages:
        # Return empty figure if no messages
        return go.Figure()
    
    # Create DataFrame with date and category
    data = []
    for msg in messages:
        data.append({
            "Date": msg.datetime.date(),
            "Category": msg.triage_category,
            "Count": 1
        })
    
    df = pd.DataFrame(data)
    df_grouped = df.groupby(["Date", "Category"]).sum().reset_index()
    
    # Define color scheme for triage levels
    color_map = {
        "URGENT_CLINICAL": "#e74c3c",    # Red
        "CLINICAL": "#f39c12",           # Orange
        "PRESCRIPTION": "#3498db",       # Blue
        "ADMINISTRATIVE": "#2ecc71",     # Green
        "INFORMATIONAL": "#95a5a6"       # Gray
    }
    
    # Create line chart
    fig = px.line(
        df_grouped,
        x="Date",
        y="Count",
        color="Category",
        color_discrete_map=color_map,
        title="Message Volume by Date and Category",
        markers=True
    )
    
    # Improve styling
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Messages",
        plot_bgcolor="white",
        font=dict(family="Arial", size=14)
    )
    
    return fig


def get_message_alert_color(triage_level: int) -> str:
    """Get the alert color for a given triage level.
    
    Args:
        triage_level: The triage urgency level (1-5)
        
    Returns:
        CSS color string
    """
    color_map = {
        5: "#e74c3c",  # Red for URGENT_CLINICAL
        4: "#f39c12",  # Orange for CLINICAL
        3: "#3498db",  # Blue for PRESCRIPTION
        2: "#2ecc71",  # Green for ADMINISTRATIVE
        1: "#95a5a6"   # Gray for INFORMATIONAL
    }
    
    return color_map.get(triage_level, "#95a5a6")


def format_datetime(dt: datetime) -> str:
    """Format a datetime object for display.
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted date string
    """
    return dt.strftime("%b %d, %Y %I:%M %p")
