import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V39 - THE NEON SUPREMACY (MAX CONTRAST)
st.set_page_config(page_title="EMPIRE_V39", layout="wide", page_icon="💎")

# ⚡ THE NUCLEAR CSS FIX - FORCE VISIBILITY
st.markdown("""
    <style>
    /* 1. Force Background for the whole app */
    .stApp { background-color: #0b0e14 !important; }

    /* 2. Force ga3 l-ktaba t-welli BIDA (White) */
    h1, h2, h3, h4, h5, h6, p, span, label, div, .stMarkdown {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* 3. Metrics Box Styling - High Contrast */
    div[data-testid="stMetric"] {
        background: #161b22 !important;
        border: 2px solid #00d2ff !important;
        border-radius: 15px !important;
        padding: 20px !important;
        box-shadow: 0 4px 20px rgba(0, 210, 255, 0.15) !important;
    }
    
    /* Neon Colors for Numbers */
    div[data-testid="stMetricValue"] > div {
        color: #00ff9d !important;
        font-size: 40px !important;
        font-weight: 900 !important;
    }
    
    /* White Labels for Metrics */
    div[data-testid="stMetricLabel"] p {
        color: #ffffff !important;
        font-size: 17px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
    }

    /* 4. Input Fields Labels Visibility */
    label[data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
    }

    /* 5. Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22 !important;
        color: #FFFFFF !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 12px 25px !important;
        border: 1px solid #30363d !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00d2ff !important;
        color: #000000 !important;
    }

    /* 6. The Business Banner */
    .biz-banner {
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        padding: 30px;
        border-radius: 15px;
        color: #FFFFFF !important;
        text-align: center;
        font-size: 45px;
        font-weight: 900;
        margin-bottom: 30px;
        border: 3px solid #ffffff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# MASTER ADMIN ID
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=scope))

client = get_gspread_client()

# --- 1. LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.markdown('<div class="biz-banner">🏦 SAAS MANAGEMENT PORTAL</div>', unsafe_allow_html=True)
    col_l, col_r = st.columns([1, 1])
    with col_l:
        u_in = st.text_input("Identifiant Business (Username):")
        p_in = st.text_input("Mot de passe (Password):", type="password")
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
                        b_name = str(match.iloc[0]['Business_Name']).strip()
                        st.session_state["biz_name"] = b_name if b_name != 'nan' and b_name != "" else f"{u_in.upper()} PRO"
                        st.session_state["sheet_name"] = str(match.iloc[0]['Sheet_Name']).strip()
                        st.rerun()
                    else: st.error("🚫 Accès Bloqué.")
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
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce')
    df['Jours Restants'] = df['Date Fin'].apply(lambda x: (x.date() - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = df['Date Fin'].dt.strftime('%Y-%m-%d').fillna("Non défini")
    df.loc[(df['Jours Restants'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 3. THE INTERFACE ---
st.markdown(f'<div class="biz-banner">🚀 {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS", "👥 GESTION", "🔔 ALERTES", "📄 REÇUS"])

# TAB 1: ANALYTICS
with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("✅ CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("🚨 RELANCES (3j)", len(df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]))

        g1, g2 = st.columns([2, 1])
        with g1:
            st.plotly_chart(px.bar(df.groupby('Service')['Prix'].sum().reset_index(), x='Service', y='Prix', title="Revenue / Service", template="plotly_dark"), use_container_width=True)
        with g2:
            st.plotly_chart(px.pie(df, names='Status', title="Status Distribution", hole=0.5, template="plotly_dark"), use_container_width=True)

# TAB 2: GESTION
with t2:
    with st.expander("➕ AJOUTER UN NOUVEAU CLIENT"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom Complet")
        n_phone = ca.text_input("WhatsApp")
        n_email = ca.text_input("Email Client")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Préciser Service") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix", min_value=0)
        n_dur = cc.number_input("Durée (Mois)", min_value=1, value=1)
        if st.button("💾 Enregistrer dans le Cloud"):
            if n_nom and n_phone:
                n_fin = today + relativedelta(months=int(n_dur))
                c_sheet_obj.append_row([n_nom, str(n_phone), n_email, final_s, n_prix, str(today), n_dur, str(n_fin), "Actif"])
                st.success("✅ Sync OK!")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Status", "Jours Restants", "Date_Display"]
        edited = st.data_editor(df[cols], use_container_width=True, num_rows="dynamic", disabled=["Jours Restants", "Date_Display"])
        if st.button("💾 Valider les Modifications"):
            final_df = edited.drop(columns=['Jours Restants', 'Date_Display'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Cloud Updated!")
            st.rerun()

# TAB 3: ALERTES
with t3:
    st.subheader("Relances WhatsApp 📲")
    urgent = df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            col_l, col_r = st.columns([3, 1])
            icon = "🔴" if r['Jours Restants'] <= 0 else "🟠"
            col_l.warning(f"{icon} **{r['Nom']}** | {r['Service']} | **{r['Jours Restants']} j** (Expire: {r['Date_Display']})")
            wa = f"https://wa.me/{r['Phone']}?text=Bonjour {r['Nom']}, renouvellement {r['Service']}? Fin le {r['Date_Display']}"
            col_r.link_button("📲 Rappeler", wa)
    else: st.success("Aucun retard.")

# TAB 4: REÇUS
with t4:
    if not df.empty:
        sel = st.selectbox("Choisir klyan:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"*REÇU - {st.session_state['biz_name']}*\n👤 Client: {c['Nom']}\n📺 Service: {c['Service']}\n💰 Prix: {c['Prix']} DH\n⌛ Expire: {c['Date_Display']}\n*Merci !*"
        st.code(reçu)
        st.link_button("📲 WhatsApp Direct", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

if st.sidebar.button("Déconnexion"):
    st.session_state.clear()
    st.rerun()
