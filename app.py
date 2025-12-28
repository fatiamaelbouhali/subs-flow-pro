import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V11 - THE FINAL DESTRUCTION OF ERROR 404
st.set_page_config(page_title="SUBS_FLOW_PRO_MASTER", layout="wide", page_icon="🏦")

# MASTER LINK NICHAN (BLA ID SGHIR BACH MAT-T-LEFCH)
MASTER_URL = "https://docs.google.com/spreadsheets/d/1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE/edit?usp=sharing"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    st.sidebar.info(f"📧 Share this Email:\n{creds_dict['client_email']}")
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
            # FORCE OPEN BY URL NICHAN
            master_sheet = client.open_by_url(MASTER_URL).get_worksheet(0)
            m_df = pd.DataFrame(master_sheet.get_all_records())
            
            user_match = m_df[(m_df['User'].astype(str) == str(u_in)) & (m_df['Password'].astype(str) == str(p_in))]
            
            if not user_match.empty:
                if user_match.iloc[0]['Status'] == 'Active':
                    st.session_state["auth"] = True
                    st.session_state["user"] = u_in
                    st.session_state["sheet_id"] = user_match.iloc[0]['Sheet_ID']
                    st.rerun()
                else:
                    st.error("🚫 Compte suspendu.")
            else:
                st.error("❌ Identifiants incorrects.")
        except Exception as e:
            st.error(f"❌ Diagnostic: Had l-link fih mochkil d l-access ou mal9itouch. Share l-email d'abord!")
            st.code(f"Technical Error: {e}")
    st.stop()

# --- LOAD CLIENT DATA ---
try:
    c_url = f"https://docs.google.com/spreadsheets/d/{st.session_state['sheet_id']}/edit"
    client_sheet = client.open_by_url(c_url).get_worksheet(0)
    df = pd.DataFrame(client_sheet.get_all_records())
except Exception as e:
    st.error(f"❌ Error Client Sheet (Check ID or Share): {e}")
    st.stop()

# --- UI INTERFACE ---
st.sidebar.title(f"👤 {st.session_state['user']}")
if st.sidebar.button("Déconnexion"):
    del st.session_state["auth"]
    st.rerun()

t1, t2, t3 = st.tabs(["📊 DASHBOARD", "👥 CLIENTS", "🔔 ALERTES"])

with t1:
    st.header("Analyse Financière")
    if not df.empty:
        df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
        st.metric("Revenue Total", f"{df['Prix'].sum()} DH")
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Service'), use_container_width=True)

with t2:
    st.header("Gestion Clients")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder Changes"):
        client_sheet.clear()
        client_sheet.update([df.columns.values.tolist()] + edited.values.tolist())
        st.success("✅ Cloud Updated!")
