#!/usr/bin/env python3
"""
Generate Architecture Diagrams for Sahay Platform
Creates technical diagrams for hackathon submission
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_architecture_diagram():
    """Create system architecture diagram using Plotly"""
    
    # Create architecture diagram
    fig = go.Figure()
    
    # Define components and their positions
    components = [
        # Frontend Layer
        {"name": "Multi-Language\nChat Interface", "x": 1, "y": 4, "color": "#E8F4FD", "layer": "Frontend"},
        {"name": "Wellness\nDashboard", "x": 3, "y": 4, "color": "#E8F4FD", "layer": "Frontend"},
        {"name": "Crisis\nIntervention UI", "x": 5, "y": 4, "color": "#E8F4FD", "layer": "Frontend"},
        
        # AI Processing Layer
        {"name": "Gemini AI\n2.5 Flash", "x": 2, "y": 3, "color": "#FFF2CC", "layer": "AI Processing"},
        {"name": "Language\nDetection", "x": 4, "y": 3, "color": "#FFF2CC", "layer": "AI Processing"},
        {"name": "Google Search\nGrounding", "x": 6, "y": 3, "color": "#FFF2CC", "layer": "AI Processing"},
        
        # Data Processing Layer
        {"name": "CSV Data\nProcessor", "x": 1.5, "y": 2, "color": "#E1D5E7", "layer": "Data Processing"},
        {"name": "Privacy Engine\n(K-Anonymity)", "x": 3.5, "y": 2, "color": "#E1D5E7", "layer": "Data Processing"},
        {"name": "Analytics\nEngine", "x": 5.5, "y": 2, "color": "#E1D5E7", "layer": "Data Processing"},
        
        # Data Storage Layer
        {"name": "Students\nCSV", "x": 1, "y": 1, "color": "#D5E8D4", "layer": "Data Storage"},
        {"name": "Wellness\nLogs CSV", "x": 2.5, "y": 1, "color": "#D5E8D4", "layer": "Data Storage"},
        {"name": "AI Interactions\nCSV", "x": 4, "y": 1, "color": "#D5E8D4", "layer": "Data Storage"},
        {"name": "Crisis\nRecords CSV", "x": 5.5, "y": 1, "color": "#D5E8D4", "layer": "Data Storage"},
    ]
    
    # Add components as rectangles
    for comp in components:
        fig.add_shape(
            type="rect",
            x0=comp["x"]-0.4, y0=comp["y"]-0.2,
            x1=comp["x"]+0.4, y1=comp["y"]+0.2,
            fillcolor=comp["color"],
            line=dict(color="black", width=1),
        )
        
        fig.add_annotation(
            x=comp["x"], y=comp["y"],
            text=comp["name"],
            showarrow=False,
            font=dict(size=10, color="black"),
            align="center"
        )
    
    # Add layer labels
    layer_colors = {"Frontend": "#E8F4FD", "AI Processing": "#FFF2CC", 
                   "Data Processing": "#E1D5E7", "Data Storage": "#D5E8D4"}
    
    for i, (layer, color) in enumerate(layer_colors.items()):
        fig.add_annotation(
            x=0.2, y=4-i,
            text=f"<b>{layer}</b>",
            showarrow=False,
            font=dict(size=12, color="black"),
            align="left",
            bgcolor=color,
            bordercolor="black",
            borderwidth=1
        )
    
    # Add arrows showing data flow
    arrows = [
        {"start": (3, 3.8), "end": (3, 3.2)},  # Frontend to AI
        {"start": (3, 2.8), "end": (3, 2.2)},  # AI to Processing
        {"start": (3, 1.8), "end": (3, 1.2)},  # Processing to Storage
    ]
    
    for arrow in arrows:
        fig.add_annotation(
            x=arrow["end"][0], y=arrow["end"][1],
            ax=arrow["start"][0], ay=arrow["start"][1],
            xref="x", yref="y",
            axref="x", ayref="y",
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="red",
        )
    
    fig.update_layout(
        title="Sahay Platform - System Architecture",
        xaxis=dict(range=[0, 7], showgrid=False, showticklabels=False),
        yaxis=dict(range=[0.5, 4.5], showgrid=False, showticklabels=False),
        width=800,
        height=600,
        showlegend=False,
        plot_bgcolor="white"
    )
    
    return fig

def create_process_flow_diagram():
    """Create process flow diagram"""
    
    fig = go.Figure()
    
    # Define process steps
    steps = [
        {"name": "Student Input\n(Multi-Language)", "x": 1, "y": 5},
        {"name": "Language Detection\n(Hindi/Bengali/English)", "x": 3, "y": 5},
        {"name": "Gemini AI Processing\n+ Google Search", "x": 5, "y": 5},
        {"name": "Privacy Layer\n(K-Anonymity)", "x": 3, "y": 3},
        {"name": "CSV Storage\n(Anonymous)", "x": 1, "y": 3},
        {"name": "Analytics Engine\n(Insights)", "x": 5, "y": 3},
        {"name": "Crisis Detection\n& Intervention", "x": 3, "y": 1},
    ]
    
    # Add process boxes
    for step in steps:
        fig.add_shape(
            type="rect",
            x0=step["x"]-0.6, y0=step["y"]-0.3,
            x1=step["x"]+0.6, y1=step["y"]+0.3,
            fillcolor="#F0F8FF",
            line=dict(color="navy", width=2),
        )
        
        fig.add_annotation(
            x=step["x"], y=step["y"],
            text=step["name"],
            showarrow=False,
            font=dict(size=10, color="navy"),
            align="center"
        )
    
    # Add process flow arrows
    flow_arrows = [
        {"start": (1.6, 5), "end": (2.4, 5)},    # Input -> Detection
        {"start": (3.6, 5), "end": (4.4, 5)},    # Detection -> AI
        {"start": (5, 4.7), "end": (3.6, 3.3)},  # AI -> Privacy
        {"start": (2.4, 3), "end": (1.6, 3)},    # Privacy -> Storage
        {"start": (3.6, 3), "end": (4.4, 3)},    # Privacy -> Analytics
        {"start": (3, 2.7), "end": (3, 1.3)},    # Privacy -> Crisis
    ]
    
    for arrow in flow_arrows:
        fig.add_annotation(
            x=arrow["end"][0], y=arrow["end"][1],
            ax=arrow["start"][0], ay=arrow["start"][1],
            xref="x", yref="y",
            axref="x", ayref="y",
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor="darkblue",
        )
    
    fig.update_layout(
        title="Sahay Platform - Process Flow Diagram",
        xaxis=dict(range=[0, 6], showgrid=False, showticklabels=False),
        yaxis=dict(range=[0, 6], showgrid=False, showticklabels=False),
        width=800,
        height=600,
        showlegend=False,
        plot_bgcolor="white"
    )
    
    return fig

def create_language_usage_chart():
    """Create language usage statistics chart"""
    
    # Sample data based on our implementation
    languages = ['English', 'Hindi', 'Bengali']
    usage_data = [45, 35, 20]
    crisis_support = [23, 15, 12]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Language Usage Distribution', 'Crisis Support by Language'),
        specs=[[{"type": "pie"}, {"type": "bar"}]]
    )
    
    # Pie chart for language usage
    fig.add_trace(
        go.Pie(
            labels=languages,
            values=usage_data,
            name="Language Usage",
            marker_colors=['#FF9999', '#66B2FF', '#99FF99']
        ),
        row=1, col=1
    )
    
    # Bar chart for crisis support
    fig.add_trace(
        go.Bar(
            x=languages,
            y=crisis_support,
            name="Crisis Interventions",
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1']
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title="Multi-Language Platform Analytics",
        width=800,
        height=400
    )
    
    return fig

def create_privacy_protection_diagram():
    """Create privacy protection mechanism diagram"""
    
    fig = go.Figure()
    
    # Privacy layers
    privacy_steps = [
        {"name": "Raw Student Data\n(Identifiable)", "x": 1, "y": 4, "color": "#FFE6E6"},
        {"name": "ID Hashing\n(SHA256)", "x": 3, "y": 4, "color": "#FFF2E6"},
        {"name": "K-Anonymity\nGrouping (k=3)", "x": 5, "y": 4, "color": "#F0FFF0"},
        {"name": "Aggregated\nInsights Only", "x": 3, "y": 2, "color": "#E6F3FF"},
    ]
    
    for step in privacy_steps:
        fig.add_shape(
            type="rect",
            x0=step["x"]-0.7, y0=step["y"]-0.4,
            x1=step["x"]+0.7, y1=step["y"]+0.4,
            fillcolor=step["color"],
            line=dict(color="black", width=1),
        )
        
        fig.add_annotation(
            x=step["x"], y=step["y"],
            text=step["name"],
            showarrow=False,
            font=dict(size=11, color="black"),
            align="center"
        )
    
    # Add privacy flow arrows
    privacy_arrows = [
        {"start": (1.7, 4), "end": (2.3, 4)},     # Raw -> Hash
        {"start": (3.7, 4), "end": (4.3, 4)},     # Hash -> K-Anon
        {"start": (5, 3.6), "end": (3.7, 2.4)},   # K-Anon -> Insights
    ]
    
    for arrow in privacy_arrows:
        fig.add_annotation(
            x=arrow["end"][0], y=arrow["end"][1],
            ax=arrow["start"][0], ay=arrow["start"][1],
            xref="x", yref="y",
            axref="x", ayref="y",
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor="green",
        )
    
    fig.update_layout(
        title="Privacy Protection Mechanism",
        xaxis=dict(range=[0, 6], showgrid=False, showticklabels=False),
        yaxis=dict(range=[1, 5], showgrid=False, showticklabels=False),
        width=700,
        height=500,
        showlegend=False,
        plot_bgcolor="white"
    )
    
    return fig

if __name__ == "__main__":
    # Generate all diagrams
    print("Generating architecture diagram...")
    arch_fig = create_architecture_diagram()
    arch_fig.write_image("sahay_architecture.png", width=800, height=600)
    
    print("Generating process flow diagram...")
    flow_fig = create_process_flow_diagram()
    flow_fig.write_image("sahay_process_flow.png", width=800, height=600)
    
    print("Generating language analytics chart...")
    lang_fig = create_language_usage_chart()
    lang_fig.write_image("sahay_language_analytics.png", width=800, height=400)
    
    print("Generating privacy protection diagram...")
    privacy_fig = create_privacy_protection_diagram()
    privacy_fig.write_image("sahay_privacy_protection.png", width=700, height=500)
    
    print("All diagrams generated successfully!")
