st.markdown("""
<style>

/* ===== GLOBAL ===== */
.stApp {
    background-color: #f8fafc;
    font-family: 'Inter', sans-serif;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e5e7eb;
}
.sidebar-logo {
    background: linear-gradient(135deg, #6366f1, #ec4899);
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 20px;
    color: white;
    font-size: 22px;
    font-weight: 800;
}

/* ===== MENU ===== */
div[role="radiogroup"] label {
    background: #ffffff;
    border-radius: 12px;
    padding: 12px 16px;
    border: 1px solid #e5e7eb;
    margin-bottom: 8px;
    transition: all 0.2s ease;
}
div[role="radiogroup"] label[data-checked="true"] {
    background: #6366f1;
    border: none;
}
div[role="radiogroup"] label[data-checked="true"] p {
    color: white;
    font-weight: 700;
}

/* ===== INPUTS ===== */
div[data-baseweb="input"],
div[data-baseweb="select"],
.stDateInput div {
    border-radius: 12px !important;
    border: 1px solid #e5e7eb !important;
    background: white !important;
}
input, select {
    font-weight: 600;
    color: #111827;
}

/* ===== METRICS ===== */
div[data-testid="stMetric"] {
    background: white;
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}

/* ===== TABLE ===== */
.luxury-table {
    width: 100%;
    border-collapse: collapse;
    border-radius: 14px;
    overflow: hidden;
}
.luxury-table thead tr {
    background-color: #6366f1;
    color: white;
}
.luxury-table td {
    padding: 14px;
    text-align: center;
    background-color: white;
    border-bottom: 1px solid #f1f5f9;
}

/* ===== RECEIPT ===== */
.receipt-card {
    background: linear-gradient(135deg, #111827, #1f2933);
    padding: 28px;
    border-radius: 24px;
    color: white;
    box-shadow: 0 10px 40px rgba(0,0,0,0.4);
}

</style>
""", unsafe_allow_html=True)
