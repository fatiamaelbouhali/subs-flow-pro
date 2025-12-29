import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V44 - SUPREME BOT (ALL FEATURES RESTORED)
st.set_page_config(page_title="EMPIRE_V44_ULTIMATE", layout="wide", page_icon="🤖")

# ⚡ THE FINAL CSS FIX (NO VISIBILITY ISSUES)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14 !important; }
    h1, h2, h3, h4, h5, h6, p, span, label, div, .stMarkdown { color: #FFFFFF !important; }
    
    /* Metrics Box Luxury */
    div[data-testid="stMetric"] {
        background: #161b22 !important;
        border: 2px solid #00d2ff !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
    div[data-testid="stMetricValue"] > div { color: #00ff9d !important; font-size: 38px !important; font-weight: 900 !important; }
    div[data-testid="stMetricLabel"] p { color: #ffffff !important; font-size: 16px !important; font-weight: 800 !important; text-transform: uppercase; }

    /* Tabs Bold */
    .stTabs [data-baseweb="tab"] { background-color: #161b22; color: #FFFFFF; font-weight: bold; border-radius: 5px; margin: 5px; }
    .stTabs [aria-selected="true"] { background-color: #00d2ff !important; color: #000000 !important; }

    /* Banner Pro */
    .biz-banner {
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        padding: 25px; border-radius: 12px; color: #FFFFFF !important;
        text-align: center; font-size: 42px; font-weight: 900;
        margin-bottom: 25px; border: 2px solid #ffffff;
        box-shadow: 0 4px 20px rgba(0,210,255,0.4);
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
    st.markdown('<div class="biz-banner">🏦 SaaS Empire Portal</div>', unsafe_allow_html=True)
    u_in = st.text_input("Business Username:")
    p_in = st.text_input("Access Password:", type="password")
    if st.button("Unlock Management"):
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
                else: st.error("🚫 Bloqué.")
            else: st.error("❌ Identifiants Incorrects.")
        except Exception as e: st.error(f"Error: {e}")
    st.stop()

# --- 2. LOAD DATA ---
try:
    c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
    df = pd.DataFrame(c_sheet_obj.get_all_records())
except:
    st.error("Base introuvable.")
    st.stop()

today = datetime.now().date()
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.date
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = pd.to_datetime(df['Date Fin']).dt.strftime('%Y-%m-%d').fillna("N/A")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 3. UI INTERFACE ---
st.markdown(f'<div class="biz-banner">🚀 {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 DASHBOARD", "👥 GESTION", "🤖 AUTO-RAPPELS", "📄 REÇUS"])

# TAB 1: ANALYTICS (RESTORED SUMMARY)
with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("ALERTES", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))

        st.markdown("---")
        g1, g2 = st.columns([2, 1])
        with g1:
            st.plotly_chart(px.bar(df.groupby('Service')['Prix'].sum().reset_index(), x='Service', y='Prix', title="Revenue per Service", template="plotly_dark"), use_container_width=True)
        with g2:
            st.plotly_chart(px.pie(df, names='Status', title="Stats Distribution", hole=0.5, template="plotly_dark"), use_container_width=True)

        st.markdown("### 📋 Résumé Business par Service")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Total Clients', 'Chiffre d\'Affaires (DH)']
        st.table(summary)

# TAB 2: GESTION (RESTORED DATE DEBUT)
with t2:
    with st.expander("➕ AJOUTER UN CLIENT"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom Complet")
        n_phone = ca.text_input("WhatsApp")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Préciser Service") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix (DH)", min_value=0)
        n_deb = cc.date_input("Date de Début", today) # 💡 RESTORED
        n_dur = cc.number_input("Durée (Mois)", min_value=1, value=1)
        
        if st.button("🚀 Enregistrer au Cloud"):
            if n_nom and n_phone:
                n_fin = n_deb + relativedelta(months=int(n_dur))
                c_sheet_obj.append_row([n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"])
                st.success("✅ Synchro réussie!")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Days"]
        edited = st.data_editor(df[cols], use_container_width=True, num_rows="dynamic", disabled=["Days", "Date Fin"])
        if st.button("💾 Sauvegarder Changes"):
            final_df = edited.drop(columns=['Days'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Database Updated!")
            st.rerun()

# TAB 3: AUTO-RAPPELS (PRO STYLE)
with t3:
    st.subheader("🤖 WhatsApp Automation Center")
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    
    if not urgent.empty:
        # PRO MESSAGE
        st.info(f"🚀 **Système d'Alerte :** {len(urgent)} client(s) nécessitent une attention immédiate.")
        
        if st.button("🚀 BULK SEND (Ouvrir tous les onglets)"):
            for _, r in urgent.iterrows():
                msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire bientôt ({r['Date_Display']}). On renouvelle?"
                wa_url = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<meta http-equiv="refresh" content="0;URL={wa_url}">', unsafe_allow_html=True)
        
        st.markdown("---")
        for _, r in urgent.iterrows():
            c_l, c_r = st.columns([3, 1])
            c_l.warning(f"👤 {r['Nom']} | 📺 {r['Service']} | ⏳ {r['Days']} jours")
            wa_link = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(f'Bonjour {r[0]}, renouvellement?')}"
            c_r.link_button("📲 Tirer", wa_link)
    else: st.success("Empire is safe. No alerts.")

# TAB 4: REÇUS
with t4:
    if not df.empty:
        sel = st.selectbox("Client pour reçu:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"*REÇU - {st.session_state['biz_name']}*\n👤 Client: {c['Nom']}\n📺 Service: {c['Service']}\n💰 Prix: {c['Prix']} DH\n⌛ Expire le: {c['Date_Display']}\n\n*Merci !*"
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

st.sidebar.button("Déconnexion", on_click=lambda: st.session_state.clear())
