import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils import load_data_with_scores, get_category_stats

TEXT   = "#0f172a"   # main text
MUTED  = "#64748b"   # secondary text
PRIMARY= "#6366f1"   # main accent
FAKE   = "#ef4444"   # red (soft)
REAL   = "#22c55e"   # green (clean)
WARN   = "#f59e0b"   # amber
GRID   = "#e2e8f0"   # light grid
CARD   = "#ffffff"   # white cards
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color=TEXT),
    margin=dict(l=10, r=10, t=30, b=10),
)

def render():
    st.markdown('<div class="rg-heading">📊 Purchase Impact Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="rg-subheading">How fake reviews distort purchase signals — using model confidence scores to quantify real-world damage</div>', unsafe_allow_html=True)

    with st.spinner("Running analysis..."):
        df = load_data_with_scores()

        if df.empty:
            st.warning("⚠️ Data failed to load. Check model or dataset.")
            return
        cats = get_category_stats()

    # ── What-if slider ────────────────────────────────────────────────────────
    st.markdown('<div class="rg-card-accent">', unsafe_allow_html=True)
    st.markdown("### 🎛️ What-If Simulator")
    st.markdown('<p style="color:#64748b;font-size:0.85rem;">If fake reviews were removed, what would the real average rating be?</p>', unsafe_allow_html=True)

    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        fake_reduction = st.slider(
            "% of fake reviews removed from platform",
            min_value=0, max_value=100, value=50, step=5,
            format="%d%%"
        )
    with col_s2:
        selected_cat = st.selectbox("Category", cats['category_clean'].tolist())

    cat_row   = cats[cats['category_clean'] == selected_cat].iloc[0]
    curr_avg  = cat_row['avg_rating_all']
    inflation = cat_row['rating_inflation'] if not np.isnan(cat_row['rating_inflation']) else 0
    fake_r    = cat_row['fake_ratio']

    adjusted_avg = curr_avg - (inflation * fake_r * fake_reduction / 100)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-tile">
            <div class="metric-value" style="color: PRIMARY">{curr_avg:.2f}★</div>
            <div class="metric-label">Current avg rating</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-tile">
            <div class="metric-value" style="color: REAL">{adjusted_avg:.2f}★</div>
            <div class="metric-label">Adjusted (fakes removed)</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        delta = curr_avg - adjusted_avg
        st.markdown(f"""<div class="metric-tile">
            <div class="metric-value" style="color: FAKE">-{delta:.2f}★</div>
            <div class="metric-label">Inflation removed</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Confidence bucket analysis ─────────────────────────────────────────────
    st.markdown('<div class="rg-card">', unsafe_allow_html=True)
    st.markdown("### Model Confidence vs Purchase Signals")
    st.markdown('<p style="color:#9d9dbf;font-size:0.85rem;">Reviews bucketed by model\'s confidence they are fake. If fake reviews inflate ratings, you\'ll see avg rating <b>rise</b> as fakeness confidence increases.</p>', unsafe_allow_html=True)

    df['confidence_bucket'] = pd.cut(
        df['prob_fake'],
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=['0–20%', '20–40%', '40–60%', '60–80%', '80–100%']
    )
    bucket = df.groupby('confidence_bucket', observed=True).agg(
        avg_rating    = ('rating', 'mean'),
        purchase_rate = ('purchase_proxy', 'mean'),
        avg_sentiment = ('sentiment', 'mean'),
        count         = ('rating', 'count'),
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=bucket['confidence_bucket'], y=bucket['avg_rating'],
        mode='lines+markers', name='Avg Rating',
        line=dict(color=FAKE, width=2.5),
        marker=dict(size=8, color= FAKE),
    ))
    fig.add_trace(go.Scatter(
        x=bucket['confidence_bucket'], y=bucket['purchase_rate'],
        mode='lines+markers', name='Purchase Proxy Rate',
        line=dict(color= PRIMARY, width=2.5, dash='dot'),
        marker=dict(size=8, color= PRIMARY),
        yaxis='y2'
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=300,
        yaxis=dict(title='Avg Rating', gridcolor= GRID, range=[3, 5.2]),
        yaxis2=dict(title='Purchase Rate', overlaying='y', side='right',
                    showgrid=False, range=[0, 1.2]),
        legend=dict(bgcolor='rgba(0,0,0,0)', x=0.01, y=0.99),
        xaxis=dict(gridcolor=GRID),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Sneaky fakes section ───────────────────────────────────────────────────
    st.markdown('<div class="rg-card">', unsafe_allow_html=True)
    st.markdown("### 🕵️ Sneaky Fakes — Reviews that Fooled the Model")
    st.markdown('<p style="color:#9d9dbf;font-size:0.85rem;">Ground-truth fake reviews (CG) that the model predicted as real. These are the most dangerous — they look authentic and will also fool real buyers.</p>', unsafe_allow_html=True)

    sneaky = df[(df['is_fake'] == 1) & (df['model_label'] == 1)].copy()

    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (f"{len(sneaky):,}",           "Total sneaky fakes",     "#ff6b9d"),
        (f"{sneaky['rating'].mean():.2f}★", "Avg rating",         FAKE),
        (f"{sneaky['sentiment'].mean():.2f}", "Avg sentiment",    REAL),
        (f"{sneaky['purchase_proxy'].mean()*100:.1f}%", "Purchase proxy rate", "#6c63ff"),
    ]
    for col, (val, label, color) in zip([c1,c2,c3,c4], metrics):
        with col:
            st.markdown(f"""<div class="metric-tile">
                <div class="metric-value" style="color:{color};font-size:1.5rem">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Sample sneaky fakes:**")
    sample = sneaky[['text', 'rating', 'prob_fake', 'sentiment']].head(4)
    for _, row in sample.iterrows():
        st.markdown(f"""
        <div style="background:#fffbeb;border:1px solid #faf6e6;border-radius:8px;color:#92400e;
                    padding:0.8rem 1rem;margin-bottom:0.5rem;font-size:0.85rem;color:#75759e;">
            <span class="tag tag-warn">prob_fake: {row['prob_fake']:.2f}</span>
            <span style="color:#9d9dbf;font-size:0.78rem;margin-left:0.5rem;">
                rating: {row['rating']}★ · sentiment: {row['sentiment']:.2f}
            </span>
            <div style="margin-top:0.5rem;line-height:1.5;">{str(row['text'])[:220]}...</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Scatter: fake ratio vs purchase rate ───────────────────────────────────
    st.markdown('<div class="rg-card">', unsafe_allow_html=True)
    st.markdown("### Fake Ratio vs Purchase Rate (by Category)")
    fig2 = go.Figure()
    for _, row in cats.iterrows():
        fig2.add_trace(go.Scatter(
            x=[row['fake_ratio']*100], y=[row['purchase_rate']*100],
            mode='markers+text',
            marker=dict(
                size=row['trust_erosion']*80 + 10,
                color=row['trust_erosion'],
                colorscale=[
                    [0, '#22c55e'],   # green (low damage)
                    [0.5, '#6366f1'], # neutral
                    [1, '#ef4444']    # high damage
                ],
                showscale=False,
                opacity=0.85,
            ),
            text=[row['category_clean']],
            textposition='top center',
            textfont=dict(size=10, color=TEXT),
            
            showlegend=False,
        ))
    fig2.update_layout(**PLOTLY_LAYOUT, height=320,
        xaxis=dict(title='Fake Review %', gridcolor= GRID),
        yaxis=dict(title='Purchase Proxy Rate %', gridcolor= GRID),
    )
    fig2.add_annotation(text="Bubble size = trust erosion score",
        x=0.98, y=0.02, xref='paper', yref='paper',
        showarrow=False, font=dict(color=MUTED, size=10))
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">🧠 Final Verdict</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background:#f1f5f9;
        border-left:4px solid #6366f1;
        padding:1rem;
        border-radius:8px;
        color:#1e293b;
    ">
    Fake reviews are not just noise — they systematically inflate ratings and distort buyer perception.
    Even a 30–50% fake presence can artificially boost product appeal, leading to biased purchase behavior.
    Platforms that fail to control this risk long-term trust erosion.
    </div>
    """, unsafe_allow_html=True)