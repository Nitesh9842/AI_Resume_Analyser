"""
Visualization Module
Create charts and visual components for the app
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict


def create_match_score_chart(score: float) -> go.Figure:
    """
    Create a circular gauge chart for match score
    """
    # Determine color based on score
    if score >= 80:
        color = "green"
    elif score >= 60:
        color = "orange"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Job Match Score", 'font': {'size': 24, 'color': 'white'}},
        delta={'reference': 70, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(255, 0, 0, 0.3)'},
                {'range': [50, 75], 'color': 'rgba(255, 165, 0, 0.3)'},
                {'range': [75, 100], 'color': 'rgba(0, 255, 0, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Arial"},
        height=300,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def create_skills_pie_chart(matched_count: int, missing_count: int) -> go.Figure:
    """
    Create a pie chart showing matched vs missing skills
    """
    labels = ['Matched Skills', 'Missing Skills']
    values = [matched_count, missing_count]
    colors = ['#00D9FF', '#FF6B6B']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textfont_size=14
    )])
    
    fig.update_layout(
        title_text="Skills Distribution",
        title_font_size=20,
        title_font_color="white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        height=350,
        showlegend=True,
        legend=dict(
            font=dict(color="white"),
            bgcolor="rgba(0,0,0,0)"
        )
    )
    
    return fig


def create_score_breakdown_chart(scores: Dict[str, float]) -> go.Figure:
    """
    Create a horizontal bar chart for score breakdown
    """
    categories = list(scores.keys())
    values = list(scores.values())
    
    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation='h',
        marker=dict(
            color=values,
            colorscale='Viridis',
            showscale=True
        ),
        text=[f'{v:.1f}%' for v in values],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Score Breakdown",
        title_font_size=20,
        title_font_color="white",
        xaxis_title="Score (%)",
        yaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        height=300,
        xaxis=dict(range=[0, 100], gridcolor='rgba(255,255,255,0.2)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.2)')
    )
    
    return fig


def create_keyword_density_chart(keywords: Dict[str, int]) -> go.Figure:
    """
    Create a word cloud style bar chart for keyword density
    """
    if not keywords:
        return go.Figure()
    
    # Sort by frequency
    sorted_keywords = dict(sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:15])
    
    fig = go.Figure(go.Bar(
        x=list(sorted_keywords.values()),
        y=list(sorted_keywords.keys()),
        orientation='h',
        marker=dict(
            color=list(sorted_keywords.values()),
            colorscale='Blues',
        ),
        text=list(sorted_keywords.values()),
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Top Keywords",
        title_font_size=20,
        title_font_color="white",
        xaxis_title="Frequency",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        height=400,
        xaxis=dict(gridcolor='rgba(255,255,255,0.2)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.2)')
    )
    
    return fig


# Test code - only runs when executed directly
if __name__ == "__main__":
    print("Testing Visualization Module...")
    print("=" * 50)
    
    # Test 1: Match Score Chart
    print("\n1. Creating Match Score Chart...")
    score_chart = create_match_score_chart(75.5)
    print(f"   ✓ Chart created successfully")
    
    # Test 2: Skills Pie Chart
    print("\n2. Creating Skills Pie Chart...")
    pie_chart = create_skills_pie_chart(matched_count=8, missing_count=3)
    print(f"   ✓ Chart created successfully")
    
    # Test 3: Score Breakdown Chart
    print("\n3. Creating Score Breakdown Chart...")
    sample_scores = {
        'Overall Score': 75.5,
        'Semantic Similarity': 68.3,
        'Skill Match': 80.0,
        'Experience Match': 70.0
    }
    breakdown_chart = create_score_breakdown_chart(sample_scores)
    print(f"   ✓ Chart created successfully")
    
    # Test 4: Keyword Density Chart
    print("\n4. Creating Keyword Density Chart...")
    sample_keywords = {
        'Python': 12,
        'Machine Learning': 8,
        'TensorFlow': 6,
        'Docker': 5,
        'AWS': 7,
        'React': 4,
        'Node.js': 3,
        'Kubernetes': 5
    }
    keyword_chart = create_keyword_density_chart(sample_keywords)
    print(f"   ✓ Chart created successfully")
    
    print("\n" + "=" * 50)
    print("All visualization tests passed! ✓")
    print("\nTo view charts in browser, you can save them:")
    print("  score_chart.show()  # Opens in default browser")
    
    # Optionally save charts as HTML
    try:
        score_chart.write_html("test_match_score.html")
        print("\n✓ Sample chart saved to: test_match_score.html")
    except Exception as e:
        print(f"\nNote: Could not save HTML file: {e}")