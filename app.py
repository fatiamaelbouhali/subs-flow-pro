import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V10 - DIAGNOSTIC MODE
st.set_page_config(page_title="SUBS_FLOW_PRO", layout="wide")

# MASTER ID NICHAN (BLA URL)
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    # Talla3 l-email f Sidebar bach Fatima t-verify-ih
    st.sidebar.info(f"📧 Service Account Email:\n{creds_dict['client_email']}")
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

client = get_gspread_client()

# --- LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.title("🏦 Plateforme Management Pro")
    st.warning("⚠️ Ila tla3 lik Error 404 l-te7t, copy l-email li f l-yissar o zidi h f Share dial Google Sheet k Editor.")
    
    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
    
    if st.button("Se Connecter"):
        try:
            # OPEN BY KEY NICHAN
            master_sheet = client.open_by_key(MASTER_ID).get_worksheet(0)
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
            st.error(f"❌ Error Detail: {e}")
    st.stop()

# --- LOAD CLIENT DATA ---
try:
    client_sheet = client.open_by_key(st.session_state["sheet_id"]).get_worksheet(0)
    df = pd.DataFrame(client_sheet.get_all_records())
except Exception as e:
    st.error(f"❌ Error Client Sheet (Share this Sheet too!): {e}")
    st.stop()

# --- REST OF UI (DASHBOARD/CLIENTS) ---
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
    st.header("Base de Données")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder Changes"):
        client_sheet.clear()
        client_sheet.update([df.columns.values.tolist()] + edited.values.tolist())
        st.success("✅ Cloud Updated!")
