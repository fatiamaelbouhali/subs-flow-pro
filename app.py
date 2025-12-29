import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V45 - PERFECT VISIBILITY ENGINE
st.set_page_config(page_title="EMPIRE_PRO_V45", layout="wide", page_icon="💎")

# ⚡ CSS DIAL L-M3ALLMIN (FIXED FOR INPUTS & LABELS)
st.markdown("""
    <style>
    /* Force Background Dark */
    .stApp { background-color: #0b0e14 !important; }
    
    /* 1. Force GA3 l-Titles o l-Labels i-welliw BIDOUN (White) */
    h1, h2, h3, h4, h5, h6, .stMarkdown p, .stMarkdown span { color: #FFFFFF !important; }
    label[data-testid="stWidgetLabel"] p { color: #FFFFFF !important; font-weight: bold !important; font-size: 1.1rem !important; }

    /* 2. Metrics Box Style */
    div[data-testid="stMetric"] {
        background: #161b22 !important;
        border: 2px solid #00d2ff !important;
        border-radius: 15px !important;
        padding: 15px !important;
    }
    div[data-testid="stMetricValue"] > div { color: #00ff9d !important; font-weight: 900 !important; }
    div[data-testid="stMetricLabel"] p { color: #ffffff !important; font-weight: 700 !important; }

    /* 3. INPUT BOXES FIX (Text inside stays readable) */
    input, select, .stSelectbox div { color: #000000 !important; background-color: #ffffff !important; font-weight: 500 !important; }

    /* 4. Tabs Visibility */
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; font-weight: bold !important; }
    .stTabs [aria-selected="true"] { background-color: #00d2ff !important; color: #000000 !important; border-radius: 5px; }

    /* 5. The Pro Banner */
    .biz-banner {
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        padding: 25px; border-radius: 12px; color: #FFFFFF !important;
        text-align: center; font-size: 40px; font-weight: 900;
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

# --- LOGIN ---
if "auth" not in st.session_state:
    st.markdown('<div class="biz-banner">🏦 SaaS Empire Login</div>', unsafe_allow_html=True)
    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
    if st.button("Unleash"):
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
            else: st.error("❌ Identifiants ghalat.")
        except Exception as e: st.error(f"Error: {e}")
    st.stop()

# --- LOAD DATA ---
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

# --- UI ---
st.markdown(f'<div class="biz-banner">🚀 {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 DASHBOARD", "👥 GESTION", "🤖 AUTO-BOT", "📄 REÇUS"])

with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("ALERTES", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
        
        st.markdown("### 📋 Résumé des Revenus par Service")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'Total (DH)']
        st.table(summary)
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="plotly_dark"), use_container_width=True)

with t2:
    with st.expander("➕ AJOUTER UN CLIENT"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom Complet")
        n_phone = ca.text_input("WhatsApp")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "IPTV", "Autre"])
        final_s = cb.text_input("Préciser Service") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix (DH)", min_value=0)
        n_deb = cc.date_input("Date de Début", today)
        n_dur = cc.number_input("Durée (Mois)", min_value=1, value=1)
        if st.button("🚀 Enregistrer"):
            if n_nom and n_phone:
                n_fin = n_deb + relativedelta(months=int(n_dur))
                c_sheet_obj.append_row([n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"])
                st.success("✅ Synced!")
                st.rerun()

    st.markdown("---")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder Changes"):
        final_df = edited.drop(columns=['Days', 'Date_Display'], errors='ignore')
        c_sheet_obj.clear()
        c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
        st.success("✅ Cloud Updated!")
        st.rerun()

with t3:
    st.subheader("🤖 WhatsApp Automation Center")
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        st.info(f"🚀 **Action Immédiate :** {len(urgent)} relances à faire.")
        if st.button("🚀 TIRER TOUT (Bulk Mode)"):
            for _, r in urgent.iterrows():
                msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire bientot ({r['Date_Display']})."
                wa_url = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<meta http-equiv="refresh" content="0;URL={wa_url}">', unsafe_allow_html=True)
        for _, r in urgent.iterrows():
            st.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} j")
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(f'Bonjour {r[0]}, renouvellement?')}"
            st.link_button("📲 Rappeler", wa)
    else: st.success("Aucun retard.")

with t4:
    if not df.empty:
        sel = st.selectbox("Client pour reçu:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"*REÇU - {st.session_state['biz_name']}*\n👤 Client: {c['Nom']}\n📺 Service: {c['Service']}\n💰 Prix: {c['Prix']} DH\n⌛ Expire: {c['Date_Display']}\n*Merci !*"
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

st.sidebar.button("Déconnexion", on_click=lambda: st.session_state.clear())
