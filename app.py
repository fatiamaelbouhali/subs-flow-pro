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

# ================= CONFIG =================
st.set_page_config(
    page_title="EMPIRE SIGNATURE PRO",
    page_icon="🛡️",
    layout="wide"
)

# ================= LANGUAGES =================
LANGS = {
    "FR": {
        "login_title": "EMPIRE SIGNATURE PRO",
        "ident": "Business ID",
        "pass": "Access Key",
        "login": "CONNEXION",
        "nav": ["GESTION", "ANALYTICS", "RAPPELS", "REÇUS"],
        "add": "AJOUTER UN CLIENT",
        "save": "ENREGISTRER",
        "rev": "CHIFFRE D'AFFAIRES",
        "act": "ACTIFS",
        "alert": "ALERTES",
        "export": "Exporter Excel",
        "logout": "Déconnexion",
        "rappel_msg": lambda n,s,d,b:
            f"""Bonjour {n},

Votre abonnement {s} arrive à expiration le {d}.
Merci de procéder au renouvellement afin d’éviter toute interruption.

— {b}""",
        "recu_msg": lambda n,e,s,p,d,b:
            f"""REÇU OFFICIEL

Client : {n}
Email  : {e}
Service: {s}
Montant: {p} DH
Expiration: {d}

Merci pour votre confiance.
{b}"""
    },
    "EN": {
        "login_title": "EMPIRE SIGNATURE PRO",
        "ident": "Business ID",
        "pass": "Access Key",
        "login": "LOGIN",
        "nav": ["MANAGEMENT", "ANALYTICS", "REMINDERS", "RECEIPTS"],
        "add": "ADD CLIENT",
        "save": "SAVE",
        "rev": "REVENUE",
        "act": "ACTIVE",
        "alert": "ALERTS",
        "export": "Export Excel",
        "logout": "Logout",
        "rappel_msg": lambda n,s,d,b:
            f"""Hello {n},

Your {s} subscription will expire on {d}.
Please renew to avoid service interruption.

— {b}""",
        "recu_msg": lambda n,e,s,p,d,b:
            f"""OFFICIAL RECEIPT

Client : {n}
Email  : {e}
Service: {s}
Amount : {p} DH
Expiry : {d}

Thank you for your trust.
{b}"""
    },
    "AR": {
        "login_title": "EMPIRE SIGNATURE PRO",
        "ident": "معرّف النشاط",
        "pass": "كلمة المرور",
        "login": "دخول",
        "nav": ["التسيير", "الإحصائيات", "التنبيهات", "الوصولات"],
        "add": "إضافة زبون",
        "save": "حفظ",
        "rev": "المداخيل",
        "act": "النشطون",
        "alert": "تنبيهات",
        "export": "تحميل Excel",
        "logout": "خروج",
        "rappel_msg": lambda n,s,d,b:
            f"""السلام عليكم {n}

اشتراك {s} سينتهي بتاريخ {d}.
المرجو التجديد لتفادي انقطاع الخدمة.

— {b}""",
        "recu_msg": lambda n,e,s,p,d,b:
            f"""وصل رسمي

الزبون : {n}
البريد : {e}
الخدمة : {s}
المبلغ : {p} درهم
تاريخ الانتهاء : {d}

شكراً لثقتكم.
{b}"""
    }
}

# ================= CSS (PRO – EYE CATCHING) =================
st.markdown("""
<style>
.stApp { background:#f8fafc; font-family:Inter,sans-serif; color:#0f172a; }
[data-testid="stSidebar"] { background:white; border-right:1px solid #e5e7eb; }
.sidebar-logo {
 background:linear-gradient(135deg,#4f46e5,#ec4899);
 padding:18px;border-radius:16px;text-align:center;
 color:white;font-size:22px;font-weight:900;
 box-shadow:0 10px 30px rgba(79,70,229,.4);
}
.biz-banner {
 background:linear-gradient(135deg,#4f46e5,#ec4899);
 padding:22px;border-radius:22px;color:white;
 text-align:center;font-size:28px;font-weight:900;
 margin-bottom:30px;
}
div[data-testid="stMetric"] {
 background:white;border-radius:18px;padding:22px;
 box-shadow:0 8px 25px rgba(0,0,0,.06);
}
div[data-testid="stMetricLabel"] p {
 color:#6366f1;font-weight:800;
}
div[data-testid="stMetricValue"] > div {
 font-size:34px;font-weight:900;color:#0f172a;
}
div[data-baseweb="input"],div[data-baseweb="select"],.stDateInput div {
 border-radius:14px;border:1px solid #d1d5db;background:white;
}
.receipt-card {
 background:white;padding:26px;border-radius:20px;
 border:2px dashed #6366f1;
}
</style>
""", unsafe_allow_html=True)

