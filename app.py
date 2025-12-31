# ================= IMPORTS =================
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
import re, io, urllib.parse

# ================= CONFIG =================
st.set_page_config(page_title="EMPIRE.PRO", page_icon="🚀", layout="wide")

# ================= WHATSAPP CLEAN =================
def clean_phone(p):
    if not p:
        return ""
    n = re.sub(r'[^0-9]', '', str(p))
    if n.startswith("212"):
        return n
    if n.startswith("0") and len(n) == 10:
        return "212" + n[1:]
    if len(n) == 9:
        return "212" + n
    return n

# ================= CSS (UI ONLY) =================
st.markdown("""
<style>
.stApp { background:#f5f7fb; font-family:Inter, sans-serif; }

/* SIDEBAR */
[data-testid="stSidebar"]{
 background:linear-gradient(180deg,#8b1538,#b8326a);
}
.sidebar-title{
 background:linear-gradient(135deg,#4ade80,#f472b6);
 color:white;font-size:22px;font-weight:800;
 padding:14px;border-radius:16px;text-align:center;
 margin-bottom:20px;
}

/* MENU BUTTONS */
div[role="radiogroup"] label{
 background:#ffffff22;
 border:2px solid #ffffff55;
 border-radius:14px;
 padding:12px 16px;
 margin-bottom:10px;
}
div[role="radiogroup"] label p{color:white;font-weight:700;}
div[role="radiogroup"] label[data-checked="true"]{
 background:linear-gradient(135deg,#4ade80,#f472b6);
}

/* HEADER */
.main-header{
 background:linear-gradient(135deg,#4f7cff,#c0266d);
 color:white;font-size:28px;font-weight:900;
 padding:22px;border-radius:24px;text-align:center;
 margin-bottom:30px;
}

/* INPUTS */
div[data-baseweb="input"],div[data-baseweb="select"],.stDateInput div{
 border:2px solid #7c1d3a !important;
 border-radius:14px !important;
 background:white;
}

/* METRICS */
.metric-card{
 background:white;
 border-radius:20px;
 padding:24px;
 box-shadow:0 10px 30px rgba(0,0,0,.08);
}
.metric-value{
 font-size:40px;font-weight:900;color:#16a34a;
}

/* RESUME TABLE */
.resume-title{font-size:26px;font-weight:900;margin-top:30px;}
.resume-table th{
 background:linear-gradient(135deg,#f9a8d4,#93c5fd);
 font-size:18px;
}
.resume-table td{
 font-size:18px;font-weight:700;
}

/* RAPPEL CARD */
.alert-card{
 background:white;border-left:8px solid #22c55e;
 border-radius:18px;padding:18px;
 box-shadow:0 8px 24px rgba(0,0,0,.1);
 margin-bottom:16px;
}
</style>
""", unsafe_allow_html=True)

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
    st.markdown('<div class="main-header">🚀 EMPIRE GATEWAY</div>', unsafe_allow_html=True)
    u = st.text_input("Business ID")
    p = st.text_input("Access Key", type="password")
    if st.button("LOGIN", use_container_width=True):
        master = client.open("Master_Admin").sheet1
        mdf = pd.DataFrame(master.get_all_records())
        ok = mdf[(mdf["User"]==u)&(mdf["Password"]==p)]
        if not ok.empty:
            r = ok.iloc[0]
            st.session_state.update({
                "auth":True,
                "sheet":r["Sheet_Name"],
                "biz":r["Business_Name"]
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
    st.markdown('<div class="sidebar-title">EMPIRE.PRO</div>', unsafe_allow_html=True)
    menu = st.radio("MENU",["GESTION","ANALYTICS","RAPPELS","REÇUS"],label_visibility="collapsed")
    st.download_button("📥 Export Excel",
        df.to_csv(index=False).encode("utf-8"),
        "clients.csv")
    if st.button("Déconnexion"):
        st.session_state.clear()
        st.rerun()

# ================= HEADER =================
st.markdown(f'<div class="main-header">{st.session_state["biz"]}</div>', unsafe_allow_html=True)

# ================= GESTION =================
if menu=="GESTION":
    c1,c2=st.columns(2)
    with c1:
        nom=st.text_input("Nom")
        phone=st.text_input("WhatsApp")
        email=st.text_input("Email")
        status=st.selectbox("Status",["Actif","Payé","En Attente","Annulé","Expiré"])
    with c2:
        service=st.text_input("Service")
        prix=st.number_input("Prix (DH)",0)
        start=st.date_input("Start Date",today)
        months=st.number_input("Months",1)

    if st.button("SAVE",use_container_width=True):
        fin=start+relativedelta(months=int(months))
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
        st.success("Client ajouté ✔️")
        st.rerun()

    st.dataframe(df,use_container_width=True)

# ================= ANALYTICS =================
elif menu=="ANALYTICS":
    c1,c2,c3=st.columns(3)
    c1.markdown(f'<div class="metric-card"><div>💰 Chiffre d\'Affaires</div><div class="metric-value">{df["Prix"].sum()} DH</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><div>👥 Actifs</div><div class="metric-value">{len(df[df["Status"]=="Actif"])}</div></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><div>🚨 Alertes</div><div class="metric-value">{len(df[df["Days"]<=3])}</div></div>',unsafe_allow_html=True)

    resume = df.groupby("Service").agg(
        Clients=("Nom","count"),
        CA=("Prix","sum")
    ).reset_index()

    st.markdown('<div class="resume-title">📊 Résumé par service</div>',unsafe_allow_html=True)
    st.markdown(resume.to_html(classes="resume-table",index=False),unsafe_allow_html=True)

# ================= RAPPELS =================
elif menu=="RAPPELS":
    urg=df[df["Days"]<=3]
    if urg.empty:
        st.success("Aucun rappel")
    else:
        for _,r in urg.iterrows():
            st.markdown(f"""
            <div class="alert-card">
            <b>👤 {r['Nom']}</b><br>
            ⏳ {r['Days']} jours restants<br>
            🛠️ {r['Service']}
            </div>
            """,unsafe_allow_html=True)

            msg=f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire le {r['Date Fin']}."
            wa=f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote(msg)}"
            st.link_button("📲 WhatsApp",wa)

# ================= REÇUS =================
elif menu=="REÇUS":
    sel=st.selectbox("Client",df["Nom"].unique())
    r=df[df["Nom"]==sel].iloc[0]
    txt=f"""
REÇU OFFICIEL – {st.session_state['biz']}
Client : {r['Nom']}
Service : {r['Service']}
Prix : {r['Prix']} DH
Expiration : {r['Date Fin']}
Merci pour votre confiance 🙏
"""
    st.code(txt)
    wa=f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote(txt)}"
    st.link_button("📲 Envoyer WhatsApp",wa)
