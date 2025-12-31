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

# ================= CONFIG =================
st.set_page_config(
    page_title="EMPIRE.PRO",
    page_icon="🚀",
    layout="wide"
)

# ================= CSS PRO (UI ONLY) =================
st.markdown("""
<style>

/* ===== GLOBAL ===== */
.stApp {
    background: linear-gradient(180deg,#fdf2f4,#f8fafc);
    color:#111827;
    font-family:Inter,sans-serif;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#9f1239,#be185d);
    border-right:2px solid #fda4af;
}
.sidebar-logo{
    background:linear-gradient(135deg,#22c55e,#ec4899);
    padding:18px;
    border-radius:18px;
    text-align:center;
    color:white;
    font-size:22px;
    font-weight:900;
    margin-bottom:20px;
}

/* MENU */
div[role="radiogroup"] label{
    background:rgba(255,255,255,.15);
    border:2px solid #fda4af;
    border-radius:14px;
    padding:14px;
    margin-bottom:10px;
}
div[role="radiogroup"] label p{
    color:white;
    font-weight:600;
}
div[role="radiogroup"] label[data-checked="true"]{
    background:linear-gradient(135deg,#22c55e,#ec4899);
    border:none;
}
div[role="radiogroup"] label[data-checked="true"] p{
    font-weight:900;
}

/* ===== HEADER ===== */
.pro-header{
    background:linear-gradient(135deg,#3b82f6,#be185d);
    padding:22px;
    border-radius:24px;
    color:white;
    text-align:center;
    font-size:28px;
    font-weight:900;
    margin-bottom:30px;
}

/* ===== INPUTS ===== */
div[data-baseweb="input"],
div[data-baseweb="select"],
.stDateInput div{
    background:white!important;
    border:2px solid #7f1d1d!important;
    border-radius:14px!important;
}
input,select{
    color:#111827!important;
    font-weight:600!important;
}

/* ===== BUTTON ===== */
.stButton button{
    background:linear-gradient(135deg,#22c55e,#ec4899);
    color:white;
    font-weight:800;
    border-radius:14px;
    padding:12px;
    border:none;
}

/* ===== METRICS ===== */
div[data-testid="stMetric"]{
    background:white;
    border-radius:20px;
    padding:24px;
    border:2px solid #fecaca;
}
div[data-testid="stMetricValue"]>div{
    font-size:34px;
    font-weight:900;
    color:#16a34a;
}
div[data-testid="stMetricLabel"] p{
    font-weight:800;
    color:#7f1d1d;
}

/* ===== RESUME TABLE ===== */
.resume-table thead tr{
    background:linear-gradient(90deg,#fecaca,#bfdbfe,#fbcfe8);
    font-weight:900;
}
.resume-table td{
    font-weight:700;
    color:#111827;
}

/* ===== RAPPEL CARD ===== */
.alert-card{
    background:linear-gradient(90deg,#dcfce7,#fce7f3);
    border-left:6px solid #16a34a;
    border-radius:18px;
    padding:18px;
    margin-bottom:16px;
    font-weight:600;
}
</style>
""", unsafe_allow_html=True)

# ================= UTILS =================
def clean_phone(p):
    if not p: return ""
    n=re.sub(r'\D','',str(p))
    if n.startswith('0'): n='212'+n[1:]
    if len(n)==9: n='212'+n
    return n

def export_excel(df):
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine="xlsxwriter") as w:
        df.to_excel(w,index=False)
    return buf.getvalue()

