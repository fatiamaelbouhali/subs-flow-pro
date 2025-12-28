import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V7 - THE FINAL BOSS
st.set_page_config(page_title="SUBS_FLOW_PRO_SaaS", layout="wide", page_icon="🏦")

# --- 1. CONFIGURATION MASTER ---
# ID dial MASTER_ADMIN dial Fatima nichan
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    # Jbed s-sarout mn Secrets
    creds_dict = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

client = get_gspread_client()

# --- 2. LOGIN SYSTEM SAAS ---
if "auth" not in st.session_state:
    st.title("🏦 Plateforme Multi-Tenant Pro")
    st.subheader("Accès Partenaires")
    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
    
    if st.button("Se Connecter"):
        try:
            # OPEN BY URL BACH N-HNAW MN 404 nichan
            master_url = f"https://docs.google.com/spreadsheets/d/{MASTER_ID}/edit"
            master_sheet = client.open_by_url(master_url).sheet1
            m_data = master_sheet.get_all_records()
            
            if not m_data:
                st.error("❌ Master Sheet khawya!")
                st.stop()
                
            m_df = pd.DataFrame(m_data)
            # Match user & pass
            user_row = m_df[(m_df['User'] == u_in) & (m_df['Password'].astype(str) == str(p_in))]
            
            if not user_row.empty:
                if user_row.iloc[0]['Status'] == 'Active':
                    st.session_state["auth"] = True
                    st.session_state["user"] = u_in
                    st.session_state["sheet_id"] = user_row.iloc[0]['Sheet_ID']
                    st.rerun()
                else:
                    st.error("🚫 Compte suspendu. Contactez Master Fatima.")
            else:
                st.error("❌ Identifiants incorrects.")
        except Exception as e:
            st.error(f"❌ Error Master Connection: {e}")
    st.stop()

# --- 3. LOAD DATA CLIENT ---
try:
    client_url = f"https://docs.google.com/spreadsheets/d/{st.session_state['sheet_id']}/edit"
    client_sheet_obj = client.open_by_url(client_url).sheet1
    data_raw = client_sheet_obj.get_all_records()
    df = pd.DataFrame(data_raw)
except Exception as e:
    st.error(f"❌ Error Client Sheet: {e}")
    st.stop()

# --- DATA CLEANING ---
if not df.empty:
    # Patch Email
    if 'Email' not in df.columns: df['Email'] = ""
    # Force Strings for Editor
    for col in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if col in df.columns: df[col] = df[col].astype(str).replace('nan', '')
    # Force Numbers
    if 'Prix' in df.columns: df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    # Force Dates
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.date

today = datetime.now().date()

# --- 4. UI INTERFACE ---
st.sidebar.title(f"👤 {st.session_state['user']}")
if st.sidebar.button("Se déconnecter"):
    del st.session_state["auth"]
    st.rerun()

t1, t2, t3 = st.tabs(["📊 DASHBOARD", "👥 CLIENTS", "🔔 ALERTES"])

with t1:
    st.header("Financial Analytics")
    if not df.empty:
        c1, c2 = st.columns(2)
        c1.metric("Total Revenue", f"{df['Prix'].sum()} DH")
        c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Service', title="Revenue per Service"), use_container_width=True)

with t2:
    st.header("Base de Données Clients")
    with st.expander("➕ Ajouter un nouveau client"):
        c_a, c_b = st.columns(2)
        with c_a:
            n_nom = st.text_input("Nom")
            n_phone = st.text_input("WhatsApp")
        with c_b:
            n_serv = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "IPTV", "Disney+", "Autre"])
            n_prix = st.number_input("Prix", min_value=0)
        
        if st.button("🚀 Enregistrer au Cloud"):
            if n_nom and n_phone:
                n_fin = today + relativedelta(months=1)
                # Formatter l-row dial Google Sheet nichan
                new_row = [n_nom, n_phone, "", n_serv, n_prix, str(today), 1, str(n_fin), "Actif"]
                client_sheet_obj.append_row(new_row)
                st.success("✅ Client ajouté dans Google Sheets!")
                st.rerun()

    st.markdown("---")
    # Data Editor Pro
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder les modifications"):
        client_sheet_obj.clear()
        # On remet les headers et les données modifiées
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
                with st.container():
                    st.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} jours")
                    msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} arrive à sa fin. On renouvelle?"
                    st.link_button(f"📲 Rappeler via WhatsApp", f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}")
                    st.markdown("---")
        else:
            st.success("Tout est à jour.")
