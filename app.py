import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# OMEGA STATUS: V14 - TOTAL DIAGNOSTIC & EMPIRE
st.set_page_config(page_title="SUBS_FLOW_PRO", layout="wide")

# S-SAROUT L-MOUBACHIR (ID DIAL MASTER_ADMIN)
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

client = get_gspread_client()

# --- LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.title("🏦 Plateforme Management Pro")
    
    # --- DIAGNOSTIC (HADI HIYA L-MOUHIMA) ---
    st.sidebar.subheader("🔍 Status Diagnostic")
    try:
        # Wach l-app katchouf l-fichieat?
        available_sheets = [s.title for s in client.openall()]
        st.sidebar.write("✅ Fichiers accessibles:", available_sheets)
        if "Master_Admin" not in available_sheets:
            st.sidebar.error("❌ Google Sheets: Master_Admin makhddamch m3aya. Verifier l-email dial Share!")
    except Exception as e:
        st.sidebar.error(f"❌ Error API: {e}")

    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
    
    if st.button("Se Connecter"):
        try:
            # TRY TO OPEN BY URL DIRECTLY TO BYPASS 404
            url = f"https://docs.google.com/spreadsheets/d/{MASTER_ID}/edit"
            master_sheet = client.open_by_url(url).get_worksheet(0)
            m_df = pd.DataFrame(master_sheet.get_all_records())
            
            # Match (Clean strings)
            user_match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & 
                              (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
            
            if not user_match.empty:
                if user_match.iloc[0]['Status'] == 'Active':
                    st.session_state["auth"] = True
                    st.session_state["user"] = u_in
                    st.session_state["sheet_id"] = str(user_match.iloc[0]['Sheet_ID']).strip()
                    st.rerun()
                else: st.error("🚫 Compte suspendu.")
            else: st.error("❌ Identifiants incorrects.")
        except Exception as e:
            st.error(f"❌ Erreur Fatale: {e}")
    st.stop()

# --- SI CONNECTÉ : DASHBOARD ---
try:
    c_url = f"https://docs.google.com/spreadsheets/d/{st.session_state['sheet_id']}/edit"
    client_sheet = client.open_by_url(c_url).get_worksheet(0)
    df = pd.DataFrame(client_sheet.get_all_records())
except Exception as e:
    st.error(f"❌ Impossible d'ouvrir votre base de données: {e}")
    st.stop()

st.sidebar.success(f"Connecté: {st.session_state['user']}")
if st.sidebar.button("Déconnexion"):
    del st.session_state["auth"]
    st.rerun()

t1, t2 = st.tabs(["📊 DASHBOARD", "👥 CLIENTS"])
with t1:
    if not df.empty:
        df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
        st.metric("Total Revenue", f"{df['Prix'].sum()} DH")
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Service'), use_container_width=True)

with t2:
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder"):
        client_sheet.clear()
        client_sheet.update([df.columns.values.tolist()] + edited.values.tolist())
        st.success("Synced!")
