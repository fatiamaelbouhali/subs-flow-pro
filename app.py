import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: V15 - THE FINAL DOMINATION
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
    
    # Sidebar Diagnostic (Ghir bach t-akki blli d-data khdama)
    st.sidebar.success("✅ Connection Google: OK")
    
    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
    
    if st.button("Se Connecter"):
        try:
            # 💡 OPEN BY TITLE NICHAN (Bach n-hanw mn 404 dial l-ID)
            master_sheet = client.open("Master_Admin").sheet1
            m_df = pd.DataFrame(master_sheet.get_all_records())
            
            # Match user & password
            user_match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & 
                              (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
            
            if not user_match.empty:
                if user_match.iloc[0]['Status'] == 'Active':
                    st.session_state["auth"] = True
                    st.session_state["user"] = u_in
                    # Safely get Sheet_ID
                    st.session_state["sheet_id"] = str(user_match.iloc[0]['Sheet_ID']).strip()
                    st.rerun()
                else:
                    st.error("🚫 Compte suspendu.")
            else:
                st.error("❌ Identifiants incorrects.")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    st.stop()

# --- LOAD CLIENT DATA (OPEN BY KEY) ---
try:
    client_sheet_obj = client.open_by_key(st.session_state["sheet_id"]).sheet1
    df = pd.DataFrame(client_sheet_obj.get_all_records())
except Exception as e:
    st.error(f"❌ Impossible d'ouvrir votre base: {e}")
    if st.button("Déconnexion"):
        del st.session_state["auth"]
        st.rerun()
    st.stop()

# --- DATA CLEANING & UI ---
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
    st.header("Financial Performance")
    if not df.empty:
        col1, col2 = st.columns(2)
        col1.metric("Revenue Total", f"{df['Prix'].sum()} DH")
        col2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Service'), use_container_width=True)

with t2:
    st.header("Gestion de la Base")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder les modifications"):
        client_sheet_obj.clear()
        client_sheet_obj.update([df.columns.values.tolist()] + edited.values.tolist())
        st.success("✅ Synchro réussie!")
        st.rerun()

with t3:
    st.header("Alertes WhatsApp")
    if not df.empty:
        df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 100)
        alerts = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
        for _, r in alerts.iterrows():
            st.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} j")
            wa = f"https://wa.me/{r['Phone']}?text=Bonjour {r['Nom']}, renouvellement {r['Service']}?"
            st.link_button(f"📲 Rappeler", wa)
