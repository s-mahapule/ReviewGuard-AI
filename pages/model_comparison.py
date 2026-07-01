import streamlit as st
import plotly.graph_objects as go
import pandas as pd

TEXT  = "#0f172a"
MUTED = "#64748b"
PRIMARY = "#6366f1"
REAL = "#22c55e"
FAKE = "#ef4444"
GRID = "#e2e8f0"
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color=TEXT),
    margin=dict(l=10, r=10, t=30, b=10),
)

# ── All values measured directly from notebook timing cell ───────────────────
# train_time_sec and infer_time_sec are real wall-clock measurements.
# Interpretable = model exposes human-readable feature weights (LR coefs, NB log-probs).
# Recommended = best balance of precision + inference speed for a real-time API.
MODEL_RESULTS = pd.DataFrame([
    {
        "Model": "Logistic Regression",
        "Accuracy": 0.8553, "Precision": 0.8534,
        "Train (s)": 2.61,  "Infer (s)": 0.4754,
        "Interpretable": True,  "Recommended": False,
    },
    {
        "Model": "Multinomial NB",
        "Accuracy": 0.8395, "Precision": 0.8537,
        "Train (s)": 0.411, "Infer (s)": 0.0563,
        "Interpretable": True,  "Recommended": True,
    },
    {
        "Model": "Random Forest",
        "Accuracy": 0.8315, "Precision": 0.8548,
        "Train (s)": 46.179, "Infer (s)": 0.608,
        "Interpretable": False, "Recommended": False,
    },
    {
        "Model": "XGBoost",
        "Accuracy": 0.8162, "Precision": 0.794,
        "Train (s)": 25.083, "Infer (s)": 0.1764,
        "Interpretable": False, "Recommended": False,
    },
    {
        "Model": "Voting Classifier",
        "Accuracy": 0.8656, "Precision": 0.8715,
        "Train (s)": 81.785, "Infer (s)": 1.0833,
        "Interpretable": False, "Recommended": False,
    },
    {
        "Model": "Stacking Classifier",
        "Accuracy": 0.8570, "Precision": 0.8567,
        "Train (s)": 493.669, "Infer (s)": 1.1554,
        "Interpretable": False, "Recommended": False,
    },
])

