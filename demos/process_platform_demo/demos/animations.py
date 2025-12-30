"""
Algorithm Animations for Process Mining Demo
Provides animated visualizations to show how algorithms work step-by-step

Features:
1. Animated DFG Building - Watch edges appear as we discover transitions
2. Animated Token Replay - See tokens flow through the process for conformance
3. Animated Prediction - Watch feature importance and predictions update
4. Animated Simulation - Cases flowing through process resources
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict
import networkx as nx


def create_animated_dfg(event_log: pd.DataFrame, 
                        duration_ms: int = 100) -> go.Figure:
    """
    Create an animated Directly-Follows Graph showing how edges are discovered.
    
    Args:
        event_log: DataFrame with case_id, activity, timestamp
        duration_ms: Duration per frame in milliseconds
    
    Returns:
        Plotly Figure with animation
    """
    # Build transition data
    transitions = []
    activities = set()
    
    for case_id, case_events in event_log.groupby('case_id'):
        case_events = case_events.sort_values('timestamp')
        acts = case_events['activity'].tolist()
        
        for i in range(len(acts) - 1):
            transitions.append((acts[i], acts[i + 1]))
            activities.add(acts[i])
            activities.add(acts[i + 1])
    
    # Create positions using simple layout
    activities = list(activities)
    n = len(activities)
    positions = {}
    for i, act in enumerate(activities):
        angle = 2 * np.pi * i / n
        positions[act] = (np.cos(angle), np.sin(angle))
    
    # Build frames showing progressive edge discovery
    frames = []
    edge_counts = defaultdict(int)
    
    for i, (src, tgt) in enumerate(transitions[:50]):  # Limit frames
        edge_counts[(src, tgt)] += 1
        
        # Create edge traces
        edge_x, edge_y = [], []
        edge_weights = []
        
        for (s, t), count in edge_counts.items():
            x0, y0 = positions[s]
            x1, y1 = positions[t]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_weights.append(count)
        
        # Create node trace
        node_x = [positions[act][0] for act in activities]
        node_y = [positions[act][1] for act in activities]
        
        frame = go.Frame(
            data=[
                go.Scatter(
                    x=edge_x, y=edge_y,
                    mode='lines',
                    line=dict(width=1, color='#667eea'),
                    hoverinfo='none'
                ),
                go.Scatter(
                    x=node_x, y=node_y,
                    mode='markers+text',
                    marker=dict(size=30, color='#764ba2'),
                    text=[a[:10] for a in activities],
                    textposition='top center',
                    textfont=dict(size=10),
                    hoverinfo='text',
                    hovertext=activities
                )
            ],
            name=str(i),
            layout=go.Layout(
                title=f"DFG Building: {i+1}/{min(50, len(transitions))} edges discovered"
            )
        )
        frames.append(frame)
    
    # Create initial figure
    fig = go.Figure(
        data=[
            go.Scatter(x=[], y=[], mode='lines'),
            go.Scatter(
                x=[positions[a][0] for a in activities],
                y=[positions[a][1] for a in activities],
                mode='markers+text',
                marker=dict(size=30, color='#764ba2'),
                text=[a[:10] for a in activities],
                textposition='top center'
            )
        ],
        layout=go.Layout(
            title="Animated Directly-Follows Graph Discovery",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    y=1.15,
                    x=0.5,
                    xanchor="center",
                    buttons=[
                        dict(label="▶ Play",
                             method="animate",
                             args=[None, {"frame": {"duration": duration_ms, "redraw": True},
                                         "fromcurrent": True,
                                         "transition": {"duration": 50}}]),
                        dict(label="⏸ Pause",
                             method="animate",
                             args=[[None], {"frame": {"duration": 0, "redraw": False},
                                           "mode": "immediate",
                                           "transition": {"duration": 0}}])
                    ]
                )
            ],
            sliders=[{
                "active": 0,
                "steps": [{"args": [[f.name], {"frame": {"duration": duration_ms, "redraw": True},
                                              "mode": "immediate",
                                              "transition": {"duration": 50}}],
                          "label": str(k),
                          "method": "animate"}
                         for k, f in enumerate(frames)],
                "x": 0.1, "len": 0.8, "y": -0.05,
                "currentvalue": {"prefix": "Edge: ", "visible": True, "xanchor": "center"},
            }]
        ),
        frames=frames
    )
    
    return fig


def create_animated_token_replay(event_log: pd.DataFrame,
                                 reference_path: List[str]) -> go.Figure:
    """
    Create animated token-based replay for conformance checking.
    Shows tokens moving through activities.
    
    Args:
        event_log: DataFrame with case_id, activity, timestamp
        reference_path: Expected sequence of activities
    
    Returns:
        Plotly Figure with animation
    """
    # Get unique cases
    cases = event_log.groupby('case_id').apply(
        lambda x: x.sort_values('timestamp')['activity'].tolist()
    ).tolist()[:10]  # Limit to 10 cases
    
    # Create positions for activities (horizontal layout)
    n = len(reference_path)
    positions = {act: (i, 0) for i, act in enumerate(reference_path)}
    
    frames = []
    
    # Create frames for each step
    max_steps = max(len(case) for case in cases)
    
    for step in range(max_steps + 1):
        # Track token positions
        token_x, token_y = [], []
        token_colors = []
        
        for case_idx, case in enumerate(cases):
            if step < len(case):
                activity = case[step]
                if activity in positions:
                    x, y = positions[activity]
                    token_x.append(x)
                    token_y.append(y - case_idx * 0.3)
                    
                    # Check conformance
                    if step < len(reference_path) and activity == reference_path[step]:
                        token_colors.append('#4CAF50')  # Green - conformant
                    else:
                        token_colors.append('#FF5722')  # Red - deviation
        
        # Create node trace (activities)
        node_x = [positions[act][0] for act in reference_path]
        node_y = [0] * len(reference_path)
        
        frame = go.Frame(
            data=[
                # Activity nodes
                go.Scatter(
                    x=node_x, y=node_y,
                    mode='markers+text',
                    marker=dict(size=40, color='#764ba2', symbol='square'),
                    text=[a[:15] for a in reference_path],
                    textposition='top center',
                    textfont=dict(size=9),
                ),
                # Tokens
                go.Scatter(
                    x=token_x, y=token_y,
                    mode='markers',
                    marker=dict(size=15, color=token_colors, symbol='circle'),
                    hoverinfo='text',
                    hovertext=[f"Case {i+1}" for i in range(len(token_x))]
                )
            ],
            name=str(step),
            layout=go.Layout(
                title=f"Token Replay: Step {step+1}/{max_steps} - {len(token_x)} active cases"
            )
        )
        frames.append(frame)
    
    # Initial figure
    fig = go.Figure(
        data=[
            go.Scatter(
                x=[positions[act][0] for act in reference_path],
                y=[0] * len(reference_path),
                mode='markers+text',
                marker=dict(size=40, color='#764ba2', symbol='square'),
                text=[a[:15] for a in reference_path],
                textposition='top center'
            ),
            go.Scatter(x=[], y=[], mode='markers')
        ],
        layout=go.Layout(
            title="Animated Token-Based Replay for Conformance Checking",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-4, 2]),
            updatemenus=[
                dict(
                    type="buttons", showactive=False, y=1.15, x=0.5, xanchor="center",
                    buttons=[
                        dict(label="▶ Play", method="animate",
                             args=[None, {"frame": {"duration": 500, "redraw": True},
                                         "fromcurrent": True}]),
                        dict(label="⏸ Pause", method="animate",
                             args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}])
                    ]
                )
            ]
        ),
        frames=frames
    )
    
    return fig


def create_animated_feature_importance(feature_names: List[str],
                                       iterations: int = 20) -> go.Figure:
    """
    Create animated bar chart showing feature importance growing during training.
    
    Args:
        feature_names: List of feature names
        iterations: Number of training iterations to animate
    
    Returns:
        Plotly Figure with animation
    """
    np.random.seed(42)
    
    # Generate simulated importance growth
    final_importance = np.random.dirichlet(np.ones(len(feature_names))) * 100
    
    frames = []
    for i in range(iterations):
        progress = (i + 1) / iterations
        # Importance grows with some noise
        current = final_importance * progress * (1 + np.random.randn(len(feature_names)) * 0.1 * (1 - progress))
        current = np.clip(current, 0, 100)
        
        frame = go.Frame(
            data=[go.Bar(
                x=feature_names,
                y=current,
                marker_color='#667eea',
                text=[f"{v:.1f}%" for v in current],
                textposition='outside'
            )],
            name=str(i),
            layout=go.Layout(
                title=f"ML Training Progress: Iteration {i+1}/{iterations}"
            )
        )
        frames.append(frame)
    
    fig = go.Figure(
        data=[go.Bar(x=feature_names, y=[0] * len(feature_names), marker_color='#667eea')],
        layout=go.Layout(
            title="Animated Feature Importance During Training",
            yaxis=dict(range=[0, max(final_importance) * 1.2], title="Importance %"),
            updatemenus=[
                dict(
                    type="buttons", showactive=False, y=1.15, x=0.5, xanchor="center",
                    buttons=[
                        dict(label="▶ Train", method="animate",
                             args=[None, {"frame": {"duration": 200, "redraw": True}}]),
                        dict(label="⏸ Pause", method="animate",
                             args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}])
                    ]
                )
            ]
        ),
        frames=frames
    )
    
    return fig


def create_animated_simulation_flow(n_cases: int = 20,
                                    activities: List[str] = None) -> go.Figure:
    """
    Create animated visualization of cases flowing through process.
    
    Args:
        n_cases: Number of cases to simulate
        activities: List of activity names
    
    Returns:
        Plotly Figure with animation
    """
    if activities is None:
        activities = ["Order", "Credit Check", "Warehouse", "Ship", "Invoice", "Payment"]
    
    np.random.seed(42)
    
    # Generate case positions over time
    frames = []
    case_positions = {i: 0 for i in range(n_cases)}
    case_speeds = {i: np.random.uniform(0.3, 1.0) for i in range(n_cases)}
    
    n_steps = 50
    n_activities = len(activities)
    
    for step in range(n_steps):
        # Move cases forward
        for case_id in range(n_cases):
            if case_positions[case_id] < n_activities - 1:
                case_positions[case_id] += case_speeds[case_id] * 0.15
        
        # Create scatter for cases
        case_x = [case_positions[i] for i in range(n_cases)]
        case_y = [i * 0.5 for i in range(n_cases)]
        colors = ['#4CAF50' if pos >= n_activities - 1 else '#667eea' for pos in case_x]
        
        frame = go.Frame(
            data=[
                # Activity boxes
                go.Bar(
                    x=list(range(len(activities))),
                    y=[n_cases * 0.5 + 2] * len(activities),
                    marker_color='#764ba2',
                    opacity=0.3,
                    width=0.8,
                    text=activities,
                    textposition='inside',
                    hoverinfo='text'
                ),
                # Cases
                go.Scatter(
                    x=case_x, y=case_y,
                    mode='markers',
                    marker=dict(size=12, color=colors, symbol='circle'),
                    hoverinfo='text',
                    hovertext=[f"Case {i+1}" for i in range(n_cases)]
                )
            ],
            name=str(step),
            layout=go.Layout(
                title=f"Simulation: {sum(1 for p in case_x if p >= n_activities-1)}/{n_cases} cases completed"
            )
        )
        frames.append(frame)
    
    fig = go.Figure(
        data=[
            go.Bar(x=list(range(len(activities))), y=[n_cases * 0.5 + 2] * len(activities),
                   marker_color='#764ba2', opacity=0.3, text=activities, textposition='inside'),
            go.Scatter(x=[], y=[], mode='markers')
        ],
        layout=go.Layout(
            title="Animated Process Simulation - Cases Flowing Through Activities",
            showlegend=False,
            xaxis=dict(ticktext=activities, tickvals=list(range(len(activities))), title="Activity"),
            yaxis=dict(showticklabels=False, title="Cases"),
            updatemenus=[
                dict(
                    type="buttons", showactive=False, y=1.15, x=0.5, xanchor="center",
                    buttons=[
                        dict(label="▶ Simulate", method="animate",
                             args=[None, {"frame": {"duration": 100, "redraw": True}}]),
                        dict(label="⏸ Pause", method="animate",
                             args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}])
                    ]
                )
            ]
        ),
        frames=frames
    )
    
    return fig


def create_cycle_time_animation(event_log: pd.DataFrame) -> go.Figure:
    """
    Create animated histogram showing cycle time distribution building up.
    
    Args:
        event_log: DataFrame with case_id, activity, timestamp
    
    Returns:
        Plotly Figure with animation
    """
    # Calculate cycle times
    cycle_times = event_log.groupby('case_id')['timestamp'].agg(
        lambda x: (x.max() - x.min()).total_seconds() / 3600
    ).values
    
    # Sort for animation
    cycle_times_sorted = np.sort(cycle_times)
    
    frames = []
    step_size = max(1, len(cycle_times_sorted) // 30)
    
    for i in range(step_size, len(cycle_times_sorted) + 1, step_size):
        current_data = cycle_times_sorted[:i]
        
        frame = go.Frame(
            data=[go.Histogram(
                x=current_data,
                nbinsx=20,
                marker_color='#667eea',
                opacity=0.7
            )],
            name=str(i),
            layout=go.Layout(
                title=f"Cycle Time Distribution: {i}/{len(cycle_times)} cases analyzed"
            )
        )
        frames.append(frame)
    
    fig = go.Figure(
        data=[go.Histogram(x=[], nbinsx=20, marker_color='#667eea')],
        layout=go.Layout(
            title="Animated Cycle Time Distribution",
            xaxis=dict(title="Cycle Time (hours)", range=[0, max(cycle_times) * 1.1]),
            yaxis=dict(title="Frequency"),
            updatemenus=[
                dict(
                    type="buttons", showactive=False, y=1.15, x=0.5, xanchor="center",
                    buttons=[
                        dict(label="▶ Analyze", method="animate",
                             args=[None, {"frame": {"duration": 150, "redraw": True}}]),
                        dict(label="⏸ Pause", method="animate",
                             args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}])
                    ]
                )
            ]
        ),
        frames=frames
    )
    
    return fig