# ================= GOOGLE SHEETS =================
def get_client():
    creds=st.secrets["connections"]["gsheets"]
    return gspread.authorize(
        Credentials.from_service_account_info(
            creds,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
    )

client=get_client()

# ================= LOGIN =================
if "auth" not in st.session_state:
    st.markdown('<div class="pro-header">🚀 EMPIRE GATEWAY</div>',unsafe_allow_html=True)
    user=st.text_input("Business ID")
    pwd=st.text_input("Access Key",type="password")
    if st.button("LOGIN",use_container_width=True):
        m=client.open("Master_Admin").sheet1
        dfm=pd.DataFrame(m.get_all_records())
        ok=dfm[(dfm["User"]==user)&(dfm["Password"]==pwd)]
        if not ok.empty:
            r=ok.iloc[0]
            st.session_state.update({
                "auth":True,
                "sheet":r["Sheet_Name"],
                "biz":r["Business_Name"]
            })
            st.rerun()
        else:
            st.error("Login ghalat")
    st.stop()

# ================= LOAD DATA =================
sheet=client.open(st.session_state["sheet"]).sheet1
df=pd.DataFrame(sheet.get_all_records())
today=datetime.now().date()

if not df.empty:
    df["Prix"]=pd.to_numeric(df["Prix"],errors="coerce").fillna(0)
    df["Date Fin"]=pd.to_datetime(df["Date Fin"]).dt.date
    df["Days"]=df["Date Fin"].apply(lambda x:(x-today).days)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">EMPIRE.PRO</div>',unsafe_allow_html=True)
    menu=st.radio("MENU",["GESTION","ANALYTICS","RAPPELS","REÇUS"])
    st.download_button("📥 Export Excel",export_excel(df),"clients.xlsx")
    if st.button("Déconnexion"):
        st.session_state.clear()
        st.rerun()

# ================= HEADER =================
st.markdown(f'<div class="pro-header">{st.session_state["biz"]}</div>',unsafe_allow_html=True)

# ================= GESTION =================
if menu=="GESTION":
    c1,c2=st.columns(2)
    with c1:
        nom=st.text_input("Nom")
        phone=st.text_input("WhatsApp")
        email=st.text_input("Email")
        status=st.selectbox("Status",["Actif","Payé","Annulé"])
    with c2:
        service=st.text_input("Service")
        prix=st.number_input("Prix",0)
        start=st.date_input("Start Date",today)
        months=st.number_input("Months",1)

    if st.button("SAVE",use_container_width=True):
        fin=start+relativedelta(months=int(months))
        row={
            "Nom":nom,
            "Phone":clean_phone(phone),
            "Email":email,
            "Service":service,
            "Prix":prix,
            "Date Debut":start.strftime("%Y-%m-%d"),
            "Months":months,
            "Date Fin":fin.strftime("%Y-%m-%d"),
            "Status":status
        }
        df2=pd.concat([df,pd.DataFrame([row])],ignore_index=True)
        sheet.clear()
        sheet.update([df2.columns.values.tolist()]+df2.astype(str).values.tolist())
        st.success("Client ajouté ✔")
        st.rerun()

    st.dataframe(df,use_container_width=True)

# ================= ANALYTICS =================
elif menu=="ANALYTICS":
    c1,c2,c3=st.columns(3)
    c1.metric("💰 Chiffre d'Affaires",f"{df['Prix'].sum()} DH")
    c2.metric("👥 Actifs",len(df[df["Status"]=="Actif"]))
    c3.metric("⏰ Alertes",len(df[df["Days"]<=3]))

    resume=df.groupby("Service").agg(
        Clients=("Nom","count"),
        CA=("Prix","sum")
    ).reset_index()

    st.markdown("### 📊 Résumé par service")
    st.write(resume.to_html(classes="resume-table",index=False),unsafe_allow_html=True)

    st.plotly_chart(px.bar(df,x="Service",y="Prix",color="Status"),use_container_width=True)

# ================= RAPPELS =================
elif menu=="RAPPELS":
    urg=df[df["Days"]<=3]
    for _,r in urg.iterrows():
        st.markdown(f"""
        <div class="alert-card">
        👤 <b>{r['Nom']}</b><br>
        ⏳ <b>{r['Days']} jours restants</b><br>
        🛠️ {r['Service']}
        </div>
        """,unsafe_allow_html=True)

# ================= REÇUS =================
elif menu=="REÇUS":
    sel=st.selectbox("Client",df["Nom"].unique())
    r=df[df["Nom"]==sel].iloc[0]
    st.code(f"""
REÇU OFFICIEL
Client : {r['Nom']}
Service: {r['Service']}
Prix   : {r['Prix']} DH
Expire : {r['Date Fin']}
Merci pour votre confiance 🙏
""")
