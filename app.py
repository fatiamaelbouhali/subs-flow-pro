# ================= IMPORTS =================
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
import re
import io
import urllib.parse

# ================= CONFIG =================
st.set_page_config(
    page_title="EMPIRE.PRO",
    page_icon="🚀",
    layout="wide"
)

# ================= CSS – PRO CLEAN THEME =================
st.markdown("""
<style>

/* ===== GLOBAL ===== */
.stApp {
    background: #f3f6fb;
    font-family: "Inter", sans-serif;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #111827);
    padding: 20px;
}

.sidebar-logo {
    background: linear-gradient(135deg, #4ade80, #f472b6);
    color: white;
    font-weight: 900;
    text-align: center;
    padding: 18px;
    border-radius: 18px;
    font-size: 22px;
    margin-bottom: 25px;
}

/* Menu radio */
div[role="radiogroup"] label {
    background: rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
    color: #e5e7eb;
    border: 1px solid rgba(255,255,255,0.15);
}

div[role="radiogroup"] label[data-checked="true"] {
    background: linear-gradient(135deg, #60a5fa, #f472b6);
    color: white;
    font-weight: 800;
}

/* Sidebar buttons */
.stButton>button, .stDownloadButton>button {
    background: linear-gradient(135deg, #4ade80, #f472b6);
    color: white;
    font-weight: 800;
    border-radius: 14px;
    border: none;
    padding: 10px 16px;
}

/* ===== HEADER ===== */
.header-banner {
    background: linear-gradient(135deg, #3b82f6, #9333ea, #be185d);
    color: white;
    text-align: center;
    font-size: 28px;
    font-weight: 900;
    padding: 22px;
    border-radius: 24px;
    margin-bottom: 30px;
}

/* ===== INPUTS ===== */
div[data-baseweb="input"], 
div[data-baseweb="select"], 
.stDateInput div {
    border: 2px solid #c7d2fe !important;
    border-radius: 14px !important;
    background: white !important;
}

/* ===== METRICS ===== */
div[data-testid="stMetric"] {
    background: white;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 12px 30px rgba(0,0,0,.08);
    border-left: 6px solid #4ade80;
}

div[data-testid="stMetricValue"] {
    color: #16a34a;
    font-size: 36px;
    font-weight: 900;
}

div[data-testid="stMetricLabel"] p {
    font-weight: 800;
    color: #334155;
}

/* ===== TABLE ===== */
thead tr th {
    background: linear-gradient(135deg, #f472b6, #4ade80) !important;
    color: white !important;
    font-weight: 900 !important;
}

tbody tr td {
    font-weight: 600;
    color: #1f2937;
}

/* ===== RAPPEL CARD ===== */
.reminder-card {
    background: white;
    border-radius: 18px;
    padding: 18px 22px;
    margin-bottom: 16px;
    border-left: 6px solid #4ade80;
    box-shadow: 0 10px 25px rgba(0,0,0,.08);
}

.reminder-name {
    font-size: 18px;
    font-weight: 900;
}

.reminder-days {
    color: #16a34a;
    font-weight: 800;
}

</style>
""", unsafe_allow_html=True)

# ================= UTILS =================
def clean_phone(p):
    if not p:
        return ""
    n = re.sub(r'\D', '', str(p))
    if n.startswith("0") and len(n) == 10:
        n = "212" + n[1:]
    if len(n) == 9:
        n = "212" + n
    return n

def export_excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Clients")
    return buffer.getvalue()

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
    st.markdown('<div class="header-banner">🚀 EMPIRE.PRO GATEWAY</div>', unsafe_allow_html=True)

    user = st.text_input("Business ID")
    pwd = st.text_input("Access Key", type="password")

    if st.button("CONNEXION", use_container_width=True):
        master = client.open("Master_Admin").sheet1
        mdf = pd.DataFrame(master.get_all_records())
        ok = mdf[(mdf["User"] == user) & (mdf["Password"] == pwd)]
        if not ok.empty:
            r = ok.iloc[0]
            st.session_state.update({
                "auth": True,
                "sheet": r["Sheet_Name"],
                "biz": r["Business_Name"]
            })
            st.rerun()
        else:
            st.error("Identifiants incorrects")

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
    st.markdown('<div class="sidebar-logo">EMPIRE.PRO</div>', unsafe_allow_html=True)
    menu = st.radio("MENU", ["GESTION", "ANALYTICS", "RAPPELS", "REÇUS"])
    st.download_button("📥 Export Excel", export_excel(df), "clients.xlsx")
    if st.button("Déconnexion"):
        st.session_state.clear()
        st.rerun()

# ================= HEADER =================
st.markdown(
    f'<div class="header-banner">{st.session_state["biz"].upper()}</div>',
    unsafe_allow_html=True
)

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
        prix = st.number_input("Prix (DH)", 0)
        start = st.date_input("Start Date", today)
        months = st.number_input("Months", 1)

    if st.button("SAVE", use_container_width=True):
        fin = start + relativedelta(months=int(months))
        new_row = {
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
        df2 = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        sheet.clear()
        sheet.update([df2.columns.values.tolist()] + df2.astype(str).values.tolist())
        st.success("Client ajouté avec succès")
        st.rerun()

    st.dataframe(df, use_container_width=True)

# ================= ANALYTICS =================
elif menu == "ANALYTICS":
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Chiffre d'Affaires", f"{df['Prix'].sum()} DH")
    c2.metric("👥 Actifs", len(df[df["Status"] == "Actif"]))
    c3.metric("⏰ Alertes", len(df[df["Days"] <= 3]))

    resume = df.groupby("Service").agg(
        Clients=("Nom", "count"),
        CA=("Prix", "sum")
    ).reset_index()

    st.markdown("### 📊 Résumé par service")
    st.dataframe(resume, use_container_width=True)

# ================= RAPPELS =================
elif menu == "RAPPELS":
    urg = df[df["Days"] <= 3]
    if urg.empty:
        st.success("Aucun rappel")
    else:
        for _, r in urg.iterrows():
            st.markdown(f"""
            <div class="reminder-card">
                <div class="reminder-name">👤 {r['Nom']}</div>
                <div class="reminder-days">⏳ {r['Days']} jours restants</div>
                <div>🛠 {r['Service']}</div>
            </div>
            """, unsafe_allow_html=True)

            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire le {r['Date Fin']}."
            wa = f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote(msg)}"
            st.link_button("📲 WhatsApp", wa)

# ================= REÇUS =================
elif menu == "REÇUS":
    sel = st.selectbox("Client", df["Nom"].unique())
    r = df[df["Nom"] == sel].iloc[0]
    receipt = f"""
REÇU OFFICIEL – {st.session_state['biz']}
Client : {r['Nom']}
Service : {r['Service']}
Prix : {r['Prix']} DH
Expire : {r['Date Fin']}
Merci pour votre confiance 🙏
"""
    st.code(receipt)
