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
    page_title="EMPIRE FROST PRO",
    page_icon="🛡️",
    layout="wide"
)

# ================= LANGUAGES =================
LANGS = {
    "FR": {
        "nav": ["GESTION", "ANALYTICS", "RAPPELS", "REÇUS"],
        "rev": "CHIFFRE D'AFFAIRES",
        "act": "ACTIFS",
        "alert": "ALERTES",
        "export": "Exporter Excel",
        "logout": "Déconnexion",
        "save": "ENREGISTRER",
        "rappel": lambda n,s,d,b:
            f"""Bonjour {n},

Votre abonnement {s} arrive à expiration le {d}.
Merci de renouveler afin d’éviter toute interruption.

— {b}""",
        "recu": lambda n,e,s,p,d,b:
            f"""REÇU OFFICIEL

Client : {n}
Email  : {e}
Service: {s}
Montant: {p} DH
Expiration : {d}

Merci pour votre confiance.
{b}"""
    },
    "EN": {
        "nav": ["MANAGEMENT", "ANALYTICS", "REMINDERS", "RECEIPTS"],
        "rev": "REVENUE",
        "act": "ACTIVE",
        "alert": "ALERTS",
        "export": "Export Excel",
        "logout": "Logout",
        "save": "SAVE",
        "rappel": lambda n,s,d,b:
            f"""Hello {n},

Your {s} subscription expires on {d}.
Please renew to avoid service interruption.

— {b}""",
        "recu": lambda n,e,s,p,d,b:
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
        "nav": ["التسيير", "الإحصائيات", "التنبيهات", "الوصولات"],
        "rev": "المداخيل",
        "act": "النشطون",
        "alert": "تنبيهات",
        "export": "تحميل Excel",
        "logout": "خروج",
        "save": "حفظ",
        "rappel": lambda n,s,d,b:
            f"""السلام عليكم {n}

اشتراك {s} سينتهي بتاريخ {d}.
المرجو التجديد لتفادي انقطاع الخدمة.

— {b}""",
        "recu": lambda n,e,s,p,d,b:
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

# ================= THEME : EMPIRE FROST PRO =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg,#eef2ff,#f8fafc);
    font-family: Inter, sans-serif;
    color:#1f2933;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#f9fafb,#eef2ff);
    border-right:1px solid #e5e7eb;
}

.sidebar-logo {
    background: linear-gradient(135deg,#2563eb,#be185d);
    padding:18px;
    border-radius:16px;
    color:white;
    font-size:22px;
    font-weight:900;
    text-align:center;
    box-shadow:0 10px 30px rgba(37,99,235,.35);
}

/* MENU */
div[role="radiogroup"] label {
    background:white;
    border-radius:14px;
    padding:14px 18px;
    border:1px solid #e5e7eb;
    margin-bottom:10px;
}
div[role="radiogroup"] label:hover {
    background:#eef2ff;
}
div[role="radiogroup"] label[data-checked="true"] {
    background:linear-gradient(135deg,#2563eb,#be185d);
    color:white;
    box-shadow:0 10px 25px rgba(190,24,93,.35);
}

/* HEADER */
.biz-banner {
    background: linear-gradient(135deg,#2563eb,#be185d);
    padding:22px;
    border-radius:22px;
    color:white;
    text-align:center;
    font-size:28px;
    font-weight:900;
    margin-bottom:30px;
}

/* METRICS */
div[data-testid="stMetric"] {
    background:white;
    border-radius:18px;
    padding:22px;
    box-shadow:0 8px 25px rgba(0,0,0,.06);
}
div[data-testid="stMetricLabel"] p {
    color:#334155;
    font-weight:800;
}
div[data-testid="stMetricValue"] > div {
    font-size:34px;
    font-weight:900;
    color:#0f172a;
}

/* INPUTS */
div[data-baseweb="input"],
div[data-baseweb="select"],
.stDateInput div {
    border-radius:14px;
    border:1px solid #c7d2fe;
    background:white;
}

/* TABLE */
.luxury-table thead tr {
    background:linear-gradient(135deg,#2563eb,#be185d);
    color:white;
}
.luxury-table td {
    background:white;
    color:#1f2937;
}

/* RECEIPT */
.receipt-card {
    background:white;
    border-radius:20px;
    padding:26px;
    border-left:6px solid #be185d;
    box-shadow:0 10px 25px rgba(0,0,0,.08);
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

# ================= LANGUAGE =================
lang = st.selectbox("🌍 Language", ["FR","EN","AR"])
T = LANGS[lang]

# ================= LOAD DATA =================
sheet = client.open(st.secrets["sheet_name"]).sheet1
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
st.markdown("<div class='biz-banner'>FATIMA ELBOUHALI PRO</div>",unsafe_allow_html=True)

# ================= ANALYTICS =================
if menu == T["nav"][1]:
    c1,c2,c3 = st.columns(3)
    c1.metric(T["rev"], f"{df['Prix'].sum()} DH")
    c2.metric(T["act"], len(df[df["Status"]=="Actif"]))
    c3.metric(T["alert"], len(df[df["Days"]<=3]))

    resume = df.groupby("Service").agg(
        Clients=("Nom","count"),
        CA=("Prix","sum")
    ).reset_index()

    st.dataframe(resume,use_container_width=True)
    st.plotly_chart(px.bar(df,x="Service",y="Prix",color="Status"),use_container_width=True)

# ================= RAPPELS =================
elif menu == T["nav"][2]:
    urg = df[df["Days"]<=3]
    for _,r in urg.iterrows():
        msg = T["rappel"](r["Nom"],r["Service"],r["Date Fin"],"EMPIRE.PRO")
        link = f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote(msg)}"
        st.link_button(f"📲 {r['Nom']}", link)

# ================= REÇUS =================
elif menu == T["nav"][3]:
    sel = st.selectbox("Client", df["Nom"].unique())
    r = df[df["Nom"]==sel].iloc[0]
    recu = T["recu"](r["Nom"],r["Email"],r["Service"],r["Prix"],r["Date Fin"],"EMPIRE.PRO")
    st.markdown(f"<div class='receipt-card'><pre>{recu}</pre></div>",unsafe_allow_html=True)
    wa = f"https://wa.me/{clean_phone(r['Phone'])}?text={urllib.parse.quote(recu)}"
    st.link_button("📲 WhatsApp", wa)
