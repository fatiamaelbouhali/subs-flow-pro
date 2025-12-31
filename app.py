# ================= IMPORTS =================
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

# ================= CONFIG =================
st.set_page_config(
    page_title="EMPIRE.PRO",
    page_icon="🚀",
    layout="wide"
)

# ================= STYLE (FINAL PRO THEME) =================
st.markdown("""
<style>

/* ===== GLOBAL ===== */
.stApp {
    background: linear-gradient(180deg,#eef2ff 0%, #f8fafc 100%);
    font-family: 'Inter', sans-serif;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0f172a,#111827);
    border-right: 1px solid #1f2937;
}

.sidebar-title {
    background: linear-gradient(135deg,#22c55e,#ec4899);
    padding:18px;
    border-radius:16px;
    text-align:center;
    color:white;
    font-weight:800;
    font-size:20px;
    margin-bottom:20px;
}

/* ===== HEADER ===== */
.main-header {
    background: linear-gradient(135deg,#3b82f6,#9333ea,#be185d);
    padding:26px;
    border-radius:26px;
    text-align:center;
    color:white;
    font-size:28px;
    font-weight:900;
    margin-bottom:30px;
    box-shadow:0 20px 40px rgba(0,0,0,.15);
}

/* ===== INPUTS ===== */
div[data-baseweb="input"], 
div[data-baseweb="select"], 
.stDateInput div {
    border-radius:14px !important;
    border:1px solid #c7d2fe !important;
    background:#ffffff !important;
}

/* ===== BUTTONS ===== */
.stButton>button, .stDownloadButton>button {
    background: linear-gradient(135deg,#22c55e,#ec4899);
    color:white;
    border:none;
    border-radius:14px;
    padding:12px;
    font-weight:800;
}

/* ===== METRICS ===== */
.metric-card {
    background: linear-gradient(135deg,#ffffff,#f1f5f9);
    border-radius:22px;
    padding:24px;
    box-shadow:0 20px 40px rgba(0,0,0,.08);
    border:1px solid #e5e7eb;
}

.metric-value {
    font-size:36px;
    font-weight:900;
    color:#16a34a;
}

/* ===== TABLE ===== */
[data-testid="stDataFrame"] {
    border-radius:18px;
    overflow:hidden;
}

/* ===== RAPPEL CARD ===== */
.alert-card {
    background:white;
    border-radius:22px;
    padding:20px;
    margin-bottom:16px;
    border-left:6px solid;
    border-image: linear-gradient(#22c55e,#ec4899) 1;
    box-shadow:0 15px 30px rgba(0,0,0,.08);
}

.alert-name {
    font-weight:800;
    font-size:18px;
}

.alert-days {
    font-weight:700;
    color:#16a34a;
}

/* ===== RECEIPT ===== */
.receipt-box {
    background: linear-gradient(135deg,#1f2937,#020617);
    color:#e5e7eb;
    padding:26px;
    border-radius:22px;
    font-size:17px;
    box-shadow:0 20px 40px rgba(0,0,0,.4);
}

</style>
""", unsafe_allow_html=True)

# ================= UTILS =================
def clean_phone(p):
    if not p:
        return ""
    n = re.sub(r'\D', '', str(p))
    if n.startswith("0"):
        n = "212" + n[1:]
    if len(n) == 9:
        n = "212" + n
    return n

