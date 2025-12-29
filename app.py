import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V48 - ULTIMATE SaaS (ALL FIXED)
st.set_page_config(page_title="EMPIRE_V48", layout="wide", page_icon="🏦")

# ⚡ CSS LUXURY & VISIBILITY
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14 !important; }
    div[data-testid="stMetric"] {
        background: #161b22;
        border: 2px solid #00d2ff;
        border-radius: 15px;
        padding: 15px;
    }
    div[data-testid="stMetricValue"] > div { color: #00ff9d !important; font-weight: 900 !important; }
    label, p, span, h1, h2, h3 { color: #FFFFFF !important; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; font-size: 18px; }
    .boss-banner {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        padding: 20px; border-radius: 12px; color: white !important;
        text-align: center; font-size: 40px; font-weight: 900;
        margin-bottom: 25px; border: 2px solid #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=scope))

client = get_gspread_client()

# --- 1. LOGIN ---
if "auth" not in st.session_state:
    st.markdown('<div class="boss-banner">🏦 SaaS Management System</div>', unsafe_allow_html=True)
    u_in = st.text_input("Username:")
    p_in = st.text_input("Password:", type="password")
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
                    st.session_state["biz_name"] = str(match.iloc[0]['Business_Name']).strip()
                    st.session_state["sheet_name"] = str(match.iloc[0]['Sheet_Name']).strip()
                    st.rerun()
            else: st.error("❌ Identifiants Incorrects.")
        except Exception as e: st.error(f"Error: {e}")
    st.stop()

# --- 2. LOAD DATA ---
try:
    c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
    data_raw = c_sheet_obj.get_all_records()
    df = pd.DataFrame(data_raw)
except:
    st.error("Base introuvable.")
    st.stop()

today = datetime.now().date()

# --- 3. DATA CLEANING & LOGIC ---
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.date
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = pd.to_datetime(df['Date Fin']).dt.strftime('%Y-%m-%d').fillna("N/A")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 4. INTERFACE ---
st.markdown(f'<div class="boss-banner">🚀 {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 DASHBOARD", "👥 GESTION", "🔔 RAPPELS PRO", "📄 REÇUS"])

# TAB 1: ANALYTICS
with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("RAPPELS URGENTS", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
        
        st.markdown("### 📋 Résumé Business par Service")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'Chiffre d\'Affaires (DH)']
        st.dataframe(summary, use_container_width=True)
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="plotly_dark"), use_container_width=True)

# TAB 2: GESTION (RESTORED FIELDS)
with t2:
    with st.expander("➕ AJOUTER UN NOUVEAU CLIENT"):
        ca, cb, cc = st.columns(3)
        with ca:
            n_nom = st.text_input("Nom Complet Client")
            n_phone = st.text_input("WhatsApp (ex: 212...)")
            n_email = st.text_input("Email")
        with cb:
            s_list = ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"]
            s_choice = st.selectbox("Service", s_list)
            # 💡 RESTORED: Autre logic
            final_s = st.text_input("Préciser le service") if s_choice == "Autre" else s_choice
            n_prix = st.number_input("Prix (DH)", min_value=0)
        with cc:
            n_deb = st.date_input("Date de Début", today) # 💡 RESTORED
            n_dur = st.number_input("Durée (Mois)", min_value=1, value=1)
        
        if st.button("🚀 Enregistrer au Cloud"):
            if n_nom and n_phone:
                n_fin = n_deb + relativedelta(months=int(n_dur))
                new_row = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"]
                c_sheet_obj.append_row(new_row)
                st.success("✅ Synchro réussie!")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        # Ordre des colonnes
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Days"]
        edited = st.data_editor(df[cols], use_container_width=True, num_rows="dynamic", disabled=["Days", "Date Fin"])
        if st.button("💾 Sauvegarder les modifications"):
            final_df = edited.drop(columns=['Days'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Cloud Updated!")
            st.rerun()

# TAB 3: RAPPELS PRO (CLEAN LOGIC)
with t3:
    st.subheader("🔔 Centre de Relance Professionnel")
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    
    if not urgent.empty:
        st.info(f"🚀 **Action Immédiate :** {len(urgent)} relances à effectuer.")
        
        # 💡 NEW SEMI-BULK MODE (Boutons individuels mais rapides)
        for _, r in urgent.iterrows():
            with st.container():
                c_l, c_r = st.columns([3, 1])
                icon = "🔴" if r['Days'] <= 0 else "🟠"
                c_l.warning(f"{icon} **{r['Nom']}** | {r['Service']} | **{r['Days']} jours restants**")
                
                # Message Pro
                msg = (f"⚠️ *RAPPEL D'EXPIRATION - {st.session_state['biz_name']}*\n"
                       f"━━━━━━━━━━━━━━━━━━\n"
                       f"Bonjour *{r['Nom']}*,\n\n"
                       f"Votre abonnement *{r['Service']}* arrive à échéance le *{r['Date_Display']}*.\n\n"
                       f"👉 Pour éviter toute coupure, merci de renouveler.\n"
                       f"━━━━━━━━━━━━━━━━━━\n"
                       f"🤝 *Merci !*")
                
                wa_url = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
                c_r.link_button("📲 Envoyer", wa_url)
                st.markdown("---")
    else: st.success("Empire is safe. No alerts.")

# TAB 4: REÇUS
with t4:
    if not df.empty:
        sel = st.selectbox("Client pour Reçu:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = (f"✅ *REÇU DE PAIEMENT - {st.session_state['biz_name']}*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👤 Client: *{c['Nom']}*\n"
                f"📺 Service: *{c['Service']}*\n"
                f"💰 Prix: *{c['Prix']} DH*\n"
                f"⌛ Expiration: *{c['Date_Display']}*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🤝 *Merci !*")
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

st.sidebar.button("Déconnexion", on_click=lambda: st.session_state.clear())
