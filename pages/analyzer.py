import streamlit as st
import plotly.graph_objects as go
from utils import predict_single

TEXT  = "#0f172a"
MUTED = "#64748b"
PRIMARY = "#6366f1"
REAL = "#22c55e"
FAKE = "#ef4444"
WARN = "#f59e0b"
GRID = "#e2e8f0"
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color=TEXT),
    margin=dict(l=10, r=10, t=10, b=10),
)

SAMPLE_REVIEWS = {
    "🚨 Likely Fake": "This pillow saved my back. I love the look and feel of this pillow.",
    "✅ Likely Real": "Bought this for my kitchen. Works fine but the handle gets a little warm after extended use. Would have preferred a longer cord. Decent quality for the price.",
    "🤔 Borderline": "Great product, does what it says. Arrived quickly and packaging was good. Happy with the purchase overall.",
}

def gauge_chart(prob_fake: float):
    pct = prob_fake * 100

    color = FAKE if pct > 65 else (WARN if pct > 40 else REAL)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,

        number=dict(
            suffix="%",
            font=dict(size=36, color=TEXT)
        ),

        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickcolor=MUTED,
                tickfont=dict(color=MUTED)
            ),

            bar=dict(color=color, thickness=0.3),

            bgcolor='white',
            bordercolor=GRID,
            borderwidth=1,

            steps=[
                dict(range=[0, 40],  color='#ecfdf5'),
                dict(range=[40, 65], color='#fffbeb'),
                dict(range=[65, 100], color='#fef2f2'),
            ],

            threshold=dict(
                line=dict(color=color, width=4),
                thickness=0.8,
                value=pct
            )
        ),

        title=dict(
            text="Fake Probability",
            font=dict(size=13, color=MUTED)
        ),
    ))

    fig.update_layout(**PLOTLY_LAYOUT, height=260)

    return fig

def signal_bars(result: dict):
    signals = {
        "Word count":    min(result['word_count'] / 200, 1.0),
        "Sentiment":     (result['sentiment'] + 1) / 2,
        "Confidence":    result['confidence'],
        "Fake prob":     result['prob_fake'],
    }

    colors = [PRIMARY, REAL, WARN, FAKE]

    fig = go.Figure()

    for i, (label, val) in enumerate(signals.items()):
        fig.add_trace(go.Bar(
            x=[val],
            y=[label],
            orientation='h',

            marker=dict(color=colors[i]),

            text=f"{val:.2f}",
            textposition='outside',
            textfont=dict(color=TEXT, size=11),

            showlegend=False,
        ))

    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=200,
        barmode='overlay',

        xaxis=dict(
            range=[0, 1.2],
            showgrid=False,
            showticklabels=False
        ),

        yaxis=dict(gridcolor=GRID),
    )

    return fig

def render():
    st.markdown('<div class="rg-heading">🔍 Review Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="rg-subheading">Paste any review to get a fake probability score, confidence level, and breakdown of signals</div>', unsafe_allow_html=True)

    # Sample selector
    sample_choice = st.selectbox("Try a sample review:", ["— paste your own below —"] + list(SAMPLE_REVIEWS.keys()))
    default_text = SAMPLE_REVIEWS.get(sample_choice, "")

    review_text = st.text_area(
        "Review text",
        value=default_text,
        height=130,
        placeholder="Paste a product review here...",
        label_visibility="collapsed"
    )

    col_btn, col_info = st.columns([1, 4])
    with col_btn:
        analyze = st.button("🔍 Analyze", use_container_width=True, type="primary")

    if not analyze and not default_text:
        st.markdown("""
        <div class="rg-card" style="text-align:center;padding:3rem;">
            <div style="font-size:3rem;">🛡️</div>
            <div style="color:#6b6b8a;margin-top:0.5rem;font-size:0.9rem;">
                Enter a review above and click Analyze
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    if not review_text.strip():
        st.warning("Please enter some review text.")
        return

    with st.spinner("Analyzing..."):
        result = predict_single(review_text)

    is_fake   = result['prediction'] == 'fake'
    conf_pct  = result['confidence'] * 100
    fake_pct  = result['prob_fake'] * 100
    sentiment = result['sentiment']

    # ── Verdict banner ────────────────────────────────────────────────────────
    if is_fake:
        risk = "HIGH RISK" if fake_pct > 75 else "MODERATE RISK"
        risk_color = FAKE if fake_pct > 75 else "#ffb86b"
        st.markdown(f"""
        <div class="verdict-fake">
            <div class="verdict-title" style="color: FAKE>🚨 Likely Fake Review</div>
            <div style="color:#ff9999;font-size:0.85rem;margin-top:0.3rem;">
                Risk Level: <b style="color:{risk_color}">{risk}</b>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="verdict-real">
            <div class="verdict-title" style="color:REAL">✅ Likely Authentic Review</div>
            <div style="color:#88ffcc;font-size:0.85rem;margin-top:0.3rem;">
                Model is <b>{conf_pct:.1f}%</b> confident this is genuine
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gauge + signals ───────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.plotly_chart(gauge_chart(result['prob_fake']), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="rg-card">', unsafe_allow_html=True)
        st.markdown("**Signal Breakdown**")
        st.plotly_chart(signal_bars(result), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        # Mini stat cards
        sent_label = "Positive 😊" if sentiment > 0.1 else ("Negative 😞" if sentiment < -0.1 else "Neutral 😐")
        sent_color = REAL if sentiment > 0.1 else (FAKE if sentiment < -0.1 else "#ffb86b")

        st.markdown(f"""
        <div class="metric-tile" style="margin-bottom:0.8rem">
            <div class="metric-value" style="color:PRIMARY;font-size:1.6rem">{conf_pct:.0f}%</div>
            <div class="metric-label">Confidence</div>
        </div>
        <div class="metric-tile" style="margin-bottom:0.8rem">
            <div class="metric-value" style="color:{sent_color};font-size:1rem">{sent_label}</div>
            <div class="metric-label">Sentiment</div>
        </div>
        <div class="metric-tile">
            <div class="metric-value" style="color:TEXT;font-size:1.6rem">{result['word_count']}</div>
            <div class="metric-label">Words</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Probability breakdown bar ─────────────────────────────────────────────
    st.markdown('<div class="rg-card">', unsafe_allow_html=True)
    st.markdown("**Probability Breakdown**")
    col_f, col_r = st.columns(2)
    with col_f:
        st.markdown(f'<span class="tag tag-fake">FAKE</span>', unsafe_allow_html=True)
        st.progress(result['prob_fake'])
        st.markdown(f'<span style="color:FAKE;font-size:1.1rem;font-weight:600">{fake_pct:.1f}%</span>', unsafe_allow_html=True)
    with col_r:
        st.markdown(f'<span class="tag tag-real">REAL</span>', unsafe_allow_html=True)
        st.progress(result['prob_real'])
        st.markdown(f'<span style="color:REAL;font-size:1.1rem;font-weight:600">{result["prob_real"]*100:.1f}%</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Interpretation ────────────────────────────────────────────────────────
    if is_fake:
        tip = "This review shows patterns common in computer-generated text — overly positive language, generic praise, and sentiment that may not match typical buyer experience."
    else:
        tip = "This review contains specific details and balanced sentiment typical of genuine buyer feedback. The model found no strong indicators of machine generation."

    st.markdown(f"""
    <div class="rg-card-accent">
        <div style="font-size:0.85rem;color:#9d9dbf;line-height:1.7;">
            💡 <b style="color:PRIMARY">Interpretation:</b> {tip}
        </div>
    </div>
    """, unsafe_allow_html=True)
