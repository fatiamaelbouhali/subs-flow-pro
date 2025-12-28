import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V18 - THE FINAL BOSS OF PERMISSIONS
st.set_page_config(page_title="SUBS_FLOW_PRO_EMPIRE", layout="wide")

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

client = get_gspread_client()

# --- LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.title("🏦 Plateforme Management Pro")
    
    # DIAGNOSTIC SIDEBAR
    with st.sidebar:
        st.subheader("🕵️ Diagnostic OMEGA")
        try:
            files = [s.title for s in client.openall()]
            st.write("Fichiers accessibles:", files)
            if len(files) < 2:
                st.error("⚠️ Khass t-zidi l-email f Share dial Database_Subs !")
        except: st.error("API Error")

    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
    
    if st.button("Se Connecter"):
        try:
            m_sheet = client.open("Master_Admin").sheet1
            m_df = pd.DataFrame(m_sheet.get_all_records())
            match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & 
                         (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
            
            if not match.empty:
                if match.iloc[0]['Status'] == 'Active':
                    st.session_state["auth"] = True
                    st.session_state["user"] = u_in
                    st.session_state["sheet_id"] = str(match.iloc[0]['Sheet_ID']).strip()
                    st.rerun()
                else: st.error("🚫 Accès Suspendu.")
            else: st.error("❌ Identifiants incorrects.")
        except Exception as e:
            st.error(f"❌ Error Master: {e}")
    st.stop()

# --- LOAD DATA ---
try:
    c_sheet = client.open_by_key(st.session_state["sheet_id"]).sheet1
    df = pd.DataFrame(c_sheet.get_all_records())
except Exception as e:
    st.error(f"❌ Impossible d'ouvrir la base de données. ID: {st.session_state['sheet_id']}")
    st.info(f"💡 Diri Share m3a dak l-email f s-Sheet dialek!")
    if st.button("Déconnexion"):
        del st.session_state["auth"]
        st.rerun()
    st.stop()

# --- INTERFACE ---
today = datetime.now().date()
st.sidebar.success(f"Connecté: {st.session_state['user']}")
if st.sidebar.button("Déconnexion"):
    del st.session_state["auth"]
    st.rerun()

t1, t2 = st.tabs(["📊 DASHBOARD", "👥 CLIENTS"])
with t1:
    if not df.empty:
        df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
        st.metric("Revenue Total", f"{df['Prix'].sum()} DH")
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Service'), use_container_width=True)

with t2:
    st.header("Gestion Clients")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder modifications"):
        c_sheet.clear()
        c_sheet.update([df.columns.values.tolist()] + edited.values.tolist())
        st.success("✅ Database Updated!")
        st.rerun()
