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
    
    # Count messages by category and urgency level
    data = []
    for msg in messages:
        data.append({
            "Category": msg.triage_category,
            "Urgency": msg.urgency_level,
            "Count": 1
        })
    
    df = pd.DataFrame(data)
    
    # Get urgency labels for better display
    urgency_labels = {
        5: "5-IMMEDIATE",
        4: "4-URGENT",
        3: "3-PRIORITY",
        2: "2-ROUTINE", 
        1: "1-LOW"
    }
    
    # Map urgency levels to labels
    df["Urgency Label"] = df["Urgency"].map(urgency_labels)
    
    # Group by category and urgency
    df_grouped = df.groupby(["Category", "Urgency", "Urgency Label"]).sum().reset_index()
    
    # Sort by urgency in descending order
    df_grouped = df_grouped.sort_values("Urgency", ascending=False)
    
    # Define color scheme based on urgency levels
    color_map = {
        5: "#e74c3c",  # Red for IMMEDIATE
        4: "#f39c12",  # Orange for URGENT
        3: "#3498db",  # Blue for PRIORITY
        2: "#2ecc71",  # Green for ROUTINE
        1: "#95a5a6"   # Gray for LOW
    }
    
    # Create stacked bar chart
    fig = px.bar(
        df_grouped, 
        x="Category", 
        y="Count",
        color="Urgency Label",
        title="Message Distribution by Category and Urgency Level",
        labels={"Count": "Number of Messages", "Category": "Triage Category"}
    )
    
    # Manually set the color scale to match our urgency levels
    for i, trace in enumerate(fig.data):
        urgency = 5 - i  # Since they're in descending order in the legend
        if urgency in color_map:
            trace.marker.color = color_map[urgency]
    
    # Improve styling
    fig.update_layout(
        xaxis_title="Message Category",
        yaxis_title="Number of Messages",
        plot_bgcolor="white",
        font=dict(family="Arial", size=14),
        legend_title="Urgency Level"
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
            "Urgency": msg.urgency_level,
            "Count": 1
        })
    
    df = pd.DataFrame(data)
    
    # Group by date and category
    df_grouped = df.groupby(["Date", "Category"]).sum().reset_index()
    
    # Get category colors
    # Use a distinct color for each category, separate from urgency colors
    unique_categories = df_grouped["Category"].unique()
    category_colors = px.colors.qualitative.Plotly[:len(unique_categories)]
    color_map = {cat: color for cat, color in zip(unique_categories, category_colors)}
    
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
        font=dict(family="Arial", size=14),
        legend_title="Message Category"
    )
    
    return fig


def get_message_alert_color(urgency_level: int) -> str:
    """Get the alert color for a given urgency level.
    
    Args:
        urgency_level: The urgency level (1-5, with 5 being most urgent)
        
    Returns:
        CSS color string
    """
    color_map = {
        5: "#e74c3c",  # Red for IMMEDIATE
        4: "#f39c12",  # Orange for URGENT
        3: "#3498db",  # Blue for PRIORITY
        2: "#2ecc71",  # Green for ROUTINE
        1: "#95a5a6"   # Gray for LOW
    }
    
    return color_map.get(urgency_level, "#95a5a6")


def format_datetime(dt: datetime) -> str:
    """Format a datetime object for display.
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted date string
    """
    return dt.strftime("%b %d, %Y %I:%M %p")