def render():
    st.markdown('<div class="rg-heading">🤖 Model Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="rg-subheading">All 6 models evaluated — accuracy, precision, speed, and production recommendation</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Accuracy + Precision grouped bar ─────────────────────────────────────
    st.markdown('<div class="rg-card">', unsafe_allow_html=True)
    st.markdown("**Accuracy vs Precision — All Models**")
    colors_acc = [REAL if r else PRIMARY for r in MODEL_RESULTS['Recommended']]
    colors_prec = ["#94a3b8" if not r else REAL for r in MODEL_RESULTS['Recommended']]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Accuracy',
        x=MODEL_RESULTS['Model'], y=MODEL_RESULTS['Accuracy'] * 100,
        marker_color=colors_acc, text=[f"{v*100:.1f}%" for v in MODEL_RESULTS['Accuracy']],
        textposition='outside', textfont=dict(color=TEXT, size=11),
    ))
    fig.add_trace(go.Bar(
        name='Precision',
        x=MODEL_RESULTS['Model'], y=MODEL_RESULTS['Precision'] * 100,
        marker_color=colors_prec, text=[f"{v*100:.1f}%" for v in MODEL_RESULTS['Precision']],
        textposition='outside', textfont=dict(color=TEXT, size=11),
        opacity=0.8,
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=360,
        barmode='group',
        yaxis=dict(range=[80, 92], gridcolor=GRID, title='Score (%)'),
        xaxis=dict(gridcolor=GRID),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=TEXT)),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Training time bar (real measured values) ──────────────────────────────
    st.markdown('<div class="rg-card">', unsafe_allow_html=True)
    st.markdown("**Measured Training Time (seconds) — from notebook**")
    sorted_time = MODEL_RESULTS.sort_values('Train (s)', ascending=True)
    fig_time = go.Figure(go.Bar(
    x=sorted_time['Train (s)'],
    y=sorted_time['Model'],
    orientation='h',

    marker=dict(
        color=PRIMARY,
        opacity=0.85
    ),

    text=[f"{v:.2f}s" for v in sorted_time['Train (s)']],
    textposition='outside',
    textfont=dict(color=TEXT, size=11),
    ))
    fig_time.update_layout(**PLOTLY_LAYOUT, height=280,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(gridcolor=GRID), 
    )
    st.plotly_chart(fig_time, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Model Capability Breakdown ────────────────────────────────────────────────────────────
    st.markdown("**Model Capability Breakdown**")

    score_df = MODEL_RESULTS.copy()
    score_df['Speed Score'] = 1 - (score_df['Train (s)'] / score_df['Train (s)'].max())
    score_df['Interpretability'] = score_df['Interpretable'].astype(int)

    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=score_df['Model'],
        y=score_df['Accuracy'],
        name='Accuracy',
        marker_color=PRIMARY
    ))

    fig2.add_trace(go.Bar(
        x=score_df['Model'],
        y=score_df['Speed Score'],
        name='Speed',
        marker_color=REAL
    ))

    fig2.add_trace(go.Bar(
        x=score_df['Model'],
        y=score_df['Interpretability'],
        name='Interpretability',
        marker_color="#94a3b8"
    ))

    fig2.update_layout(
        **PLOTLY_LAYOUT,
        barmode='group',
        height=320,
        yaxis=dict(gridcolor=GRID),
        xaxis=dict(gridcolor=GRID),
    )

    st.plotly_chart(fig2, use_container_width=True)
    # ── Summary table ─────────────────────────────────────────────────────────
    st.markdown('<div class="rg-card">', unsafe_allow_html=True)
    st.markdown("**Model Summary Table** — all values measured from notebook")
    for _, row in MODEL_RESULTS.iterrows():
        rec_badge = '<span class="tag tag-real">✓ RECOMMENDED</span>' if row['Recommended'] else ''
        interp    = "✅ Yes" if row['Interpretable'] else "❌ No"
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:0.7rem 1rem;border-bottom:1px solid #e2e8f0;font-size:0.87rem;">
            <div style="width:210px;font-weight:500;color:{TEXT}">
                {row['Model']} {rec_badge}
            </div>
            <div style="color: FAKE  ;width:90px">Acc: <b>{row['Accuracy']*100:.2f}%</b></div>
            <div style="color: REAL  ;width:90px">Prec: <b>{row['Precision']*100:.2f}%</b></div>
            <div style="color:#ffb86b;width:110px">Train: <b>{row['Train (s)']}s</b></div>
            <div style="color: PRIMARY;width:100px">Infer: <b>{row['Infer (s)']}s</b></div>
            <div style="color:{MUTED};width:90px">Interp: {interp}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Recommendation card ────────────────────────────────────────────────────
    st.markdown("""
    <div class="rg-card-accent" style="margin-top:1rem">
        <div style="font-family:'Syne',sans-serif;font-weight:700;color:#6c63ff;margin-bottom:0.5rem;">
            🏆 Production Recommendation: Multinomial Naive Bayes
        </div>
        <div style="color:#9d9dbf;font-size:0.88rem;line-height:1.7;">
            Naive Bayes trained in <b style="color:#6bffaa">0.41s</b> and infers in 
            <b style="color:#6bffaa">0.056s</b> — <b>1,200× faster to train</b> than Stacking (493s) 
            and <b>20× faster inference</b> than Voting (1.08s). Its precision of 
            <b style="color:#6bffaa">85.37%</b> matches Random Forest and nearly ties Voting Classifier, 
            with none of the compute cost. The Voting Classifier is the most accurate overall 
            (86.56%) but takes 82s to train and 1.08s per inference batch — 
            not practical for a real-time review screening API. NB's probabilistic output 
            also directly powers the confidence-score analysis in the Purchase Impact module.
        </div>
    </div>
    """, unsafe_allow_html=True)
