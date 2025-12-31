# ===================== IMPORTS =====================
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px
import io
import re

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="EMPIRE.PRO",
    layout="wide",
    page_icon="🛡️"
)

# ===================== PRO THEME (CSS ONLY) =====================
st.markdown("""
<style>

/* ===== GLOBAL ===== */
.stApp {
    background: #f6f7fb;
    color: #111;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #8b1d3d 0%, #a8325a 100%);
    padding: 20px;
}

.sidebar-logo {
    background: linear-gradient(135deg, #5fd38d, #f08bb4);
    color: white;
    font-weight: 900;
    font-size: 22px;
    padding: 16px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 25px;
}

/* menu buttons */
[data-testid="stSidebar"] .stRadio label {
    background: rgba(255,255,255,0.12);
    border: 2px solid rgba(255,255,255,0.25);
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 10px;
    font-weight: 700;
    color: white;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.25);
}

/* ===== HEADER ===== */
.pro-header {
    background: linear-gradient(135deg, #4f7cff, #b83280);
    color: white;
    padding: 22px;
    border-radius: 26px;
    font-size: 28px;
    font-weight: 900;
    text-align: center;
    margin-bottom: 30px;
}

/* ===== INPUTS ===== */
div[data-baseweb="input"],
div[data-baseweb="select"],
.stDateInput > div {
    border: 2px solid #8b1d3d !important;
    border-radius: 14px !important;
    background: #ffffff !important;
}

input, select {
    font-weight: 700 !important;
}

/* ===== SAVE BUTTON ===== */
.stButton>button {
    background: linear-gradient(135deg, #5fd38d, #f08bb4);
    color: white;
    font-weight: 900;
    border-radius: 18px;
    padding: 10px 26px;
    border: none;
}

/* ===== METRICS ===== */
.metric-card {
    background: white;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
}

.metric-value {
    font-size: 36px;
    font-weight: 900;
    color: #1aa053;
}

/* ===== SUMMARY TABLE ===== */
.summary-table th {
    background: linear-gradient(135deg, #ffd6e6, #d7e8ff);
    color: #111;
    font-weight: 900;
}

.summary-table td {
    font-weight: 700;
}

/* ===== RAPPELS CARD ===== */
.rappel-card {
    background: white;
    border-left: 6px solid #5fd38d;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)

# ===================== UTILS =====================
def omega_whatsapp_fix(phone):
    if not phone:
        return ""
    num = re.sub(r'[^0-9]', '', str(phone))
    if num.startswith("0"):
        num = "212" + num[1:]
    if len(num) == 9:
        num = "212" + num
    return num

# ===================== GOOGLE SHEETS =====================
def get_client():
    creds = st.secrets["connections"]["gsheets"]
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    return gspread.authorize(
        Credentials.from_service_account_info(creds, scopes=scopes)
    )

client = get_client()

# ===================== LOGIN =====================
if "auth" not in st.session_state:
    st.markdown('<div class="pro-header">🛡️ EMPIRE.PRO</div>', unsafe_allow_html=True)

    user = st.text_input("Business ID")
    pwd = st.text_input("Access Key", type="password")

    if st.button("CONNEXION"):
        admin = client.open("Master_Admin").sheet1
        df_admin = pd.DataFrame(admin.get_all_records())

        ok = df_admin[
            (df_admin["User"] == user) &
            (df_admin["Password"] == pwd)
        ]

        if not ok.empty:
            st.session_state.auth = True
            st.session_state.user = user
            st.session_state.sheet = ok.iloc[0]["Sheet_Name"]
            st.session_state.biz = ok.iloc[0]["Business_Name"]
            st.rerun()

    st.stop()

# ===================== LOAD DATA =====================
sheet = client.open(st.session_state.sheet).sheet1
df = pd.DataFrame(sheet.get_all_records())

today = datetime.now().date()
if not df.empty:
    df["Prix"] = pd.to_numeric(df["Prix"], errors="coerce").fillna(0)
    df["Date Fin"] = pd.to_datetime(df["Date Fin"]).dt.date
    df["Days"] = df["Date Fin"].apply(lambda x: (x - today).days)

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">EMPIRE.PRO</div>', unsafe_allow_html=True)

    menu = st.radio(
        "MENU",
        ["GESTION", "ANALYTICS", "RAPPELS", "REÇUS"]
    )

    st.download_button(
        "📥 Export Excel",
        data=df.to_csv(index=False),
        file_name="clients.csv"
    )

    if st.button("Déconnexion"):
        st.session_state.clear()
        st.rerun()

# ===================== HEADER =====================
st.markdown(
    f'<div class="pro-header">{st.session_state.biz.upper()}</div>',
    unsafe_allow_html=True
)

# ===================== GESTION =====================
if menu == "GESTION":
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("Nom")
        phone = st.text_input("WhatsApp")
        email = st.text_input("Email")
        status = st.selectbox("Status", ["Actif", "Payé", "Annulé"])

    with c2:
        service = st.text_input("Service")
        prix = st.number_input("Prix (DH)", 0)
        start = st.date_input("Start Date", today)
        months = st.number_input("Months", 1)

    if st.button("SAVE"):
        end = start + relativedelta(months=int(months))
        new = [nom, phone, email, service, prix, start, months, end, status]
        df.loc[len(df)] = new
        sheet.clear()
        sheet.update([df.columns.tolist()] + df.astype(str).values.tolist())
        st.success("Client ajouté")
        st.rerun()

    st.dataframe(df, use_container_width=True)

# ===================== ANALYTICS =====================
elif menu == "ANALYTICS":
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Chiffre d'Affaires", f"{df['Prix'].sum()} DH")
    c2.metric("👥 Actifs", len(df[df["Status"] == "Actif"]))
    c3.metric("🚨 Alertes", len(df[df["Days"] <= 3]))

    resume = df.groupby("Service").agg(
        Clients=("Nom", "count"),
        CA=("Prix", "sum")
    ).reset_index()

    st.markdown("### 📊 Résumé par service")
    st.write(resume.to_html(classes="summary-table", index=False), unsafe_allow_html=True)

# ===================== RAPPELS =====================
elif menu == "RAPPELS":
    urgent = df[(df["Days"] <= 3) & (df["Status"] == "Actif")]

    for _, r in urgent.iterrows():
        st.markdown(
            f"""
            <div class="rappel-card">
                <b>👤 {r['Nom']}</b><br>
                ⏳ {r['Days']} jours restants<br>
                🛠 {r['Service']}
            </div>
            """,
            unsafe_allow_html=True
        )
        num = omega_whatsapp_fix(r["Phone"])
        msg = f"Bonjour {r['Nom']}, votre abonnement expire bientôt."
        st.link_button(
            "📲 WhatsApp",
            f"https://wa.me/{num}?text={urllib.parse.quote(msg)}"
        )

# ===================== REÇUS =====================
elif menu == "REÇUS":
    sel = st.selectbox("Client", df["Nom"].unique())
    c = df[df["Nom"] == sel].iloc[0]

    txt = f"""
REÇU OFFICIEL
Client: {c['Nom']}
Service: {c['Service']}
Prix: {c['Prix']} DH
Expire le: {c['Date Fin']}
Merci pour votre confiance
"""
    st.text(txt)

    num = omega_whatsapp_fix(c["Phone"])
    st.link_button(
        "📲 Envoyer",
        f"https://wa.me/{num}?text={urllib.parse.quote(txt)}"
    )
