import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V52 - SMART INSERTION (NO GAPS)
st.set_page_config(page_title="EMPIRE_PRO_V52", layout="wide", page_icon="⚡")

# ⚡ CSS VIBRANT (STAYING CLEAN)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .biz-banner {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        padding: 30px; border-radius: 20px; color: white !important;
        text-align: center; font-size: 40px; font-weight: 900; margin-bottom: 25px;
    }
    div[data-testid="stMetric"] { background: white !important; border-radius: 20px !important; padding: 20px !important; box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important; }
    div[data-testid="stMetricValue"] > div { color: #4f46e5 !important; font-weight: 800 !important; }
    label p { color: #1e293b !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=scope))

client = get_gspread_client()

# --- LOGIN ---
if "auth" not in st.session_state:
    st.markdown('<div class="biz-banner">🚀 ENTERPRISE LOGIN</div>', unsafe_allow_html=True)
    u_in = st.text_input("Username:")
    p_in = st.text_input("Password:", type="password")
    if st.button("Unlock"):
        m_sheet = client.open("Master_Admin").sheet1
        m_df = pd.DataFrame(m_sheet.get_all_records())
        match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
        if not match.empty:
            st.session_state.update({"auth": True, "user": u_in, "biz_name": str(match.iloc[0]['Business_Name']), "sheet_name": str(match.iloc[0]['Sheet_Name'])})
            st.rerun()
    st.stop()

# --- LOAD DATA ---
c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
df = pd.DataFrame(c_sheet_obj.get_all_records())
today = datetime.now().date()

if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = pd.to_datetime(df['Date Fin']).dt.strftime('%Y-%m-%d').fillna("N/A")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

st.markdown(f'<div class="biz-banner">⚡ {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)
t1, t2, t3, t4 = st.tabs(["📊 DASHBOARD", "👥 GESTION", "🔔 RAPPELS", "📄 REÇUS"])

with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("ALERTES", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="simple_white"), use_container_width=True)

with t2:
    with st.expander("➕ AJOUTER UN CLIENT"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom")
        n_phone = ca.text_input("WhatsApp")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Détails") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix", min_value=0)
        n_dur = cc.number_input("Mois", min_value=1, value=1)
        
        if st.button("🚀 Valider"):
            if n_nom and n_phone:
                # 💡 SMART INSERTER: Ghadi n-ziydou l-klyan dabba nichan m9add
                n_fin = today + relativedelta(months=int(n_dur))
                new_r = [n_nom, str(n_phone), "", final_s, n_prix, str(today), n_dur, str(n_fin), "Actif"]
                
                # OMEGA HACK: Blast append_row, ghadi n-zidoh f l-DataFrame o n-sauvegardo kolchi m-sttef
                df_new = pd.concat([df.drop(columns=['Days', 'Date_Display'], errors='ignore'), pd.DataFrame([dict(zip(df.columns, new_r))])], ignore_index=True)
                c_sheet_obj.clear()
                c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
                st.success("✅ Synchronisé wa7ed-te7t-wa7ed!")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Days"]
        edited = st.data_editor(df[cols], use_container_width=True, num_rows="dynamic", disabled=["Days", "Date Fin"])
        if st.button("💾 Sauvegarder Changes"):
            final_df = edited.drop(columns=['Days', 'Date_Display'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Cloud Updated!")
            st.rerun()

with t3:
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.info(f"👤 {r['Nom']} | ⏳ {r['Days']} j")
            wa = f"https://wa.me/{r['Phone']}?text=Bonjour {r['Nom']}, renouvellement {r['Service']}?"
            cr.link_button("📲 Rappeler", wa)
    else: st.success("Tout est OK.")

with t4:
    if not df.empty:
        sel = st.selectbox("Client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"*REÇU - {st.session_state['biz_name']}*\n👤 Client: {c['Nom']}\n📺 Service: {c['Service']}\n💰 Prix: {c['Prix']} DH\n⌛ Expire: {c['Date_Display']}\n*Merci !*"
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

st.sidebar.button("Log out", on_click=lambda: st.session_state.clear())
