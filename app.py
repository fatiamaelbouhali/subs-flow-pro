import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="EMPIRE.PRO", layout="wide")

# ======================================================
# 🎨 STYLE ONLY – AUCUN CHANGEMENT DE LOGIQUE
# ======================================================
st.markdown("""
<style>

/* ===== GLOBAL ===== */
.stApp {
    background: linear-gradient(180deg, #f7f8fc 0%, #eef1f6 100%);
    color: #111;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #9a1f45 0%, #c13564 100%);
    padding: 22px;
}

section[data-testid="stSidebar"] * {
    color: #111 !important;
}

/* Logo */
.sidebar-logo {
    background: linear-gradient(90deg, #7bdc9a, #f29ac0);
    color: white;
    padding: 16px;
    border-radius: 18px;
    font-weight: 900;
    text-align: center;
    margin-bottom: 25px;
    font-size: 18px;
}

/* Menu buttons */
div[role="radiogroup"] > label {
    background: rgba(255,255,255,0.22);
    border: 1.5px solid rgba(255,255,255,0.4);
    border-radius: 16px;
    padding: 12px 16px;
    margin-bottom: 12px;
    font-weight: 700;
}

/* Active menu */
div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(90deg, #7bdc9a, #f29ac0);
    color: #111 !important;
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: linear-gradient(90deg, #7bdc9a, #f29ac0);
    border-radius: 16px;
    border: none;
    font-weight: 800;
    color: #111;
    padding: 10px 18px;
}

/* ===== INPUTS ===== */
input, textarea, select {
    border-radius: 16px !important;
    border: 2px solid #9a1f45 !important;
    background: #f2f4fa !important;
    font-weight: 600;
}

/* ===== HEADER ===== */
.header-pro {
    background: linear-gradient(90deg, #4f7cff, #8f5cff, #c13564);
    padding: 26px;
    border-radius: 30px;
    color: white;
    font-size: 30px;
    font-weight: 900;
    text-align: center;
    margin-bottom: 35px;
}

/* ===== KPI CARDS ===== */
.kpi-card {
    background: white;
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    font-weight: 900;
}

.kpi-value {
    color: #2fa866;
    font-size: 36px;
}

/* ===== RESUME TABLE ===== */
.resume-title {
    font-size: 28px;
    font-weight: 900;
    margin: 25px 0 15px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
}

thead th {
    background: linear-gradient(90deg, #f6b6cc, #d6e4ff);
    color: #111;
    font-weight: 900;
    font-size: 16px;
    padding: 14px;
}

tbody td {
    font-weight: 800;
    padding: 12px;
    border-bottom: 1px solid #ddd;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# SIDEBAR (LOGIQUE INCHANGÉE)
# ======================================================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">EMPIRE.PRO</div>', unsafe_allow_html=True)

    menu = st.radio(
        "MENU",
        ["GESTION", "ANALYTICS", "RAPPELS", "REÇUS"]
    )

    st.button("📤 Export Excel")
    st.button("Déconnexion")

# ======================================================
# HEADER
# ======================================================
st.markdown('<div class="header-pro">FATIMA ELBOUHALI PRO</div>', unsafe_allow_html=True)

# ======================================================
# ANALYTICS (EXEMPLE – نفس المنطق)
# ======================================================
if menu == "ANALYTICS":

    c1, c2, c3 = st.columns(3)

    c1.markdown("""
    <div class="kpi-card">
        💰 Chiffre d'Affaires<br>
        <div class="kpi-value">1741 DH</div>
    </div>
    """, unsafe_allow_html=True)

    c2.markdown("""
    <div class="kpi-card">
        👥 Actifs<br>
        <div class="kpi-value">8</div>
    </div>
    """, unsafe_allow_html=True)

    c3.markdown("""
    <div class="kpi-card">
        🚨 Alertes<br>
        <div class="kpi-value">8</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="resume-title">📊 Résumé par service</div>', unsafe_allow_html=True)

    df = pd.DataFrame({
        "Service": ["APT", "COURSERA", "ChatGPT", "IPTV", "Netflix", "Udemy", "udimy"],
        "Clients": [3, 1, 2, 2, 6, 4, 1],
        "CA": [410, 123, 140, 174, 406, 388, 100]
    })

    st.dataframe(df, use_container_width=True)

# ======================================================
# باقي الصفحات (GESTION / RAPPELS / REÇUS)
# ======================================================
# ⚠️ خليهُم بنفس الكود ديالك الحالي
# ⚠️ ما تبدّل حتى function ولا calcul