# ================= UTILS =================
def clean_phone(p):
    if not p: return ""
    n = re.sub(r"\D","",str(p))
    if n.startswith("0") and len(n)==10: n="212"+n[1:]
    if len(n)==9: n="212"+n
    return n

def export_excel(df):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as w:
        df.to_excel(w,index=False)
    return out.getvalue()

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

# ================= LANGUAGE SELECT =================
lang = st.selectbox("🌍 Language", ["FR","EN","AR"])
T = LANGS[lang]

# ================= LOGIN =================
if "auth" not in st.session_state:
    st.markdown(f"<div class='biz-banner'>{T['login_title']}</div>",unsafe_allow_html=True)
    u = st.text_input(T["ident"])
    p = st.text_input(T["pass"], type="password")
    if st.button(T["login"]):
        master = client.open("Master_Admin").sheet1
        mdf = pd.DataFrame(master.get_all_records())
        ok = mdf[(mdf["User"]==u)&(mdf["Password"]==p)]
        if not ok.empty:
            r = ok.iloc[0]
            st.session_state.update({
                "auth":True,
                "biz":r["Business_Name"],
                "sheet":r["Sheet_Name"]
            })
            st.rerun()
        else:
            st.error("Access denied")
    st.stop()

# ================= LOAD DATA =================
sheet = client.open(st.session_state["sheet"]).sheet1
df = pd.DataFrame(sheet.get_all_records())
today = datetime.now().date()

if not df.empty:
    df["Prix"] = pd.to_numeric(df["Prix"], errors="coerce").fillna(0)
    df["Date Fin"] = pd.to_datetime(df["Date Fin"]).dt.date
    df["Days"] = df["Date Fin"].apply(lambda x:(x-today).days)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("<div class='sidebar-logo'>EMPIRE.PRO</div>",unsafe_allow_html=True)
    menu = st.radio("MENU", T["nav"])
    st.download_button(T["export"], export_excel(df), "clients.xlsx")
    if st.button(T["logout"]):
        st.session_state.clear()
        st.rerun()

# ================= HEADER =================
st.markdown(f"<div class='biz-banner'>{st.session_state['biz']}</div>",unsafe_allow_html=True)

# ================= GESTION =================
if menu == T["nav"][0]:
    n = st.text_input("Nom")
    ph = st.text_input("WhatsApp")
    em = st.text_input("Email")
    s = st.text_input("Service")
    pr = st.number_input("Prix",0)
    d = st.date_input("Start", today)
    m = st.number_input("Months",1)
    stt = st.selectbox("Status",["Actif","Payé","En Attente","Annulé"])
    if st.button(T["save"]):
        fin = d + relativedelta(months=int(m))
        row = {
            "Nom":n,"Phone":clean_phone(ph),"Email":em,
            "Service":s,"Prix":pr,
            "Date Debut":str(d),"Months":m,
            "Date Fin":str(fin),"Status":stt
        }
        df2 = pd.concat([df,pd.DataFrame([row])])
        sheet.clear()
        sheet.update([df2.columns.tolist()]+df2.astype(str).values.tolist())
        st.success("OK")
        st.rerun()
    st.dataframe(df,use_container_width=True)

# ================= ANALYTICS =================
elif menu == T["nav"][1]:
    c1,c2,c3 = st.columns(3)
    c1.metric(T["rev"], f"{df['Prix'].sum()} DH")
    c2.metric(T["act"], len(df[df["Status"]=="Actif"]))
    c3.metric(T["alert"], len(df[df["Days"]<=3]))
    resume = df.groupby("Service").agg(Clients=("Nom","count"),CA=("Prix","sum")).reset_index()
    st.dataframe(resume,use_container_width=True)
    st.plotly_chart(px.bar(df,x="Service",y="Prix",color="Status"),use_container_width=True)

# ================= RAPPELS =================
elif menu == T["nav"][2]:
    urg = df[df["Days"]<=3]
    for _,r in urg.iterrows():
        msg = T["rappel_msg"](r["Nom"],r["Service"],r["Date Fin"],st.session_state["biz"])
        link = f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote(msg)}"
        st.link_button(f"📲 {r['Nom']}", link)

# ================= REÇUS =================
elif menu == T["nav"][3]:
    sel = st.selectbox("Client", df["Nom"].unique())
    r = df[df["Nom"]==sel].iloc[0]
    recu = T["recu_msg"](r["Nom"],r["Email"],r["Service"],r["Prix"],r["Date Fin"],st.session_state["biz"])
    st.markdown(f"<div class='receipt-card'><pre>{recu}</pre></div>",unsafe_allow_html=True)
    wa = f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote(recu)}"
    st.link_button("📲 WhatsApp", wa)
