import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V9 - THE UNSTOPPABLE SaaS
st.set_page_config(page_title="SUBS_FLOW_PRO_SaaS", layout="wide", page_icon="🏦")

# MASTER URL (L-Link l-kamel bach Google mat-t-lefch)
MASTER_URL = "https://docs.google.com/spreadsheets/d/1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE/edit"

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
            # 💡 TEST CONNECTION MASTER
            master_sheet = client.open_by_url(MASTER_URL).get_worksheet(0)
            m_df = pd.DataFrame(master_sheet.get_all_records())
            
            # Match user & password
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
        except gspread.exceptions.SpreadsheetNotFound:
            st.error("❌ Google goul lik: Had l-Master Sheet mal9itouch. Share l-email d'abord!")
        except Exception as e:
            st.error(f"❌ Error Diagnostic: {e}")
    st.stop()

# --- LOAD CLIENT DATA ---
try:
    c_url = f"https://docs.google.com/spreadsheets/d/{st.session_state['sheet_id']}/edit"
    client_sheet = client.open_by_url(c_url).get_worksheet(0)
    df = pd.DataFrame(client_sheet.get_all_records())
except Exception as e:
    st.error(f"❌ Error Client Sheet (Check ID or Share): {e}")
    st.stop()

# --- DATA CLEANING ---
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    if 'Prix' in df.columns: df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    today = datetime.now().date()
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 100)

# --- UI TABS ---
st.sidebar.title(f"👤 {st.session_state['user']}")
if st.sidebar.button("Déconnexion"):
    del st.session_state["auth"]
    st.rerun()

t1, t2, t3 = st.tabs(["📊 DASHBOARD", "👥 CLIENTS", "🔔 ALERTES"])

with t1:
    st.header("Analyse Business")
    if not df.empty:
        col1, col2 = st.columns(2)
        col1.metric("Total DH", f"{df['Prix'].sum()} DH")
        col2.metric("Actifs", len(df[df['Status'] == 'Actif']))
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Service'), use_container_width=True)

with t2:
    st.header("Gestion Clients")
    with st.expander("➕ Nouveau Client"):
        c_a, c_b = st.columns(2)
        n_nom = c_a.text_input("Nom")
        n_phone = c_a.text_input("Phone")
        n_serv = c_b.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "IPTV", "Disney+", "Autre"])
        n_prix = c_b.number_input("Prix", min_value=0)
        if st.button("🚀 Ajouter au Google Sheet"):
            n_fin = datetime.now().date() + relativedelta(months=1)
            new_r = [n_nom, n_phone, "", n_serv, n_prix, str(datetime.now().date()), 1, str(n_fin), "Actif"]
            client_sheet.append_row(new_r)
            st.success("✅ Synced!")
            st.rerun()

    st.markdown("---")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder Changes"):
        client_sheet.clear()
        client_sheet.update([df.columns.values.tolist()] + edited.values.tolist())
        st.success("✅ Cloud Updated!")
        st.rerun()

with t3:
    st.header("Alertes WhatsApp")
    if not df.empty:
        alerts = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
        for _, r in alerts.iterrows():
            st.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} j")
            wa = f"https://wa.me/{r['Phone']}?text=Bonjour {r['Nom']}, renouvellement {r['Service']}?"
            st.link_button(f"📲 Rappeler {r['Nom']}", wa)
