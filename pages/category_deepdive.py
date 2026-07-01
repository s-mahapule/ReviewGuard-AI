import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils import load_data_with_scores, get_category_stats

TEXT  = "#0f172a"   # dark text
MUTED = "#64748b"   # soft gray
PRIMARY = "#6366f1" # soft indigo
FAKE = "#ef4444"    # red (not neon)
REAL = "#22c55e"    # green (pleasant)
GRID = "#e2e8f0"    # light grid
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color=TEXT),
    margin=dict(l=10, r=10, t=30, b=10),
)

def render():
    st.markdown('<div class="rg-heading">🗂️ Category Deep-Dive</div>', unsafe_allow_html=True)
    st.markdown('<div class="rg-subheading">Select a category to explore its full fake review profile</div>', unsafe_allow_html=True)

    with st.spinner("Loading..."):
        df = load_data_with_scores()

        if df.empty:
            st.warning("⚠️ Data failed to load. Check model or dataset.")
            return
        cats = get_category_stats()

    selected = st.selectbox("Choose a category", cats['category_clean'].tolist())
    cat_df  = df[df['category_clean'] == selected].copy()
    cat_row = cats[cats['category_clean'] == selected].iloc[0]

    # ── Category KPIs ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(5)
    kpis = [
        (f"{int(cat_row['total_reviews']):,}", "Total reviews",   "#6c63ff"),
        (f"{cat_row['fake_ratio']*100:.1f}%",  "Fake ratio",      "#ff6b6b"),
        (f"{cat_row['avg_rating_all']:.2f}★",  "Current avg ★",   "#ffb86b"),
        (f"{cat_row['rating_inflation']:.2f}★" if not np.isnan(cat_row['rating_inflation']) else "N/A",
                                               "Rating inflation", "#ff6b9d"),
        (f"{cat_row['trust_erosion']:.3f}",    "Trust erosion",   "#6bffaa"),
    ]
    for col, (val, label, color) in zip(cols, kpis):
        with col:
            st.markdown(f"""<div class="metric-tile">
                <div class="metric-value" style="color:{color};font-size:1.4rem">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Rating distributions ───────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown("**Rating Distribution: Fake vs Real**")
        fake_r = cat_df[cat_df['model_label'] == 0]['rating']
        real_r = cat_df[cat_df['model_label'] == 1]['rating']
        fig = go.Figure()
        for ratings, name, color in [(fake_r, 'Fake (CG)', FAKE), (real_r, 'Real (OR)', REAL)]:
            counts = ratings.value_counts().sort_index()
            fig.add_trace(go.Bar(
                x=counts.index, y=counts.values, name=name,
                marker_color=color, opacity=0.8,
            ))
        fig.update_layout(**PLOTLY_LAYOUT, height=260,
            barmode='group',
            xaxis=dict(title='Rating', gridcolor=GRID, dtick=1),
            yaxis=dict(gridcolor=GRID),
            legend=dict(bgcolor='rgba(0,0,0,0)'),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown("**Sentiment Distribution: Fake vs Real**")
        fig2 = go.Figure()
        for label_val, name, color in [(0, 'Fake (CG)', '#ff4444'), (1, 'Real (OR)', '#6bffaa')]:
            subset = cat_df[cat_df['model_label'] == label_val]['sentiment']
            fig2.add_trace(go.Histogram(
                x=subset, name=name, nbinsx=20,
                marker_color=color, opacity=0.7,
            ))
        fig2.update_layout(**PLOTLY_LAYOUT, height=260,
            barmode='overlay',
            xaxis=dict(title='Sentiment score', gridcolor='#1e1e2e'),
            yaxis=dict(gridcolor='#1e1e2e'),
            legend=dict(bgcolor='rgba(0,0,0,0)'),
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Confidence distribution ────────────────────────────────────────────────
    st.markdown('<div class="rg-card">', unsafe_allow_html=True)
    st.markdown("**Model Confidence Distribution for this Category**")

    fig3 = go.Figure()
    for label_val, name, color in [(0, 'Predicted fake', '#ff4444'), (1, 'Predicted real', '#6bffaa')]:
        subset = cat_df[cat_df['model_label'] == label_val]['model_confidence']
        fig3.add_trace(go.Histogram(
            x=subset, name=name, nbinsx=20,
            marker_color=color, opacity=0.75,
        ))
    fig3.update_layout(**PLOTLY_LAYOUT, height=220,
        barmode='overlay',
        xaxis=dict(title='Model confidence', gridcolor='#1e1e2e'),
        yaxis=dict(gridcolor='#1e1e2e'),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Top fake reviews ───────────────────────────────────────────────────────
    st.markdown('<div class="rg-card">', unsafe_allow_html=True)
    st.markdown("**Most Confidently Fake Reviews in this Category**")

    top_fakes = (cat_df[cat_df['model_label'] == 0]
                 .sort_values('prob_fake', ascending=False)
                 .head(5))

    for _, row in top_fakes.iterrows():
        bar_width = int(row['prob_fake'] * 100)
        sent_str  = f"+{row['sentiment']:.2f}" if row['sentiment'] > 0 else f"{row['sentiment']:.2f}"
        st.markdown(f"""
        <div style="background:#fff1f2;border:1px solid #fecaca;border-radius:8px;
                    padding:0.9rem 1.1rem;margin-bottom:0.6rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                <span class="tag tag-fake">fake prob: {row['prob_fake']*100:.1f}%</span>
                <span style="color:#9d9dbf;font-size:0.78rem;">
                    ★ {row['rating']} · sentiment {sent_str}
                </span>
            </div>
            <div style="background:#2d0f0f;height:3px;border-radius:2px;margin-bottom:0.6rem;">
                <div style="background:#fecaca;height:3px;border-radius:2px;width:{bar_width}%"></div>
            </div>
            <div style="color:#75759e;font-size:0.84rem;line-height:1.5;">{str(row['text'])[:250]}...</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Comparison table ───────────────────────────────────────────────────────
    st.markdown('<div class="rg-card">', unsafe_allow_html=True)
    st.markdown("**Category vs All-Category Averages**")

    overall_fake_ratio = (df['model_label'] == 0).mean()
    overall_inflation  = cats['rating_inflation'].mean()
    overall_erosion    = cats['trust_erosion'].mean()

    compare_df = pd.DataFrame({
        "Metric":       ["Fake ratio", "Rating inflation", "Trust erosion", "Avg rating (all)", "Purchase rate"],
        selected:       [
            f"{cat_row['fake_ratio']*100:.1f}%",
            f"+{cat_row['rating_inflation']:.2f}★" if not np.isnan(cat_row['rating_inflation']) else "N/A",
            f"{cat_row['trust_erosion']:.3f}",
            f"{cat_row['avg_rating_all']:.2f}★",
            f"{cat_row['purchase_rate']*100:.1f}%",
        ],
        "All categories avg": [
            f"{overall_fake_ratio*100:.1f}%",
            f"+{overall_inflation:.2f}★",
            f"{overall_erosion:.3f}",
            f"{df['rating'].mean():.2f}★",
            f"{df['purchase_proxy'].mean()*100:.1f}%",
        ],
    })
    st.dataframe(compare_df.set_index("Metric"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
