# ================= IMPORTS =================
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
import urllib.parse
import io
import re

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="EMPIRE SIGNATURE PRO",
    page_icon="🛡️",
    layout="wide"
)

# ================= THEME (WOW EFFECT) =================
st.markdown("""
<style>
.stApp{
    background: radial-gradient(circle at top,#0f172a,#020617);
    color:#e5e7eb;
    font-family:Inter,sans-serif;
}
[data-testid="stSidebar"]{
    background:#020617;
    border-right:1px solid #1e293b;
}
.sidebar-logo{
    background:linear-gradient(135deg,#6366f1,#ec4899);
    padding:20px;
    border-radius:18px;
    text-align:center;
    color:white;
    font-size:22px;
    font-weight:900;
    box-shadow:0 0 30px rgba(236,72,153,.6);
}
div[role="radiogroup"] label{
    background:#020617;
    border-radius:14px;
    padding:14px;
    border:1px solid #1e293b;
    margin-bottom:8px;
}
div[role="radiogroup"] label[data-checked="true"]{
    background:linear-gradient(135deg,#6366f1,#ec4899);
    box-shadow:0 0 20px rgba(99,102,241,.7);
}
.biz-banner{
    background:linear-gradient(135deg,#6366f1,#ec4899);
    padding:26px;
    border-radius:24px;
    text-align:center;
    color:white;
    font-size:30px;
    font-weight:900;
    margin-bottom:30px;
    box-shadow:0 0 40px rgba(99,102,241,.7);
}
div[data-testid="stMetric"]{
    background:#020617;
    border-radius:20px;
    padding:24px;
    border:1px solid #1e293b;
}
div[data-testid="stMetricValue"]>div{
    font-size:36px;
    font-weight:900;
    color:white;
}
input,textarea,select{
    color:white!important;
    font-weight:700!important;
}
.luxury-table thead tr{
    background:linear-gradient(135deg,#6366f1,#ec4899);
    color:white;
    font-weight:900;
}
.luxury-table td{
    padding:14px;
    background:#020617;
    color:#e5e7eb;
    text-align:center;
    border-bottom:1px solid #1e293b;
}
.receipt-card{
    background:#020617;
    padding:28px;
    border-radius:22px;
    border:1px solid #6366f1;
    box-shadow:0 0 25px rgba(99,102,241,.6);
}
</style>
""", unsafe_allow_html=True)

# ================= LANGUAGE SYSTEM =================
LANG = {
 "FR":{
  "login":"CONNEXION","id":"Business ID","key":"Access Key",
  "gestion":"GESTION","analytics":"ANALYTICS","rappels":"RAPPELS","recus":"REÇUS",
  "revenue":"REVENU","actifs":"ACTIFS","alertes":"ALERTES",
  "save":"ENREGISTRER","logout":"Déconnexion",
  "rappel_msg":"""👋 Bonjour {nom},

Votre abonnement *{service}* arrive à expiration le *{date}*.

Merci de procéder au renouvellement afin d’éviter toute interruption.

💼 {biz}
""",
  "recu_msg":"""🧾 REÇU OFFICIEL

Client : {nom}
Service : {service}
Montant : {prix} DH
Expiration : {date}

Merci pour votre confiance.
💼 {biz}
"""
 },
 "EN":{
  "login":"LOGIN","id":"Business ID","key":"Access Key",
  "gestion":"MANAGEMENT","analytics":"ANALYTICS","rappels":"REMINDERS","recus":"RECEIPTS",
  "revenue":"REVENUE","actifs":"ACTIVE","alertes":"ALERTS",
  "save":"SAVE","logout":"Logout",
  "rappel_msg":"""👋 Hello {nom},

Your subscription *{service}* will expire on *{date}*.

Please renew to avoid service interruption.

💼 {biz}
""",
  "recu_msg":"""🧾 OFFICIAL RECEIPT

Client : {nom}
Service : {service}
Amount : {prix} DH
Expiry : {date}

Thank you for your trust.
💼 {biz}
"""
 },
 "AR":{
  "login":"تسجيل الدخول","id":"هوية العمل","key":"مفتاح الدخول",
  "gestion":"إدارة","analytics":"إحصائيات","rappels":"تنبيهات","recus":"وصولات",
  "revenue":"المداخيل","actifs":"نشط","alertes":"تنبيه",
  "save":"حفظ","logout":"خروج",
  "rappel_msg":"""👋 السلام عليكم {nom}

نخبركم أن اشتراك *{service}* سينتهي بتاريخ *{date}*.

المرجو التجديد لتفادي انقطاع الخدمة.

💼 {biz}
""",
  "recu_msg":"""🧾 وصل رسمي

الزبون : {nom}
الخدمة : {service}
المبلغ : {prix} درهم
تاريخ الانتهاء : {date}

شكرا لثقتكم.
💼 {biz}
"""
 }
}

