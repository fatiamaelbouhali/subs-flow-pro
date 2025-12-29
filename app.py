import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V50 - LUXURY SAAS DESIGN
st.set_page_config(page_title="EMPIRE_PRO_V50", layout="wide", page_icon="💎")

# ⚡ THE LUXURY UI ENGINE (PERFECT VISIBILITY & STYLE)
st.markdown("""
    <style>
    /* 1. Background Pro */
    .stApp { background-color: #0e1117 !important; }

    /* 2. Business Banner Luxury */
    .biz-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 30px;
        border-radius: 20px;
        color: #ffffff !important;
        text-align: center;
        font-size: 42px;
        font-weight: 900;
        margin-bottom: 30px;
        border-bottom: 5px solid #00d2ff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* 3. Metrics Cards (The "Wow" Factor) */
    div[data-testid="stMetric"] {
        background: #1a1c24 !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        transition: 0.3s;
    }
    div[data-testid="stMetric"]:hover { transform: translateY(-5px); border-color: #00ffcc !important; }
    
    /* Neon Green for Money */
    div[data-testid="stMetricValue"] > div {
        color: #00ff9d !important;
        font-size: 38px !important;
        font-weight: 900 !important;
    }
    
    /* Pure White for Metric Labels */
    div[data-testid="stMetricLabel"] p {
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* 4. Input Fields (NO MORE WHITE ON WHITE) */
    div[data-testid="stWidgetLabel"] p { color: #ffffff !important; font-weight: 600 !important; font-size: 1rem !important; }
    
    /* Force inputs to be white with black text for readability */
    input, select, textarea {
        color: #000000 !important;
        background-color: #ffffff !important;
        border-radius: 8px !important;
    }

    /* 5. Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1f2937 !important;
        color: #ffffff !important;
        border-radius: 10px 10px 0 0 !important;
        padding: 10px 25px !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="true"] { background-color: #3b82f6 !important; border-bottom: 4px solid #00d2ff !important; }

    /* Tables & Frames */
    .stTable, .stDataFrame { border-radius: 10px !important; overflow: hidden !important; }
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
    st.markdown('<div class="biz-banner">👑 EMPIRE MANAGEMENT PORTAL</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        u_in = st.text_input("Identifiant Business:")
        p_in = st.text_input("Access Password:", type="password")
        if st.button("Se Connecter & Dominer"):
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
                else: st.error("❌ Identifiants Ghalat.")
            except Exception as e: st.error(f"Error Master: {e}")
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

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS PRO", "👥 GESTION", "🔔 RAPPELS", "📄 REÇUS"])

with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("ALERTES", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
        
        st.markdown("### 📋 Résumé des Revenus par Service")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'Total (DH)']
        st.dataframe(summary, use_container_width=True)
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="plotly_dark", barmode='group'), use_container_width=True)

with t2:
    with st.expander("➕ AJOUTER UN NOUVEAU CLIENT"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom Complet")
        n_phone = ca.text_input("WhatsApp (ex: 212...)")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Préciser Service") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix (DH)", min_value=0)
        n_deb = cc.date_input("Date de Début", today)
        n_dur = cc.number_input("Durée (Mois)", min_value=1, value=1)
        if st.button("🚀 Valider l'Abonnement"):
            if n_nom and n_phone:
                n_fin = n_deb + relativedelta(months=int(n_dur))
                c_sheet_obj.append_row([n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"])
                st.success("✅ Synchronisation réussie !")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Days"]
        edited = st.data_editor(df[cols], use_container_width=True, num_rows="dynamic", disabled=["Days", "Date Fin"])
        if st.button("💾 Sauvegarder les modifications"):
            final_df = edited.drop(columns=['Days'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Google Sheets Synchro!")
            st.rerun()

with t3:
    st.subheader("Relances WhatsApp Intelligent 📲")
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            col_l, col_r = st.columns([3, 1])
            icon = "🔴" if r['Days'] <= 0 else "🟠"
            col_l.warning(f"{icon} **{r['Nom']}** | {r['Service']} | **{r['Days']} jours**")
            msg = f"⚠️ *RAPPEL {st.session_state['biz_name']}*\n\nBonjour {r['Nom']},\nVotre abonnement {r['Service']} expire le {r['Date_Display']}.\nSouhaitez-vous le renouveler ?"
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
            col_r.link_button("📲 Rappeler", wa)
    else: st.success("Aucun rappel urgent.")

with t4:
    st.subheader("Générateur de Reçu Pro 📄")
    if not df.empty:
        sel = st.selectbox("Sélectionner le client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = (f"✅ *REÇU DE PAIEMENT - {st.session_state['biz_name']}*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👤 Client: *{c['Nom']}*\n"
                f"📺 Service: *{c['Service']}*\n"
                f"💰 Prix: *{c['Prix']} DH*\n"
                f"⌛ Expiration: *{c['Date_Display']}*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🤝 *Merci pour votre confiance !*")
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

st.sidebar.button("Se déconnecter", on_click=lambda: st.session_state.clear())
