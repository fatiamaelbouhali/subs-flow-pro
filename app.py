# ================= IMPORTS =================
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
import re, io, requests, json
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
</style>
""", unsafe_allow_html=True)

# ================= UTILS =================
def clean_phone(p):
    if not p: return ""
    n = re.sub(r'\D','',str(p))
    if n.startswith('0') and len(n)==10: n='212'+n[1:]
    if len(n)==9: n='212'+n
    return n

def send_whatsapp_api(phone, message):
    token = st.secrets["whatsapp"]["TOKEN"]
    phone_id = st.secrets["whatsapp"]["PHONE_ID"]

    url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": message}
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    return r.status_code == 200, r.text

def export_excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    return buffer.getvalue()

def export_pdf_receipt(client_row, biz_name):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    t = c.beginText(40, 800)
    t.setFont("Helvetica-Bold", 16)
    t.textLine(biz_name)
    t.textLine("")
    t.setFont("Helvetica", 12)
    t.textLine(f"Client : {client_row['Nom']}")
    t.textLine(f"Email  : {client_row['Email']}")
    t.textLine(f"Service: {client_row['Service']}")
    t.textLine(f"Prix   : {client_row['Prix']} DH")
    t.textLine(f"Expire : {client_row['Date Fin']}")
    t.textLine("")
    t.textLine("Merci pour votre confiance 🙏")
    c.drawText(t)
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
    st.markdown("<div class='sidebar-logo'>🚀 EMPIRE GATEWAY</div>", unsafe_allow_html=True)
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
        st.session_state.clear(); st.rerun()

# ================= HEADER =================
st.markdown(f"<h2>{st.session_state['biz']}</h2>", unsafe_allow_html=True)

# ================= GESTION =================
if menu=="GESTION":
    nom=st.text_input("Nom")
    phone=st.text_input("WhatsApp")
    email=st.text_input("Email")
    service=st.text_input("Service")
    prix=st.number_input("Prix",0)
    status=st.selectbox("Status",["Actif","Payé","En Attente","Annulé","Expiré"])
    start=st.date_input("Start Date",today)
    months=st.number_input("Months",1)

    if st.button("SAVE",use_container_width=True):
        fin=start+relativedelta(months=int(months))
        row={
            "Nom":nom,"Phone":clean_phone(phone),"Email":email,
            "Service":service,"Prix":prix,
            "Date Debut":start.strftime("%Y-%m-%d"),
            "Months":months,"Date Fin":fin.strftime("%Y-%m-%d"),
            "Status":status
        }
        df2=pd.concat([df,pd.DataFrame([row])],ignore_index=True)
        sheet.clear()
        sheet.update([df2.columns.values.tolist()]+df2.astype(str).values.tolist())
        st.success("Client ajouté")
        st.rerun()

    st.dataframe(df,use_container_width=True)

# ================= ANALYTICS =================
elif menu=="ANALYTICS":
    st.metric("Revenue",f"{df['Prix'].sum()} DH")
    resume=df.groupby("Service").agg(Clients=("Nom","count"),CA=("Prix","sum")).reset_index()
    st.dataframe(resume,use_container_width=True)
    st.plotly_chart(px.bar(df,x="Service",y="Prix",color="Status"),use_container_width=True)

# ================= RAPPELS =================
elif menu=="RAPPELS":
    urg=df[(df["Days"]<=3)&(df["Status"]=="Actif")]
    for _,r in urg.iterrows():
        msg=f"Salam {r['Nom']} 👋\nL'abonnement {r['Service']} ghadi يسالي f {r['Date Fin']}.\nMerci 🙏"
        if st.button(f"📲 Envoyer à {r['Nom']}"):
            ok,resp=send_whatsapp_api(clean_phone(r["Phone"]),msg)
            if ok: st.success("Message envoyé")
            else: st.error(resp)

# ================= REÇUS =================
elif menu=="REÇUS":
    sel=st.selectbox("Client",df["Nom"].unique())
    r=df[df["Nom"]==sel].iloc[0]
    st.code(f"{r['Nom']} | {r['Service']} | {r['Prix']} DH | {r['Date Fin']}")
    pdf=export_pdf_receipt(r,st.session_state["biz"])
    st.download_button("📄 Télécharger PDF",pdf,"recu.pdf")
    if st.button("📲 Envoyer reçu WhatsApp"):
        send_whatsapp_api(clean_phone(r["Phone"]), "Merci pour votre paiement 🙏")
