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

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ================= CONFIG =================
st.set_page_config(page_title="EMPIRE PRO", page_icon="🚀", layout="wide")

# ================= CSS =================
st.markdown("""
<style>
.stApp { background-color:#f8fafc; font-family:Inter,sans-serif; }
[data-testid="stSidebar"] { background:#fff; border-right:1px solid #e5e7eb; }
.sidebar-logo {
 background:linear-gradient(135deg,#6366f1,#ec4899);
 padding:20px;border-radius:16px;
 text-align:center;color:white;
 font-size:22px;font-weight:800;
}
div[role="radiogroup"] label {
 background:white;border-radius:12px;
 padding:12px 16px;border:1px solid #e5e7eb;
 margin-bottom:8px;
}
div[role="radiogroup"] label[data-checked="true"] {
 background:#6366f1;
}
div[role="radiogroup"] label[data-checked="true"] p {
 color:white;font-weight:700;
}
div[data-baseweb="input"],div[data-baseweb="select"],.stDateInput div {
 border-radius:12px !important;border:1px solid #e5e7eb !important;
}
div[data-testid="stMetric"] {
 background:white;padding:24px;border-radius:16px;
 box-shadow:0 8px 24px rgba(0,0,0,.06);
}
</style>
""", unsafe_allow_html=True)

# ================= UTILS =================
def clean_phone(p):
    if not p: return ""
    n = re.sub(r'\D','',str(p))
    if n.startswith('0') and len(n)==10: n='212'+n[1:]
    if len(n)==9: n='212'+n
    return n

def export_excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Clients")
    return buffer.getvalue()

def export_pdf_receipt(client_row, biz_name):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    text = c.beginText(40, 800)

    text.setFont("Helvetica-Bold", 16)
    text.textLine(biz_name)
    text.textLine("")

    text.setFont("Helvetica", 12)
    text.textLine(f"Client : {client_row['Nom']}")
    text.textLine(f"Email  : {client_row['Email']}")
    text.textLine(f"Service: {client_row['Service']}")
    text.textLine(f"Prix   : {client_row['Prix']} DH")
    text.textLine(f"Expire : {client_row['Date Fin']}")
    text.textLine("")
    text.textLine("Merci pour votre confiance 🙏")

    c.drawText(text)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

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
    st.markdown("""
    <div style="background:linear-gradient(135deg,#6366f1,#ec4899);
    padding:30px;border-radius:20px;text-align:center;
    color:white;font-size:30px;font-weight:800;">
    🚀 EMPIRE GATEWAY
    </div>
    """, unsafe_allow_html=True)

    _, c, _ = st.columns([1,2,1])
    with c:
        user = st.text_input("Business ID")
        pwd = st.text_input("Access Key", type="password")
        if st.button("LOGIN", use_container_width=True):
            master = client.open("Master_Admin").sheet1
            mdf = pd.DataFrame(master.get_all_records())
            ok = mdf[(mdf["User"]==user)&(mdf["Password"]==pwd)]
            if not ok.empty:
                r = ok.iloc[0]
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
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# ================= HEADER =================
st.markdown(f"""
<div style="background:linear-gradient(135deg,#6366f1,#ec4899);
padding:18px;border-radius:18px;color:white;
text-align:center;font-size:26px;font-weight:800;margin-bottom:24px;">
👤 {st.session_state["biz"]}
</div>
""", unsafe_allow_html=True)

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
        st.success("Client tzed ✔️")
        st.rerun()

    st.dataframe(df,use_container_width=True)

# ================= ANALYTICS =================
elif menu=="ANALYTICS":
    c1,c2,c3=st.columns(3)
    c1.metric("Revenue",f"{df['Prix'].sum()} DH")
    c2.metric("Actifs",len(df[df["Status"]=="Actif"]))
    c3.metric("Alerts",len(df[df["Days"]<=3]))

    resume = df.groupby("Service").agg(
        Clients=("Nom","count"),
        CA=("Prix","sum")
    ).reset_index()

    st.markdown("### 📊 Résumé par service")
    st.dataframe(resume, use_container_width=True)

    st.plotly_chart(px.bar(df,x="Service",y="Prix",color="Status"),use_container_width=True)

# ================= RAPPELS =================
elif menu=="RAPPELS":
    urg=df[df["Days"]<=3]
    if urg.empty:
        st.success("Aucun rappel")
    else:
        for _,r in urg.iterrows():
            msg=f"Salam {r['Nom']} 👋\nL'abonnement {r['Service']} ghadi يسالي f {r['Date Fin']}.\nMerci 🙏"
            link=f"https://wa.me/{clean_phone(r['Phone'])}?text={msg.replace(' ','%20')}"
            c1,c2=st.columns([3,1])
            c1.warning(f"{r['Nom']} | {r['Days']} jours")
            c2.link_button("📲 WhatsApp",link)

# ================= REÇUS =================
elif menu=="REÇUS":
    sel=st.selectbox("Client",df["Nom"].unique())
    r=df[df["Nom"]==sel].iloc[0]

    receipt=f"""
REÇU
Client: {r['Nom']}
Email: {r['Email']}
Service: {r['Service']}
Prix: {r['Prix']} DH
Expire: {r['Date Fin']}
"""
    st.code(receipt)

    pdf = export_pdf_receipt(r, st.session_state["biz"])
    st.download_button("📄 Télécharger PDF", pdf, "recu.pdf")

    wa_link=f"https://wa.me/{clean_phone(r['Phone'])}?text={receipt.replace(' ','%20')}"
    st.link_button("📲 Envoyer WhatsApp", wa_link)
