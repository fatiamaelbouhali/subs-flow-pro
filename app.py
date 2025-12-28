import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# OMEGA STATUS: V12 SUPREME - THE END OF ERRORS
st.set_page_config(page_title="SUBS_FLOW_EMPIRE", layout="wide", page_icon="👑")

# LINKS NICHAN (S-SATA L-9ATTALA)
MASTER_URL = "https://docs.google.com/spreadsheets/d/1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE/edit"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
        st.error("❌ Secrets machi m9addin f Streamlit! Ziri m3aya f Settings.")
        st.stop()
    creds_dict = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

client = get_gspread_client()

# --- LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.title("🏦 SaaS Empire Management")
    st.info(f"📧 Share Google Sheets with: {st.secrets['connections']['gsheets']['client_email']}")
    
    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
    
    if st.button("Se Connecter & Dominer"):
        try:
            # 💡 OPEN MASTER SHEET NICHAN
            master_sheet = client.open_by_url(MASTER_URL).sheet1
            m_df = pd.DataFrame(master_sheet.get_all_records())
            
            # Clean spaces o match
            user_match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & 
                              (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
            
            if not user_match.empty:
                if user_match.iloc[0]['Status'] == 'Active':
                    st.session_state["auth"] = True
                    st.session_state["user"] = u_in
                    st.session_state["sheet_id"] = str(user_match.iloc[0]['Sheet_ID']).strip()
                    st.rerun()
                else:
                    st.error("🚫 Compte suspendu. Khlless s-chhar a ba!")
            else:
                st.error("❌ Identifiants incorrects.")
        except Exception as e:
            st.error(f"❌ Error Detail: {e}")
    st.stop()

# --- LOAD CLIENT DATA ---
try:
    # Build Client URL from ID in Master Sheet
    client_url = f"https://docs.google.com/spreadsheets/d/{st.session_state['sheet_id']}/edit"
    client_sheet_obj = client.open_by_url(client_url).sheet1
    df = pd.DataFrame(client_sheet_obj.get_all_records())
except Exception as e:
    st.error(f"❌ Error Database: Ma-9dertch n-dkhol l s-Sheet ID: {st.session_state['sheet_id']}")
    st.code(f"Technical Reason: {e}")
    if st.button("Déconnexion"):
        del st.session_state["auth"]
        st.rerun()
    st.stop()

# --- DATA CLEANING ---
if not df.empty:
    if 'Email' not in df.columns: df['Email'] = ""
    for col in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if col in df.columns: df[col] = df[col].astype(str).replace('nan', '')
    if 'Prix' in df.columns: df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date

today = datetime.now().date()

# --- UI TABS ---
st.sidebar.success(f"Connected: {st.session_state['user']}")
if st.sidebar.button("Déconnexion"):
    del st.session_state["auth"]
    st.rerun()

t1, t2, t3 = st.tabs(["📊 DASHBOARD", "👥 CLIENTS", "🔔 RAPPELS"])

with t1:
    st.header("Business Analytics")
    if not df.empty:
        c1, c2 = st.columns(2)
        c1.metric("Revenue Total", f"{df['Prix'].sum()} DH")
        c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Service', title="Revenue per Service"), use_container_width=True)

with t2:
    st.header("Gestion de la Base")
    with st.expander("➕ Nouveau Client"):
        ca, cb = st.columns(2)
        n_nom = ca.text_input("Nom")
        n_phone = ca.text_input("Phone")
        n_serv = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "IPTV", "Disney+", "Autre"])
        n_prix = cb.number_input("Prix", min_value=0)
        if st.button("🚀 Ajouter au Cloud"):
            n_fin = today + relativedelta(months=1)
            new_r = [n_nom, n_phone, "", n_serv, n_prix, str(today), 1, str(n_fin), "Actif"]
            client_sheet_obj.append_row(new_r)
            st.success("✅ Nadi!")
            st.rerun()

    st.markdown("---")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder Changes"):
        client_sheet_obj.clear()
        client_sheet_obj.update([df.columns.values.tolist()] + edited.values.tolist())
        st.success("✅ Synchro Nadiya!")
        st.rerun()

with t3:
    st.header("Rappels WhatsApp")
    if not df.empty:
        df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 100)
        alerts = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
        if not alerts.empty:
            for _, r in alerts.iterrows():
                st.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} j")
                wa = f"https://wa.me/{r['Phone']}?text=Bonjour {r['Nom']}, renouvellement {r['Service']}?"
                st.link_button(f"📲 Rappeler", wa)