# ================= UTILS =================
def clean_phone(p):
    if not p: return ""
    n=re.sub(r'\D','',str(p))
    if n.startswith('0'): n='212'+n[1:]
    if len(n)==9: n='212'+n
    return n

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
    L=LANG[lang]

    st.markdown('<div class="biz-banner">🛡️ EMPIRE SIGNATURE PRO</div>',unsafe_allow_html=True)
    u=st.text_input(L["id"])
    p=st.text_input(L["key"],type="password")
    if st.button(L["login"],use_container_width=True):
        m=client.open("Master_Admin").sheet1
        dfm=pd.DataFrame(m.get_all_records())
        ok=dfm[(dfm["User"]==u)&(dfm["Password"]==p)]
        if not ok.empty:
            r=ok.iloc[0]
            st.session_state.update({
                "auth":True,
                "lang":lang,
                "sheet":r["Sheet_Name"],
                "biz":r["Business_Name"]
            })
            st.rerun()
    st.stop()

# ================= LOAD DATA =================
L=LANG[st.session_state["lang"]]
sheet=client.open(st.session_state["sheet"]).sheet1
df=pd.DataFrame(sheet.get_all_records())
today=datetime.now().date()

if not df.empty:
    df["Prix"]=pd.to_numeric(df["Prix"],errors="coerce").fillna(0)
    df["Date Fin"]=pd.to_datetime(df["Date Fin"],errors="coerce").dt.date
    df["Days"]=df["Date Fin"].apply(lambda x:(x-today).days if pd.notnull(x) else 0)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">EMPIRE.PRO</div>',unsafe_allow_html=True)
    menu=st.radio("MENU",[L["gestion"],L["analytics"],L["rappels"],L["recus"]])
    if st.button(L["logout"]):
        st.session_state.clear()
        st.rerun()

# ================= HEADER =================
st.markdown(f'<div class="biz-banner">👤 {st.session_state["biz"]}</div>',unsafe_allow_html=True)

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

    if st.button(L["save"],use_container_width=True):
        fin=start+relativedelta(months=int(months))
        new={
            "Nom":nom,"Phone":clean_phone(phone),"Email":email,
            "Service":service,"Prix":prix,
            "Date Debut":start.strftime("%Y-%m-%d"),
            "Months":months,
            "Date Fin":fin.strftime("%Y-%m-%d"),
            "Status":status
        }
        df2=pd.concat([df,pd.DataFrame([new])],ignore_index=True)
        sheet.clear()
        sheet.update([df2.columns.tolist()]+df2.astype(str).values.tolist())
        st.success("✔ Saved")
        st.rerun()
    st.dataframe(df,use_container_width=True)

# ================= ANALYTICS =================
elif menu==L["analytics"]:
    c1,c2,c3=st.columns(3)
    c1.metric(L["revenue"],f"{df['Prix'].sum()} DH")
    c2.metric(L["actifs"],len(df[df["Status"]=="Actif"]))
    c3.metric(L["alertes"],len(df[df["Days"]<=3]))
    st.plotly_chart(px.bar(df,x="Service",y="Prix",color="Status"),use_container_width=True)

# ================= RAPPELS =================
elif menu==L["rappels"]:
    urg=df[df["Days"]<=3]
    for _,r in urg.iterrows():
        msg=L["rappel_msg"].format(
            nom=r["Nom"],service=r["Service"],
            date=r["Date Fin"],biz=st.session_state["biz"]
        )
        st.link_button("📲 WhatsApp",
            f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote(msg)}"
        )

# ================= REÇUS =================
elif menu==L["recus"]:
    sel=st.selectbox("Client",df["Nom"].unique())
    r=df[df["Nom"]==sel].iloc[0]
    rec=L["recu_msg"].format(
        nom=r["Nom"],service=r["Service"],
        prix=r["Prix"],date=r["Date Fin"],
        biz=st.session_state["biz"]
    )
    st.markdown(f'<div class="receipt-card"><pre>{rec}</pre></div>',unsafe_allow_html=True)
    st.link_button("📲 WhatsApp",
        f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote(rec)}"
    )
