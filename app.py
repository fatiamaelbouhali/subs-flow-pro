import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA FINAL V8 - THE UNBREAKABLE SAAS
st.set_page_config(page_title="SUBS_FLOW_PRO_PLATFORM", layout="wide", page_icon="🏦")

# --- 1. CONFIGURATION MASTER (S-SAROUT DIAL FATIMA) ---
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

client = get_gspread_client()

# --- 2. LOGIN SYSTEM SAAS ---
if "auth" not in st.session_state:
    st.title("🏦 Plateforme de Gestion Pro")
    st.subheader("Accès Partenaires")
    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
    
    if st.button("Se Connecter"):
        try:
            # Connect l l-Master Sheet sghir
            master_sheet = client.open_by_key(MASTER_ID).get_worksheet(0)
            m_data = master_sheet.get_all_records()
            
            if not m_data:
                st.error("❌ Master Sheet khawya!")
            else:
                m_df = pd.DataFrame(m_data)
                # Match user & pass
                user_row = m_df[(m_df['User'].astype(str) == str(u_in)) & (m_df['Password'].astype(str) == str(p_in))]
                
                if not user_row.empty:
                    if user_row.iloc[0]['Status'] == 'Active':
                        st.session_state["auth"] = True
                        st.session_state["user"] = u_in
                        st.session_state["sheet_id"] = user_row.iloc[0]['Sheet_ID']
                        st.rerun()
                    else:
                        st.error("🚫 Accès Suspendu.")
                else:
                    st.error("❌ Identifiants incorrects.")
        except Exception as e:
            st.error(f"❌ Error Master: {e}")
    st.stop()

# --- 3. LOAD CLIENT DATA (SI CONNECTÉ) ---
try:
    client_sheet_obj = client.open_by_key(st.session_state["sheet_id"]).get_worksheet(0)
    raw_data = client_sheet_obj.get_all_records()
    df = pd.DataFrame(raw_data)
except Exception as e:
    st.error(f"❌ Error Client Sheet: {e}")
    st.stop()

# --- DATA CLEANING (ANTI-ERROR) ---
if not df.empty:
    if 'Email' not in df.columns: df['Email'] = ""
    for col in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if col in df.columns: df[col] = df[col].astype(str).replace('nan', '')
    if 'Prix' in df.columns: df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.date

today = datetime.now().date()

# --- 4. INTERFACE UI ---
st.sidebar.title(f"👤 {st.session_state['user']}")
if st.sidebar.button("Se déconnecter"):
    del st.session_state["auth"]
    st.rerun()

t1, t2, t3 = st.tabs(["📊 DASHBOARD", "👥 CLIENTS", "🔔 ALERTES"])

# TAB 1: ANALYTICS
with t1:
    st.header("Analyse Financière")
    if not df.empty:
        c1, c2 = st.columns(2)
        c1.metric("Revenue Total", f"{df['Prix'].sum()} DH")
        c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Service', title="Revenue par Service"), use_container_width=True)
    else:
        st.info("Aucune donnée.")

# TAB 2: MANAGEMENT
with t2:
    st.header("Gestion de la Base")
    with st.expander("➕ Nouveau Client"):
        ca, cb, cc = st.columns(3)
        with ca:
            n_nom = st.text_input("Nom")
            n_phone = st.text_input("WhatsApp")
        with cb:
            n_serv = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
            n_prix = st.number_input("Prix", min_value=0)
        with cc:
            n_dur = st.number_input("Durée (Mois)", min_value=1, value=1)
        
        if st.button("🚀 Enregistrer au Cloud"):
            if n_nom and n_phone:
                n_fin = today + relativedelta(months=int(n_dur))
                new_row = [n_nom, n_phone, "", n_serv, n_prix, str(today), n_dur, str(n_fin), "Actif"]
                client_sheet_obj.append_row(new_row)
                st.success("✅ Client ajouté!")
                st.rerun()

    st.markdown("---")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder les changements"):
        client_sheet_obj.clear()
        client_sheet_obj.update([df.columns.values.tolist()] + edited.values.tolist())
        st.success("✅ Google Sheets Synced!")
        st.rerun()

# TAB 3: ALERTES
with t3:
    st.header("Rappels de Renouvellement")
    if not df.empty:
        df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 100)
        alerts = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
        if not alerts.empty:
            for _, r in alerts.iterrows():
                with st.container():
                    st.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} jours restants")
                    msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire bientôt. On renouvelle?"
                    st.link_button(f"📲 Rappeler", f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}")
                    st.markdown("---")
        else:
            st.success("Tout est à jour.")
