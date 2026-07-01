
import streamlit as st

st.set_page_config(
    page_title="ReviewGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

/* ───────── BASE ───────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f8fafc;
    color: #0f172a;
}

.stApp {
    background-color: #f8fafc;
}

/* ───────── SIDEBAR ───────── */
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
    padding-top: 1rem;
}

/* 🚫 REMOVE DEFAULT NAV */
[data-testid="stSidebarNav"] {
    display: none;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #334155 !important;
}

/* ───────── BRAND LOGO ───────── */
.rg-logo {
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 1.2rem;
    letter-spacing: -0.02em;
}

.rg-logo span {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ───────── HEADINGS (CLEAN POP) ───────── */
.rg-heading {
    font-size: 1.6rem;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 0.2rem;
    letter-spacing: -0.01em;
}

.rg-heading::after {
    content: "";
    display: block;
    width: 42px;
    height: 3px;
    background: #6366f1;
    border-radius: 2px;
    margin-top: 6px;
}

.rg-subheading {
    font-size: 0.95rem;
    color: #64748b;
    margin-bottom: 1.2rem;
}

.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #334155;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}

/* ───────── CARDS ───────── */
.rg-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

/* Accent Card */
.rg-card-accent {
    background: #f8fafc;
    border: 1px solid #e0e7ff;
    border-radius: 12px;
    padding: 1.2rem;
}

/* ───────── METRICS ───────── */
.metric-tile {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    transition: 0.2s ease;
}

.metric-tile:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 600;
    color: #0f172a;
}

.metric-label {
    font-size: 0.75rem;
    color: #64748b;
}

/* ───────── TAGS ───────── */
.tag {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
}

.tag-fake { background: #fee2e2; color: #dc2626; }
.tag-real { background: #dcfce7; color: #16a34a; }
.tag-warn { background: #fef3c7; color: #d97706; }

/* ───────── VERDICTS ───────── */
.verdict-fake {
    background: #fee2e2;
    border: 1px solid #fecaca;
    border-radius: 10px;
    padding: 1rem;
}

.verdict-real {
    background: #dcfce7;
    border: 1px solid #bbf7d0;
    border-radius: 10px;
    padding: 1rem;
}

/* ───────── BUTTONS ───────── */
.stButton>button {
    background: #6366f1;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 0.5rem 1rem;
    transition: 0.2s ease;
}

.stButton>button:hover {
    background: #4f46e5;
}

/* ───────── RADIO NAV (MAKE IT LOOK LIKE REAL NAV) ───────── */
div[role="radiogroup"] > label {
    padding: 8px 10px;
    border-radius: 8px;
    margin-bottom: 4px;
    transition: all 0.2s ease;
    cursor: pointer;
}

div[role="radiogroup"] > label:hover {
    background-color: #f1f5f9;
}

div[role="radiogroup"] > label[data-selected="true"] {
    background-color: #eef2ff;
    font-weight: 600;
}

/* ───────── INPUTS ───────── */
input, textarea {
    color: #0f172a !important;
    background-color: #ffffff !important;
}

input::placeholder, textarea::placeholder {
    color: #94a3b8 !important;
}

/* ───────── TABLES ───────── */
[data-testid="stDataFrame"] {
    color: #0f172a !important;
}

/* ───────── CLEANUP ───────── */
#MainMenu, footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)
# ── Sidebar nav ───────────────────────────────────────────────────────────────

with st.sidebar:
   
    st.markdown("""
    <div class="rg-logo">
        🛡️ <span>ReviewGuard</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**Navigation**")
    page = st.radio("Navigation", [
        "🏠  Overview",
        "🔍  Review Analyzer",
        "📊  Purchase Impact",
        "🗂️  Category Deep-Dive",
        "🤖  Model Comparison",
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<p style="font-size:0.75rem;color:#3a3a5a;">College Project · 2026<br/>Fake Review Detection & Purchase Behavior Analysis</p>', unsafe_allow_html=True)

# ── Route pages ───────────────────────────────────────────────────────────────
if "Overview" in page:
    from pages import overview; overview.render()
elif "Review Analyzer" in page:
    from pages import analyzer; analyzer.render()
elif "Purchase Impact" in page:
    from pages import purchase_impact; purchase_impact.render()
elif "Category Deep-Dive" in page:
    from pages import category_deepdive; category_deepdive.render()
elif "Model Comparison" in page:
    from pages import model_comparison; model_comparison.render()
