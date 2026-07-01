import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import load_data_with_scores, get_category_stats

BG = "#ffffff"
CARD = "#ffffff"

PRIMARY = "#6366f1"
SECONDARY = "#8b5cf6"

TEXT = "#0f172a"
MUTED = "#64748b"

REAL = "#22c55e"
FAKE = "#ef4444"
WARN = "#f59e0b"

GRID = "#e2e8f0"

PLOTLY_LAYOUT = dict(
    paper_bgcolor='white',
    plot_bgcolor='white',
    font=dict(family='DM Sans', color=TEXT),
    margin=dict(l=10, r=10, t=30, b=10),
)

def render():
    st.markdown('<div class="rg-heading">📊 Project Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="rg-subheading">Fake review detection & purchase behavior analysis across Amazon product categories</div>', unsafe_allow_html=True)

    with st.spinner("Loading dataset..."):
        df = load_data_with_scores()

        if df.empty:
            st.warning("⚠️ Data failed to load. Check model or dataset.")
            return
        cats = get_category_stats()

    total       = len(df)
    fake_count  = (df['model_label'] == 0).sum()
    fake_pct    = fake_count / total * 100
    avg_conf    = df['model_confidence'].mean() * 100
    sneaky      = ((df['is_fake']==1) & (df['model_label']==1)).sum()

    # ── KPI row ──────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-tile">
            <div class="metric-value" style="color:PRIMARY">{total:,}</div>
            <div class="metric-label">Total Reviews</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-tile">
            <div class="metric-value" style="color:FAKE">{fake_pct:.1f}%</div>
            <div class="metric-label">Detected Fake</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-tile">
            <div class="metric-value" style="color:REAL">{avg_conf:.1f}%</div>
            <div class="metric-label">Avg Model Confidence</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-tile">
            <div class="metric-value" style="color:WARN">{sneaky:,}</div>
            <div class="metric-label">Sneaky Fakes 🕵️</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

#------------------------------------
    from insights import generate_overview_insight

    insight = generate_overview_insight(df)
    st.markdown('<div class="section-title">💡 AI Insight</div>', unsafe_allow_html=True)

    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.write(insight)
    st.markdown('</div>', unsafe_allow_html=True)
    # ── Row 2: Fake ratio chart + label pie ───────────────────────────────────
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown("**Fake Review Ratio by Category**")
        cats_sorted = cats.sort_values('fake_ratio', ascending=True)
        fig = go.Figure(go.Bar(
            x=cats_sorted['fake_ratio'] * 100,
            y=cats_sorted['category_clean'],
            orientation='h',
            marker=dict(
                color=cats_sorted['fake_ratio'],
                colorscale=[
                    [0, '#dcfce7'],   # light green
                    [0.5, '#fde68a'], # soft yellow
                    [1, '#fee2e2']    # light red
                ],
                showscale=False,
            ),
            text=[f"{v:.1f}%" for v in cats_sorted['fake_ratio']*100],
            textposition='outside',
            textfont=dict(color=TEXT, size=11),
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=300,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(gridcolor=GRID),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown("**Overall Label Distribution**")
        fig2 = go.Figure(go.Pie(
            labels=['Fake (CG)', 'Real (OR)'],
            values=[fake_count, total - fake_count],
            hole=0.6,
            marker=dict(
                colors=[FAKE, REAL],
                line=dict(color='white', width=2)
            ),
            textinfo='label+percent',
            textfont=dict(color=TEXT, size=12),
        ))
        fig2.add_annotation(text=f"{fake_pct:.1f}%<br><span style='font-size:10px'>fake</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color=TEXT, family='Syne'))
        fig2.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 3: Trust erosion + rating inflation ───────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown("**Trust Erosion Score by Category**")
        cats2 = cats.sort_values('trust_erosion', ascending=True)
        fig3 = go.Figure(go.Bar(
            x=cats2['trust_erosion'],
            y=cats2['category_clean'],
            orientation='h',
            marker=dict(color=cats2['trust_erosion'],
                        colorscale=[
                            [0, '#e0f2fe'],
                            [0.5, '#c7d2fe'],
                            [1, '#fbcfe8']
                        ],
                        showscale=False),
            text=[f"{v:.3f}" for v in cats2['trust_erosion']],
            textposition='outside',
            textfont=dict(color=TEXT, size=11),
        ))
        fig3.update_layout(**PLOTLY_LAYOUT, height=300,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(gridcolor=GRID),
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_d:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown("**Rating Inflation (Fake vs Real Reviews)**")
        cats3 = cats.sort_values('rating_inflation', ascending=True).dropna(subset=['rating_inflation'])
        colors = [FAKE if v > 0 else REAL for v in cats3['rating_inflation']]
        fig4 = go.Figure(go.Bar(
            x=cats3['rating_inflation'],
            y=cats3['category_clean'],
            orientation='h',
            marker=dict(color=colors),
            text=[f"+{v:.2f}★" if v > 0 else f"{v:.2f}★" for v in cats3['rating_inflation']],
            textposition='outside',
            textfont=dict(color=TEXT, size=11),
        ))
        fig4.add_vline(x=0, line_color=MUTED, line_width=1)
        fig4.update_layout(**PLOTLY_LAYOUT, height=300,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(gridcolor=GRID),
        )
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Key finding callout ───────────────────────────────────────────────────
    worst = cats.sort_values('trust_erosion', ascending=False).iloc[0]
    st.markdown(f"""
    <div class="rg-card-accent">
        <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:PRIMARY;margin-bottom:0.5rem;border: 1px solid #e0e7ff;
background: #f8fafc;">
            🔑 Key Finding
        </div>
        <div style="color:{TEXT};font-size:0.95rem;line-height:1.6;">
            <b>{worst['category_clean']}</b> has the highest trust erosion score 
            (<b>{worst['trust_erosion']:.3f}</b>) with <b>{worst['fake_ratio']*100:.1f}%</b> fake reviews 
            inflating average ratings by <b>+{worst['rating_inflation']:.2f} stars</b>. 
            This directly misleads buyers making purchase decisions based on star ratings.
        </div>
    </div>
    """, unsafe_allow_html=True)
