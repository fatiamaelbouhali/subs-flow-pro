import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V17 - TOTAL CLARITY
st.set_page_config(page_title="SUBS_FLOW_PRO_MASTER", layout="wide")

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

client = get_gspread_client()

# --- LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.title("🏦 SaaS Empire Login")
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

# --- LOAD DATA (THE CRITICAL PART) ---
try:
    # 💡 SCAN FILES: Bach Fatima t-chouf chnou katchouf l-app
    available_files = [s.title for s in client.openall()]
    if "Database_Subs" not in available_files:
        st.sidebar.error("🚨 Database_Subs n'est pas partagée !")
        st.sidebar.info(f"Ajoute cet email dans Share de Database_Subs:\n{st.secrets['connections']['gsheets']['client_email']}")
    
    c_sheet = client.open_by_key(st.session_state["sheet_id"]).sheet1
    df = pd.DataFrame(c_sheet.get_all_records())
except Exception as e:
    st.error(f"❌ Impossible d'ouvrir la base de données client.")
    st.code(f"Error detail: {e}")
    st.stop()

# --- REST OF UI ---
today = datetime.now().date()
st.sidebar.success(f"User: {st.session_state['user']}")
if st.sidebar.button("Déconnexion"):
    del st.session_state["auth"]
    st.rerun()

t1, t2, t3 = st.tabs(["📊 DASHBOARD", "👥 CLIENTS", "🔔 ALERTES"])

with t1:
    if not df.empty:
        df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
        st.metric("Revenue Global", f"{df['Prix'].sum()} DH")
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Service'), use_container_width=True)

with t2:
    st.header("Gestion Clients")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder Changes"):
        c_sheet.clear()
        c_sheet.update([df.columns.values.tolist()] + edited.values.tolist())
        st.success("✅ Database Updated!")
        st.rerun()

with t3:
    st.header("WhatsApp Alertes")
    if not df.empty:
        df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
        df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 100)
        alerts = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
        for _, r in alerts.iterrows():
            st.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} j")
            wa = f"https://wa.me/{r['Phone']}?text=Bonjour {r['Nom']}, renouvellement {r['Service']}?"
            st.link_button(f"📲 Rappeler", wa)
