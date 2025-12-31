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
st.set_page_config(page_title="EMPIRE.PRO", page_icon="🛡️", layout="wide")

# ================= THEME MOTARD LIGHT =================
st.markdown("""
<style>
.stApp{
 background:linear-gradient(180deg,#f8fafc,#eef2ff);
 color:#0f172a;
 font-family:Inter,sans-serif;
}
[data-testid="stSidebar"]{
 background:linear-gradient(180deg,#0f172a,#020617);
}
.sidebar-logo{
 background:linear-gradient(135deg,#22c55e,#ec4899);
 padding:18px;border-radius:18px;
 text-align:center;
 color:white;font-size:22px;font-weight:900;
 box-shadow:0 10px 30px rgba(0,0,0,.3);
}
.pro-header{
 background:linear-gradient(135deg,#22c55e,#38bdf8,#ec4899);
 padding:22px;border-radius:28px;
 text-align:center;
 font-size:28px;font-weight:900;
 color:white;
 margin-bottom:30px;
 box-shadow:0 12px 30px rgba(0,0,0,.25);
}
div[data-testid="stMetric"]{
 background:white;
 border-radius:22px;
 padding:22px;
 box-shadow:0 10px 25px rgba(0,0,0,.08);
}
div[data-testid="stMetricValue"]{
 color:#16a34a!important;
 font-size:38px;font-weight:900;
}
div[data-testid="stMetricLabel"]{
 color:#ec4899!important;
 font-weight:800;
}
div[data-baseweb="input"],div[data-baseweb="select"],.stDateInput div{
 background:white!important;
 border:1px solid #c7d2fe!important;
 border-radius:14px!important;
}
input,select,textarea{color:#0f172a!important;font-weight:700;}
button{
 background:linear-gradient(135deg,#22c55e,#ec4899)!important;
 color:white!important;font-weight:900!important;
 border-radius:16px!important;
}
thead tr{background:#22c55e!important;color:white!important;}
tbody tr td{background:white!important;color:#0f172a!important;}
.rappel-card{
 background:white;
 border-left:6px solid #22c55e;
 padding:18px 22px;border-radius:18px;
 margin-bottom:14px;
 box-shadow:0 8px 20px rgba(0,0,0,.1);
}
.receipt{
 background:white;
 border:2px dashed #ec4899;
 padding:26px;border-radius:22px;
 font-size:17px;font-weight:700;
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
    buffer=io.BytesIO()
    with pd.ExcelWriter(buffer,engine="xlsxwriter") as w:
        df.to_excel(w,index=False,sheet_name="Clients")
    return buffer.getvalue()

# ================= LANG =================
LANG={
 "FR":{
  "gestion":"GESTION","analytics":"ANALYTICS","rappels":"RAPPELS","recus":"REÇUS",
  "ca":"💰 CHIFFRE D’AFFAIRES","actifs":"👥 ACTIFS","alertes":"🚨 ALERTES",
  "rappel":"Bonjour {nom}, votre abonnement {service} expire le {date}.",
  "merci":"Merci pour votre confiance."
 },
 "EN":{
  "gestion":"MANAGEMENT","analytics":"ANALYTICS","rappels":"REMINDERS","recus":"RECEIPTS",
  "ca":"💰 REVENUE","actifs":"👥 ACTIVE","alertes":"🚨 ALERTS",
  "rappel":"Hello {nom}, your {service} subscription expires on {date}.",
  "merci":"Thank you for your trust."
 },
 "AR":{
  "gestion":"الإدارة","analytics":"الإحصائيات","rappels":"التنبيهات","recus":"الوصولات",
  "ca":"💰 رقم المعاملات","actifs":"👥 نشط","alertes":"🚨 تنبيهات",
  "rappel":"السلام عليكم {nom}، اشتراك {service} سينتهي في {date}.",
  "merci":"شكراً لثقتكم."
 }
}

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
    lang=st.selectbox("🌍 Language",["FR","EN","AR"])
    st.markdown("<div class='pro-header'>EMPIRE.PRO</div>",unsafe_allow_html=True)
    user=st.text_input("Business ID")
    pwd=st.text_input("Access Key",type="password")
    if st.button("LOGIN",use_container_width=True):
        master=client.open("Master_Admin").sheet1
        mdf=pd.DataFrame(master.get_all_records())
        ok=mdf[(mdf["User"]==user)&(mdf["Password"]==pwd)]
        if not ok.empty:
            r=ok.iloc[0]
            st.session_state.update({
             "auth":True,
             "sheet":r["Sheet_Name"],
             "biz":r["Business_Name"],
             "lang":lang
            })
            st.rerun()
        else: st.error("Access denied")
    st.stop()

L=LANG[st.session_state["lang"]]

# ================= LOAD DATA =================
sheet=client.open(st.session_state["sheet"]).sheet1
df=pd.DataFrame(sheet.get_all_records())
today=datetime.now().date()

if not df.empty:
    df["Prix"]=pd.to_numeric(df["Prix"],errors="coerce").fillna(0)
    df["Date Fin"]=pd.to_datetime(df["Date Fin"],errors="coerce").dt.date
    df["Days"]=df["Date Fin"].apply(lambda x:(x-today).days if pd.notnull(x) else 0)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("<div class='sidebar-logo'>EMPIRE.PRO</div>",unsafe_allow_html=True)
    menu=st.radio("MENU",[L["gestion"],L["analytics"],L["rappels"],L["recus"]])
    st.download_button("📥 Export Excel",export_excel(df),"clients.xlsx")
    if st.button("Déconnexion"):
        st.session_state.clear(); st.rerun()

# ================= HEADER =================
st.markdown(f"<div class='pro-header'>{st.session_state['biz']}</div>",unsafe_allow_html=True)

# ================= GESTION =================
if menu==L["gestion"]:
    c1,c2=st.columns(2)
    with c1:
        nom=st.text_input("Nom")
        phone=st.text_input("WhatsApp")
        email=st.text_input("Email")
        status=st.selectbox("Status",["Actif","Payé","En Attente","Annulé"])
    with c2:
        service=st.text_input("Service")
        prix=st.number_input("Prix",0)
        start=st.date_input("Start",today)
        months=st.number_input("Months",1)
    if st.button("SAVE",use_container_width=True):
        fin=start+relativedelta(months=int(months))
        new={
         "Nom":nom,"Phone":clean_phone(phone),"Email":email,
         "Service":service,"Prix":prix,
         "Date Debut":start.strftime("%Y-%m-%d"),
         "Months":months,"Date Fin":fin.strftime("%Y-%m-%d"),
         "Status":status
        }
        df2=pd.concat([df,pd.DataFrame([new])],ignore_index=True)
        sheet.clear()
        sheet.update([df2.columns.values.tolist()]+df2.astype(str).values.tolist())
        st.success("Client ajouté ✔️")
        st.rerun()
    st.dataframe(df,use_container_width=True)

# ================= ANALYTICS =================
elif menu==L["analytics"]:
    c1,c2,c3=st.columns(3)
    c1.metric(L["ca"],f"{df['Prix'].sum()} DH")
    c2.metric(L["actifs"],len(df[df["Status"]=="Actif"]))
    c3.metric(L["alertes"],len(df[df["Days"]<=3]))
    resume=df.groupby("Service").agg(Clients=("Nom","count"),CA=("Prix","sum")).reset_index()
    st.dataframe(resume,use_container_width=True)
    st.plotly_chart(px.bar(df,x="Service",y="Prix",color="Status"),use_container_width=True)

# ================= RAPPELS =================
elif menu==L["rappels"]:
    urg=df[(df["Days"]<=3)&(df["Status"]=="Actif")]
    if urg.empty: st.success("Aucun rappel")
    for _,r in urg.iterrows():
        st.markdown(f"""
        <div class="rappel-card">
        👤 <b>{r['Nom']}</b><br>
        ⏳ <b>{r['Days']} jours restants</b><br>
        🛠️ {r['Service']}
        </div>
        """,unsafe_allow_html=True)
        msg=f"{L['rappel'].format(nom=r['Nom'],service=r['Service'],date=r['Date Fin'])}\n{L['merci']}"
        wa=f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote(msg)}"
        st.link_button("📲 WhatsApp",wa)

# ================= REÇUS =================
elif menu==L["recus"]:
    sel=st.selectbox("Client",df["Nom"].unique())
    r=df[df["Nom"]==sel].iloc[0]
    receipt=f"""
🧾 REÇU — {st.session_state['biz']}

Client : {r['Nom']}
Service : {r['Service']}
Montant : {r['Prix']} DH
Expiration : {r['Date Fin']}

{L['merci']}
"""
    st.markdown(f"<div class='receipt'>{receipt}</div>",unsafe_allow_html=True)
    wa=f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote(receipt)}"
    st.link_button("📲 Envoyer WhatsApp",wa)
