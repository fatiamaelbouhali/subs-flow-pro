st.markdown("""
<style>

/* ===== GLOBAL ===== */
.stApp {
    background: #f9fafb;
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e5e7eb;
    padding-top: 1rem;
}

.sidebar-logo {
    background: linear-gradient(135deg,#6366f1,#ec4899);
    padding: 18px;
    border-radius: 14px;
    text-align: center;
    color: white;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 20px;
}

/* ===== NAV RADIO ===== */
div[role="radiogroup"] label {
    background: #f9fafb;
    border-radius: 12px;
    padding: 12px 18px;
    border: 1px solid #e5e7eb;
    margin-bottom: 8px;
    transition: all .2s ease;
}

div[role="radiogroup"] label:hover {
    background: #eef2ff;
    border-color: #6366f1;
}

div[role="radiogroup"] label[data-checked="true"] {
    background: linear-gradient(135deg,#6366f1,#ec4899);
    border: none;
}

div[role="radiogroup"] label[data-checked="true"] p {
    color: white;
    font-weight: 700;
}

/* ===== HEADER / BANNER ===== */
.biz-banner {
    background: linear-gradient(135deg,#6366f1,#ec4899);
    padding: 22px;
    border-radius: 20px;
    color: white;
    text-align: center;
    font-size: 26px;
    font-weight: 800;
    margin-bottom: 28px;
}

/* ===== METRICS ===== */
div[data-testid="stMetric"] {
    background: white;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 10px 25px rgba(0,0,0,.06);
    border: 1px solid #e5e7eb;
}

div[data-testid="stMetricValue"] > div {
    color: #111827;
    font-weight: 800;
    font-size: 34px;
}

div[data-testid="stMetricLabel"] p {
    color: #6b7280;
    font-weight: 600;
    letter-spacing: .03em;
}

/* ===== INPUTS ===== */
div[data-baseweb="input"],
div[data-baseweb="select"],
div[data-baseweb="base-input"],
.stDateInput div {
    border-radius: 12px !important;
    border: 1px solid #e5e7eb !important;
    background: #ffffff !important;
}

input, select, textarea {
    color: #111827 !important;
    font-weight: 500 !important;
}

/* ===== BUTTONS ===== */
button {
    border-radius: 12px !important;
    font-weight: 600 !important;
}

button[kind="primary"] {
    background: linear-gradient(135deg,#6366f1,#ec4899) !important;
    color: white !important;
    border: none !important;
}

/* ===== TABLE ===== */
.luxury-table {
    width: 100%;
    border-collapse: collapse;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 10px 25px rgba(0,0,0,.06);
}

.luxury-table thead tr {
    background: #111827;
    color: white;
    font-weight: 700;
}

.luxury-table td {
    padding: 14px;
    text-align: center;
    background: white;
    color: #111827;
    border-bottom: 1px solid #e5e7eb;
}

/* ===== RECEIPT ===== */
.receipt-card {
    background: #111827;
    padding: 28px;
    border-radius: 22px;
    color: white;
    font-family: 'JetBrains Mono', monospace;
    box-shadow: 0 10px 30px rgba(0,0,0,.3);
}

</style>
""", unsafe_allow_html=True)
