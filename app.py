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
    page_icon="🛡️",
    layout="wide"
)

# ================= CSS (STYLE ONLY) =================
st.markdown("""
<style>

/* -------- GLOBAL -------- */
.stApp {
    background: #f5f7fb;
    font-family: 'Inter', sans-serif;
}

/* -------- SIDEBAR -------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#8b1c3d,#a8325a);
    color: white;
}

.sidebar-logo {
    background: linear-gradient(135deg,#3cb371,#e75480);
    padding:18px;
    border-radius:18px;
    text-align:center;
    font-size:22px;
    font-weight:900;
    color:white;
    margin-bottom:20px;
}

/* menu buttons */
div[role="radiogroup"] label {
    background: rgba(255,255,255,0.15);
    border-radius:14px;
    padding:12px;
    margin-bottom:10px;
    border:2px solid rgba(255,255,255,0.25);
}
div[role="radiogroup"] label[data-checked="true"] {
    background: linear-gradient(135deg,#3cb371,#e75480);
}
div[role="radiogroup"] label p {
    font-weight:800;
    color:white;
}

/* -------- HEADER -------- */
.header-banner {
    background: linear-gradient(135deg,#4a7cff,#b83280);
    padding:22px;
    border-radius:25px;
    text-align:center;
    color:white;
    font-size:26px;
    font-weight:900;
    margin-bottom:30px;
}

/* -------- INPUTS -------- */
div[data-baseweb="input"],
div[data-baseweb="select"],
.stDateInput div {
    border:2px solid #8b1c3d !important;
    border-radius:14px !important;
    background:white;
}

/* -------- METRICS -------- */
div[data-testid="stMetric"] {
    background:white;
    border-radius:20px;
    padding:20px;
    box-shadow:0 8px 25px rgba(0,0,0,0.06);
}

div[data-testid="stMetricValue"] {
    font-size:44px !important;
    font-weight:900 !important;
    color:#1faa59 !important;
}

/* -------- SUMMARY TABLE -------- */
.summary-table {
    width:70%;
    font-size:18px;
}

.summary-table th {
    background: linear-gradient(135deg,#f3c6d8,#c7d8ff);
    font-size:20px;
    font-weight:900;
    color:#000;
}

.summary-table td {
    font-weight:700;
}

/* -------- RAPPEL CARD -------- */
.rappel-card {
    background:white;
    border-left:6px solid #1faa59;
    padding:18px;
    border-radius:18px;
    margin-bottom:15px;
    box-shadow:0 6px 20px rgba(0,0,0,0.06);
}

</style>
""", unsafe_allow_html=True)

# ================= UTILS =================
def clean_phone(p):
    if not p: return ""
    n = re.sub(r'\D','',str(p))
    if n.startswith('0') and len(n)==10:
        n = '212' + n[1:]
    if len(n)==9:
        n = '212' + n
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
    st.markdown('<div class="header-banner">🛡️ EMPIRE GATEWAY</div>', unsafe_allow_html=True)

    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        user = st.text_input("Business ID")
        pwd = st.text_input("Access Key", type="password")
        if st.button("LOGIN", use_container_width=True):
            master = client.open("Master_Admin").sheet1
            mdf = pd.DataFrame(master.get_all_records())
            ok = mdf[(mdf["User"]==user) & (mdf["Password"]==pwd)]
            if not ok.empty:
                r = ok.iloc[0]
                st.session_state.update({
                    "auth": True,
                    "sheet": r["Sheet_Name"],
                    "biz": r["Business_Name"]
                })
                st.rerun()
            else:
                st.error("Login incorrect")
    st.stop()

# ================= LOAD DATA =================
sheet = client.open(st.session_state["sheet"]).sheet1
df = pd.DataFrame(sheet.get_all_records())
today = datetime.now().date()

if not df.empty:
    df["Prix"] = pd.to_numeric(df["Prix"], errors="coerce").fillna(0)
    df["Date Fin"] = pd.to_datetime(df["Date Fin"], errors="coerce").dt.date
    df["Days"] = df["Date Fin"].apply(lambda x:(x-today).days if pd.notnull(x) else 0)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">EMPIRE.PRO</div>', unsafe_allow_html=True)
    menu = st.radio("MENU",["GESTION","ANALYTICS","RAPPELS","REÇUS"],label_visibility="collapsed")
    st.download_button("📥 Export Excel", export_excel(df), "clients.xlsx")
    if st.button("Déconnexion"):
        st.session_state.clear()
        st.rerun()

# ================= HEADER =================
st.markdown(f'<div class="header-banner">{st.session_state["biz"]}</div>', unsafe_allow_html=True)

# ================= GESTION =================
if menu=="GESTION":
    c1,c2 = st.columns(2)
    with c1:
        nom = st.text_input("Nom")
        phone = st.text_input("WhatsApp")
        email = st.text_input("Email")
        status = st.selectbox("Status",["Actif","Payé","En Attente","Annulé"])
    with c2:
        service = st.text_input("Service")
        prix = st.number_input("Prix (DH)",0)
        start = st.date_input("Start Date",today)
        months = st.number_input("Months",1)

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
        st.success("Client ajouté")
        st.rerun()

    st.dataframe(df, use_container_width=True)

# ================= ANALYTICS =================
elif menu=="ANALYTICS":
    c1,c2,c3 = st.columns(3)
    c1.metric("💰 Chiffre d'Affaires", f"{df['Prix'].sum()} DH")
    c2.metric("👥 Actifs", len(df[df["Status"]=="Actif"]))
    c3.metric("🚨 Alertes", len(df[df["Days"]<=3]))

    resume = df.groupby("Service").agg(
        Clients=("Nom","count"),
        CA=("Prix","sum")
    ).reset_index()

    st.markdown("### 📊 Résumé par service")
    st.write(resume.to_html(classes="summary-table", index=False), unsafe_allow_html=True)

# ================= RAPPELS =================
elif menu=="RAPPELS":
    urg = df[df["Days"]<=3]
    for _,r in urg.iterrows():
        st.markdown(f"""
        <div class="rappel-card">
            <b>👤 {r['Nom']}</b><br>
            ⏳ {r['Days']} jours restants<br>
            🛠️ {r['Service']}
        </div>
        """, unsafe_allow_html=True)

        msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire le {r['Date Fin']}."
        link = f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote(msg)}"
        st.link_button("📲 WhatsApp", link)

# ================= REÇUS =================
elif menu=="REÇUS":
    sel = st.selectbox("Client", df["Nom"].unique())
    r = df[df["Nom"]==sel].iloc[0]

    txt = f"""
REÇU
Client: {r['Nom']}
Service: {r['Service']}
Prix: {r['Prix']} DH
Expire: {r['Date Fin']}
"""
    st.code(txt)
    wa = f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote(txt)}"
    st.link_button("📲 Envoyer WhatsApp", wa)
