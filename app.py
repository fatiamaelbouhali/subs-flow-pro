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
    page_title="EMPIRE PRO",
    page_icon="🚀",
    layout="wide"
)

# ================= CSS (DESIGN CLEAN SAAS) =================
st.markdown("""
<style>
.stApp {
    background-color: #f8fafc;
    font-family: 'Inter', sans-serif;
}
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
div[role="radiogroup"] label {
    background: #ffffff;
    border-radius: 12px;
    padding: 12px 16px;
    border: 1px solid #e5e7eb;
    margin-bottom: 8px;
}
div[role="radiogroup"] label[data-checked="true"] {
    background: #6366f1;
}
div[role="radiogroup"] label[data-checked="true"] p {
    color: white;
    font-weight: 700;
}
div[data-baseweb="input"],
div[data-baseweb="select"],
.stDateInput div {
    border-radius: 12px !important;
    border: 1px solid #e5e7eb !important;
    background: white !important;
}
div[data-testid="stMetric"] {
    background: white;
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}
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
.receipt-card {
    background: linear-gradient(135deg, #111827, #1f2933);
    padding: 28px;
    border-radius: 24px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ================= UTILS =================
def clean_phone(p):
    if not p:
        return ""
    n = re.sub(r'\D', '', str(p))
    if n.startswith('0') and len(n) == 10:
        n = '212' + n[1:]
    if len(n) == 9:
        n = '212' + n
    return n

# ================= GOOGLE SHEETS =================
MASTER_ID = "PUT_YOUR_MASTER_SHEET_ID_HERE"

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
    st.markdown("""
    <div style="
    background: linear-gradient(135deg,#6366f1,#ec4899);
    padding:30px;
    border-radius:20px;
    text-align:center;
    color:white;
    font-size:30px;
    font-weight:800;">
    🚀 EMPIRE GATEWAY
    </div>
    """, unsafe_allow_html=True)

    _, c, _ = st.columns([1,2,1])
    with c:
        user = st.text_input("Business ID")
        pwd = st.text_input("Access Key", type="password")
        if st.button("LOGIN", use_container_width=True):
            m_sheet = client.open_by_key(MASTER_ID).sheet1
            m_df = pd.DataFrame(m_sheet.get_all_records())
            ok = m_df[
                (m_df["User"] == user) &
                (m_df["Password"] == pwd)
            ]
            if not ok.empty:
                row = ok.iloc[0]
                st.session_state.update({
                    "auth": True,
                    "user": user,
                    "sheet": row["Sheet_Name"],
                    "biz": row["Business_Name"]
                })
                st.rerun()
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
    menu = st.radio("MENU", ["GESTION", "ANALYTICS", "RAPPELS", "REÇUS"], label_visibility="collapsed")
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# ================= HEADER =================
st.markdown(f"""
<div style="
background: linear-gradient(135deg,#6366f1,#ec4899);
padding:18px;
border-radius:18px;
color:white;
text-align:center;
font-size:26px;
font-weight:800;
margin-bottom:24px;">
👤 {st.session_state["biz"]}
</div>
""", unsafe_allow_html=True)

# ================= PAGES =================
if menu == "GESTION":
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("Nom")
        phone = st.text_input("WhatsApp")
        status = st.selectbox("Status", ["Actif", "Expiré"])
    with c2:
        service = st.text_input("Service")
        prix = st.number_input("Prix (DH)", min_value=0)
        start = st.date_input("Start Date", today)
        months = st.number_input("Months", min_value=1, value=1)

    if st.button("SAVE", use_container_width=True):
        fin = start + relativedelta(months=int(months))
        new = [nom, phone, service, prix, start, months, fin, status]
        df2 = pd.concat([df, pd.DataFrame([new], columns=df.columns)], ignore_index=True)
        sheet.clear()
        sheet.update([df2.columns.values.tolist()] + df2.astype(str).values.tolist())
        st.success("Saved")
        st.rerun()

    st.dataframe(df, use_container_width=True)

elif menu == "ANALYTICS":
    c1, c2, c3 = st.columns(3)
    c1.metric("Revenue", f"{df['Prix'].sum()} DH")
    c2.metric("Actifs", len(df[df["Status"] == "Actif"]))
    c3.metric("Alerts", len(df[df["Days"] <= 3]))

    if not df.empty:
        st.plotly_chart(
            px.bar(df, x="Service", y="Prix", color="Status"),
            use_container_width=True
        )

elif menu == "RAPPELS":
    urgent = df[df["Days"] <= 3]
    for _, r in urgent.iterrows():
        num = clean_phone(r["Phone"])
        link = f"https://wa.me/{num}?text=Votre abonnement expire bientôt"
        st.warning(f"{r['Nom']} | {r['Days']} jours")
        st.link_button("WhatsApp", link)

elif menu == "REÇUS":
    sel = st.selectbox("Client", df["Nom"].unique())
    r = df[df["Nom"] == sel].iloc[0]
    txt = f"""
RECU
Client: {r['Nom']}
Service: {r['Service']}
Prix: {r['Prix']} DH
Expire: {r['Date Fin']}
"""
    st.markdown(f"<div class='receipt-card'><pre>{txt}</pre></div>", unsafe_allow_html=True)
