import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V16 - THE UNBREAKABLE EMPIRE
st.set_page_config(page_title="SUBS_FLOW_EMPIRE", layout="wide")

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

client = get_gspread_client()

# --- LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.title("🏦 Plateforme Management Pro")
    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
    
    if st.button("Se Connecter"):
        try:
            # OPEN MASTER BY NAME (V15 FIX)
            m_sheet = client.open("Master_Admin").sheet1
            m_df = pd.DataFrame(m_sheet.get_all_records())
            
            # Match (Force string & Strip spaces)
            match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & 
                         (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
            
            if not match.empty:
                if match.iloc[0]['Status'] == 'Active':
                    st.session_state["auth"] = True
                    st.session_state["user"] = u_in
                    # 💡 FIX: Strip ID for safety
                    st.session_state["sheet_id"] = str(match.iloc[0]['Sheet_ID']).strip()
                    st.rerun()
                else: st.error("🚫 Accès Suspendu.")
            else: st.error("❌ Identifiants incorrects.")
        except Exception as e:
            st.error(f"❌ Erreur Master: {e}")
    st.stop()

# --- LOAD CLIENT DATA (FIXED TO OPEN BY KEY) ---
try:
    # 💡 OMEGA FIX: Open by Key Directly (Bypasses 404 URL errors)
    client_sheet_obj = client.open_by_key(st.session_state["sheet_id"]).sheet1
    df = pd.DataFrame(client_sheet_obj.get_all_records())
except Exception as e:
    st.error(f"❌ Error Data: Ma-9dertch n-7el s-Sheet dialek.")
    st.info(f"💡 Check f MASTER_ADMIN wach had l-ID s7i7: {st.session_state['sheet_id']}")
    if st.button("Déconnexion"):
        del st.session_state["auth"]
        st.rerun()
    st.stop()

# --- REST OF UI (PERFECTION) ---
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    if 'Prix' in df.columns: df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date

today = datetime.now().date()
st.sidebar.success(f"Connecté: {st.session_state['user']}")
if st.sidebar.button("Déconnexion"):
    del st.session_state["auth"]
    st.rerun()

t1, t2, t3 = st.tabs(["📊 DASHBOARD", "👥 CLIENTS", "🔔 ALERTES"])

with t1:
    st.header("Financial Overview")
    if not df.empty:
        c1, c2 = st.columns(2)
        c1.metric("Revenue Total", f"{df['Prix'].sum()} DH")
        c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Service'), use_container_width=True)

with t2:
    st.header("Base de Données")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder"):
        client_sheet_obj.clear()
        client_sheet_obj.update([df.columns.values.tolist()] + edited.values.tolist())
        st.success("✅ Synchro Nadiya!")
        st.rerun()

with t3:
    st.header("Rappels WhatsApp")
    if not df.empty:
        df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 100)
        alerts = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
        for _, r in alerts.iterrows():
            st.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} j")
            wa = f"https://wa.me/{r['Phone']}?text=Bonjour {r['Nom']}, renouvellement {r['Service']}?"
            st.link_button(f"📲 Rappeler", wa)
