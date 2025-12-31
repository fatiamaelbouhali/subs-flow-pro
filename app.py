# ================== PRO UI THEME – CSS ONLY ==================
st.markdown("""
<style>

/* ================= GLOBAL ================= */
.stApp {
    background-color: #f6f7fb;
    color: #111111;
}

/* ================= SIDEBAR ================= */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #a8324a, #b83a5a);
    padding: 22px;
}

section[data-testid="stSidebar"] * {
    color: #111 !important;
}

/* LOGO / TITLE */
.sidebar-logo {
    background: linear-gradient(90deg, #7bdc9a, #f29ac0);
    padding: 16px;
    border-radius: 18px;
    font-weight: 900;
    text-align: center;
    margin-bottom: 25px;
    color: white !important;
}

/* MENU BUTTONS */
div[role="radiogroup"] > label {
    background: rgba(255,255,255,0.25);
    border: 1.8px solid rgba(255,255,255,0.6);
    border-radius: 18px;
    padding: 12px 18px;
    margin-bottom: 12px;
    font-weight: 800;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* ACTIVE MENU */
div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(90deg, #7bdc9a, #f29ac0);
    color: #111 !important;
}

/* ================= HEADER ================= */
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

/* ================= INPUTS – AJOUT CLIENT ================= */
input, textarea, select, div[data-baseweb="input"], div[data-baseweb="select"] {
    border-radius: 18px !important;
    border: 2px solid #8b1e3f !important;
    background-color: #f1f3f9 !important;
    font-weight: 600;
    color: #111 !important;
}

/* ================= BUTTONS ================= */
button {
    border-radius: 18px !important;
    font-weight: 800 !important;
}

/* ================= KPI CARDS ================= */
div[data-testid="metric-container"] {
    background: #ffffff;
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}

div[data-testid="metric-container"] label {
    font-weight: 800;
    color: #444;
}

div[data-testid="metric-container"] div {
    font-size: 36px;
    font-weight: 900;
    color: #2fa866;
}

/* ================= RÉSUMÉ PAR SERVICE ================= */
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

/* ================= RAPPELS CARDS ================= */
.rappel-card {
    background: white;
    border-left: 6px solid #7bdc9a;
    border-radius: 20px;
    padding: 16px 20px;
    margin-bottom: 18px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.07);
    font-weight: 700;
}

/* ================= EXPORT / LOGOUT ================= */
section[data-testid="stSidebar"] button {
    background: linear-gradient(90deg, #7bdc9a, #f29ac0) !important;
    color: white !important;
    font-weight: 900 !important;
}

</style>
""", unsafe_allow_html=True)
# ================== END THEME ==================
