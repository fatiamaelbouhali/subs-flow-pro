import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# OMEGA STATUS: V22 - THE PERFECTION SaaS
st.set_page_config(page_title="SUBS_FLOW_EMPIRE_V22", layout="wide", page_icon="💎")

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

client = get_gspread_client()

# --- 1. LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.title("🛡️ SaaS Subscription Platform")
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
                    st.session_state["target_sheet"] = str(match.iloc[0]['Sheet_Name']).strip()
                    st.rerun()
                else: st.error("🚫 Accès Suspendu.")
            else: st.error("❌ Identifiants incorrects.")
        except Exception as e:
            st.error(f"❌ Error Master: {e}")
    st.stop()

# --- 2. LOAD & PROCESS DATA ---
try:
    c_sheet_obj = client.open(st.session_state["target_sheet"]).sheet1
    data_raw = c_sheet_obj.get_all_records()
    df = pd.DataFrame(data_raw)
except Exception as e:
    st.error(f"❌ Impossible d'ouvrir la base: {st.session_state['target_sheet']}")
    st.stop()

# --- HARD DATA CLEANING & AUTO-CALC ---
today = datetime.now().date()

if not df.empty:
    # Force Email if missing
    if 'Email' not in df.columns: df['Email'] = ""
    # Hard Type Casting (Ant-Error)
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Durée (Mois)'] = pd.to_numeric(df['Durée (Mois)'], errors='coerce').fillna(1)
    
    # Process Dates
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.date
    
    # 💡 AUTO-CALC: Jours Restants & Mois
    df['Jours Restants'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Mois'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.strftime('%B %Y').fillna("N/A")

# --- UI INTERFACE ---
st.sidebar.title(f"👤 {st.session_state['user']}")
if st.sidebar.button("Déconnexion"):
    del st.session_state["auth"]
    st.rerun()

t1, t2, t3 = st.tabs(["📊 DASHBOARD", "👥 GESTION CLIENTS", "🔔 ALERTES"])

with t1:
    st.header("Financial Performance")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Revenue Global", f"{df['Prix'].sum()} DH")
        c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        c3.metric("Relances (3j)", len(df[(df['Jours Restants'] <= 3) & (df['Status'] == 'Actif')]))
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Service', title="Chiffre d'affaires / Service"), use_container_width=True)

with t2:
    st.header("Gestion de la Base")
    with st.expander("➕ Ajouter un nouveau client"):
        ca, cb, cc = st.columns(3)
        with ca:
            n_nom = st.text_input("Nom Complet")
            n_phone = st.text_input("WhatsApp (ex: 2126...)")
            n_email = st.text_input("Email")
        with cb:
            s_list = ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"]
            s_choice = st.selectbox("Service", s_list)
            # 💡 LOGIC AUTRE (BACK):
            final_s = st.text_input("Préciser le service") if s_choice == "Autre" else s_choice
            n_prix = st.number_input("Prix (DH)", min_value=0, step=5)
        with cc:
            n_deb = st.date_input("Date de Début", today)
            n_dur = st.number_input("Durée (Mois)", min_value=1, value=1)
            n_stat = st.selectbox("Status", ["Actif", "Payé", "En Attente"])

        if st.button("🚀 Enregistrer au Cloud"):
            if n_nom and n_phone and final_s:
                # 💡 AUTO-CALC DATE FIN
                n_fin = n_deb + relativedelta(months=int(n_dur))
                new_r = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), n_stat]
                c_sheet_obj.append_row(new_r)
                st.success(f"✅ {n_nom} t-zad nichan f Google Sheets!")
                st.rerun()

    st.markdown("---")
    # Data Editor avec colonnes virtuelles
    if not df.empty:
        # On définit l'ordre des colonnes pour que ça soit PRO
        cols_order = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Jours Restants", "Status"]
        edited = st.data_editor(df[cols_order], use_container_width=True, num_rows="dynamic", 
                                disabled=["Jours Restants", "Date Fin"])
        
        if st.button("💾 Sauvegarder les modifications"):
            # Cleanup avant d'envoyer à Google
            final_df = edited.drop(columns=['Jours Restants', 'Mois'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.values.tolist())
            st.success("✅ Google Sheets Synchro!")
            st.rerun()

with t3:
    st.header("WhatsApp Smart Rappels")
    if not df.empty:
        alerts = df[(df['Jours Restants'] <= 3) & (df['Status'] == 'Actif')]
        if not alerts.empty:
            for _, r in alerts.iterrows():
                col1, col2 = st.columns([3, 1])
                col1.warning(f"👤 **{r['Nom']}** | ⏳ **{r['Jours Restants']} jours** (Expire le: {r['Date Fin']})")
                msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} va expirer bientôt. Voulez-vous renouveler ?"
                wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
                col2.link_button("📲 Rappeler", wa)
        else: st.success("Aucun rappel urgent.")
