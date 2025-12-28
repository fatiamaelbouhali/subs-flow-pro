import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V7 - THE FINAL BOSS
st.set_page_config(page_title="SUBS_FLOW_PRO_SaaS", layout="wide")

# --- 1. CONFIGURATION DES ACCÈS ---
# Master ID dial MASTER_ADMIN dial Fatima nichan
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

# Fonction bach n-connectiw m3a Google
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
    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
    
    if st.button("Se Connecter"):
        try:
            # Open Master Sheet
            master_sheet = client.open_by_key(MASTER_ID).sheet1
            m_df = pd.DataFrame(master_sheet.get_all_records())
            
            user_row = m_df[(m_df['User'] == u_in) & (m_df['Password'] == str(p_in))]
            
            if not user_row.empty:
                if user_row.iloc[0]['Status'] == 'Active':
                    st.session_state["auth"] = True
                    st.session_state["user"] = u_in
                    st.session_state["sheet_id"] = user_row.iloc[0]['Sheet_ID']
                    st.rerun()
                else:
                    st.error("🚫 Compte suspendu.")
            else:
                st.error("❌ Identifiants incorrects.")
        except Exception as e:
            st.error(f"❌ Error Master: {e}")
    st.stop()

# --- 3. LOAD DATA CLIENT ---
try:
    client_sheet_obj = client.open_by_key(st.session_state["sheet_id"]).sheet1
    df = pd.DataFrame(client_sheet_obj.get_all_records())
except Exception as e:
    st.error(f"❌ Error Client Sheet: {e}")
    st.stop()

# --- DATA CLEANING ---
if not df.empty:
    for col in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if col in df.columns: df[col] = df[col].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
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
    st.header("Financial Overview")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Revenue", f"{df['Prix'].sum()} DH")
        c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Service', title="Revenue/Service"), use_container_width=True)

with t2:
    st.header("Gestion de la Base de Données")
    # Formulaire d'ajout
    with st.expander("➕ Nouveau Client"):
        c_a, c_b = st.columns(2)
        with c_a:
            n_nom = st.text_input("Nom")
            n_phone = st.text_input("WhatsApp")
        with c_b:
            n_serv = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "IPTV", "Disney+", "Autre"])
            n_prix = st.number_input("Prix", min_value=0)
        
        if st.button("🚀 Enregistrer"):
            if n_nom and n_phone:
                n_fin = today + relativedelta(months=1)
                new_row = [n_nom, n_phone, "", n_serv, n_prix, str(today), 1, str(n_fin), "Actif"]
                client_sheet_obj.append_row(new_row)
                st.success("Client ajouté!")
                st.rerun()

    st.markdown("---")
    # Editor
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder les modifications"):
        client_sheet_obj.clear()
        client_sheet_obj.update([df.columns.values.tolist()] + edited.values.tolist())
        st.success("Synced!")
        st.rerun()

with t3:
    st.header("Rappels WhatsApp")
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 100)
    alerts = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not alerts.empty:
        for _, r in alerts.iterrows():
            st.warning(f"👤 {r['Nom']} | 📺 {r['Service']} | ⏳ {r['Days']} jours")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire bientôt."
            st.link_button(f"📲 Rappeler {r['Nom']}", f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}")