# ================= GOOGLE SHEETS =================
def get_client():
    creds = st.secrets["connections"]["gsheets"]
    return gspread.authorize(
        Credentials.from_service_account_info(
            creds,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
    )

client = get_client()

# ================= LOGIN =================
if "auth" not in st.session_state:
    st.markdown('<div class="main-header">🚀 EMPIRE.PRO ACCESS</div>', unsafe_allow_html=True)
    u = st.text_input("Business ID")
    p = st.text_input("Access Key", type="password")
    if st.button("LOGIN"):
        master = client.open("Master_Admin").sheet1
        dfm = pd.DataFrame(master.get_all_records())
        ok = dfm[(dfm["User"] == u) & (dfm["Password"] == p)]
        if not ok.empty:
            r = ok.iloc[0]
            st.session_state.update({
                "auth": True,
                "sheet": r["Sheet_Name"],
                "biz": r["Business_Name"]
            })
            st.rerun()
        else:
            st.error("Access refusé")
    st.stop()

# ================= LOAD DATA =================
sheet = client.open(st.session_state["sheet"]).sheet1
df = pd.DataFrame(sheet.get_all_records())
today = datetime.now().date()

if not df.empty:
    df["Prix"] = pd.to_numeric(df["Prix"], errors="coerce").fillna(0)
    df["Date Fin"] = pd.to_datetime(df["Date Fin"], errors="coerce").dt.date
    df["Days"] = df["Date Fin"].apply(lambda x: (x - today).days if pd.notnull(x) else 0)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown('<div class="sidebar-title">EMPIRE.PRO</div>', unsafe_allow_html=True)
    menu = st.radio("MENU", ["GESTION", "ANALYTICS", "RAPPELS", "REÇUS"])
    st.download_button("📥 Export Excel", data=df.to_csv(index=False), file_name="clients.csv")
    if st.button("Déconnexion"):
        st.session_state.clear()
        st.rerun()

# ================= HEADER =================
st.markdown(f'<div class="main-header">{st.session_state["biz"]}</div>', unsafe_allow_html=True)

# ================= GESTION =================
if menu == "GESTION":
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("Nom")
        phone = st.text_input("WhatsApp")
        email = st.text_input("Email")
        status = st.selectbox("Status", ["Actif", "Payé", "En Attente", "Annulé"])
    with c2:
        service = st.text_input("Service")
        prix = st.number_input("Prix", 0)
        start = st.date_input("Start", today)
        months = st.number_input("Months", 1)

    if st.button("SAVE"):
        fin = start + relativedelta(months=int(months))
        new = {
            "Nom": nom,
            "Phone": clean_phone(phone),
            "Email": email,
            "Service": service,
            "Prix": prix,
            "Date Debut": start.strftime("%Y-%m-%d"),
            "Months": months,
            "Date Fin": fin.strftime("%Y-%m-%d"),
            "Status": status
        }
        df2 = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
        sheet.clear()
        sheet.update([df2.columns.tolist()] + df2.astype(str).values.tolist())
        st.success("Client ajouté")
        st.rerun()

    st.dataframe(df, use_container_width=True)

# ================= ANALYTICS =================
elif menu == "ANALYTICS":
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card">💰 Chiffre d\'Affaires<br><div class="metric-value">{df["Prix"].sum()} DH</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card">👥 Actifs<br><div class="metric-value">{len(df[df["Status"]=="Actif"])}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card">⏰ Alertes<br><div class="metric-value">{len(df[df["Days"]<=3])}</div></div>', unsafe_allow_html=True)

    resume = df.groupby("Service").agg(Clients=("Nom","count"), CA=("Prix","sum")).reset_index()
    st.dataframe(resume, use_container_width=True)

# ================= RAPPELS =================
elif menu == "RAPPELS":
    urg = df[df["Days"] <= 3]
    if urg.empty:
        st.success("Aucun rappel")
    else:
        for _, r in urg.iterrows():
            st.markdown(f"""
            <div class="alert-card">
                <div class="alert-name">👤 {r['Nom']}</div>
                <div class="alert-days">⏳ {r['Days']} jours restants</div>
                <div>🛠️ {r['Service']}</div>
            </div>
            """, unsafe_allow_html=True)
            wa = f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote('Bonjour, votre abonnement arrive à expiration.')}"
            st.link_button("📲 WhatsApp", wa)

# ================= REÇUS =================
elif menu == "REÇUS":
    sel = st.selectbox("Client", df["Nom"].unique())
    r = df[df["Nom"] == sel].iloc[0]
    receipt = f"""
REÇU OFFICIEL

Client : {r['Nom']}
Service : {r['Service']}
Prix : {r['Prix']} DH
Expiration : {r['Date Fin']}

Merci pour votre confiance.
"""
    st.markdown(f'<div class="receipt-box"><pre>{receipt}</pre></div>', unsafe_allow_html=True)
    st.link_button("📲 Envoyer WhatsApp", f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote(receipt)}")
