import copy

COLORS = {
    "bg":         "#0F1117",
    "surface":    "#1A1D27",
    "surface2":   "#22263A",
    "border":     "#2E3350",
    "accent":     "#6EE7B7",
    "accent2":    "#818CF8",
    "gold":       "#FCD34D",
    "red":        "#F87171",
    "text":       "#F1F5F9",
    "muted":      "#94A3B8",
    "dim":        "#475569",
    "pedra_Q":    "#67E8F9",
    "pedra_A":    "#F9A8D4",
    "pedra_Am":   "#A78BFA",
    "pedra_T":    "#FCD34D",
    "fem":        "#F472B6",
    "masc":       "#60A5FA",
}

_BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=COLORS["muted"], size=12),
    title=dict(text="", font=dict(family="Inter, sans-serif", color=COLORS["text"], size=15)),
    legend=dict(
        bgcolor="rgba(26,29,39,0.9)",
        bordercolor=COLORS["border"],
        borderwidth=1,
        font=dict(color=COLORS["muted"], size=11),
    ),
    xaxis=dict(
        gridcolor=COLORS["border"],
        linecolor=COLORS["border"],
        tickfont=dict(color=COLORS["muted"]),
        title_font=dict(color=COLORS["muted"]),
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor=COLORS["border"],
        linecolor=COLORS["border"],
        tickfont=dict(color=COLORS["muted"]),
        title_font=dict(color=COLORS["muted"]),
        zeroline=False,
    ),
    margin=dict(l=16, r=16, t=40, b=16),
    hoverlabel=dict(
        bgcolor="#1A1D27",
        bordercolor="#2E3350",
        font=dict(color="#F1F5F9", size=12),
        namelength=-1,
    ),
)

# Keep PLOTLY_LAYOUT for backward compat but use get_layout() for new code
PLOTLY_LAYOUT = _BASE_LAYOUT

HOVER = dict(
    bgcolor="#1A1D27",
    bordercolor="#2E3350",
    font=dict(color="#F1F5F9", size=12),
    namelength=-1,
)

def get_layout(**kwargs):
    """Returns a fresh deep copy of the base layout with optional overrides."""
    layout = copy.deepcopy(_BASE_LAYOUT)
    layout.update(kwargs)
    # Always enforce hover
    layout['hoverlabel'] = copy.deepcopy(HOVER)
    return layout

def apply_layout(fig, **kwargs):
    """Apply layout to fig and guarantee dark hover."""
    fig.update_layout(**get_layout(**kwargs))
    return fig

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stHeaderActionElements"] { display: none !important; }
[data-testid="stSidebar"] { background: #0D0F1A !important; border-right: 1px solid #1E2135 !important; }
[data-testid="stSidebar"] * { color: #94A3B8 !important; }

.metric-card {
    background: linear-gradient(135deg, #1A1D27 0%, #1E2235 100%);
    border: 1px solid #2E3350;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #6EE7B7; }
.metric-number {
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 0.2rem;
}
.metric-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748B;
}
.metric-delta {
    font-size: 0.78rem;
    font-weight: 500;
    margin-top: 0.35rem;
}

.insight-card {
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin: 0.6rem 0;
    border-left: 3px solid;
}
.insight-info    { background: rgba(110,231,183,0.07); border-color: #6EE7B7; }
.insight-warning { background: rgba(252,211,77,0.07);  border-color: #FCD34D; }
.insight-danger  { background: rgba(248,113,113,0.07); border-color: #F87171; }
.insight-success { background: rgba(129,140,248,0.07); border-color: #818CF8; }

.insight-card p { color: #CBD5E1; font-size: 0.88rem; line-height: 1.65; margin: 0; }
.insight-card strong { color: #F1F5F9; }

.section-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #6EE7B7;
    margin-bottom: 0.3rem;
}
.section-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #F1F5F9;
    line-height: 1.2;
    margin-bottom: 1.5rem;
}

div[data-testid="stExpander"] {
    background: #1A1D27 !important;
    border: 1px solid #2E3350 !important;
    border-radius: 10px !important;
}
</style>
"""

def inject_css():
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)

def metric_card(number, label, delta=None, color="#6EE7B7"):
    delta_html = f'<div class="metric-delta" style="color:{color};">▲ {delta}</div>' if delta else ""
    return f"""
    <div class="metric-card">
        <div class="metric-number" style="color:{color};">{number}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>"""

def insight(text, tipo="info"):
    icons = {"info":"💡","warning":"⚠️","danger":"🔴","success":"✨"}
    return f"""<div class="insight-card insight-{tipo}">
        <p>{icons[tipo]} {text}</p></div>"""

def section_header(label, title):
    return f"""
    <div class="section-label">{label}</div>
    <div class="section-title">{title}</div>"""
