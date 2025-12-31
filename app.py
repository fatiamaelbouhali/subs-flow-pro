import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import io

# OMEGA V86 - THE EMPIRE UI RECOVERY (DARK SLATE EDITION)
st.set_page_config(page_title="EMPIRE_PRO_V86", layout="wide", page_icon="🛡️")

# ⚡ THE SUPREME CSS - CLONING THE REACT SIDEBAR LOOK
st.markdown("""
    <style>
    /* 1. Global Dark Theme (Slate-900) */
    .stApp { background-color: #0f172a !important; color: #f8fafc !important; }

    /* 2. Professional Sidebar Fix */
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155 !important;
        width: 300px !important;
    }

    /* 3. Navigation Buttons - React Style */
    div[role="radiogroup"] { gap: 12px !important; padding-top: 20px; }
    div[role="radiogroup"] label {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    div[role="radiogroup"] label:hover {
        background-color: #334155 !important;
        border-color: #475569 !important;
    }
    /* Active Tab Highlighter */
    div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(90deg, #1e293b 0%, #334155 100%) !important;
        border: 1px solid #14b8a6 !important; /* Teal-500 */
        border-left: 5px solid #14b8a6 !important;
    }
    /* Hide Radio Circles */
    div[role="radiogroup"] [data-testid="stWidgetLabel"] + div div div { display: none !important; }
    
    /* Nav Text Style */
    div[data-testid="stRadioButtonContactLabel"] p {
        color: #f8fafc !important; font-size: 15px !important; font-weight: 700 !important;
        text-transform: uppercase; letter-spacing: 0.5px;
    }

    /* 4. Language Switcher (Glassmorphism) */
    .lang-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 10px; border-radius: 15px; margin-bottom: 20px;
    }

    /* 5. Metrics Box Luxury */
    div[data-testid="stMetric"] {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 16px !important;
        padding: 20px !important;
    }
    div[data-testid="stMetricValue"] > div { color: #14b8a6 !important; font-size: 38px !important; font-weight: 900 !important; }

    /* 6. Inputs & Borders (360 Fix) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        border: 2px solid #334155 !important;
        background-color: #0f172a !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CONFIG DICTIONARY ---
LANGS = {
    "FR": {"nav1": "📊 DASHBOARD", "nav2": "👥 GESTION", "nav3": "🔔 RAPPELS", "nav4": "📄 REÇUS", "logout": "Déconnexion", "add": "Ajouter Client"},
    "AR": {"nav1": "📊 الإحصائيات", "nav2": "👥 إدارة الزبناء", "nav3": "🔔 التنبيهات", "nav4": "📄 الوصولات", "logout": "خروج", "add": "إضافة زبون"}
}

# --- 2. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown('<div class="lang-box">', unsafe_allow_html=True)
    sel_lang = st.selectbox("🌍", ["FR", "AR"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    L = LANGS[sel_lang]
    
    st.markdown("### MENU")
    menu = st.radio("Nav", [L["nav1"], L["nav2"], L["nav3"], L["nav4"]], label_visibility="collapsed")
    
    st.markdown("---")
    if st.button(L["logout"]):
        st.session_state.clear()
        st.rerun()

# --- 3. CONNECTION & DATA (MA-9EST WALO) ---
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"
def get_client():
    creds = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']))

# Check Auth
if "auth" not in st.session_state:
    st.title("🛡️ EMPIRE GATEWAY")
    u = st.text_input("Username:")
    p = st.text_input("Password:", type="password")
    if st.button("Login"):
        client = get_client()
        m_sheet = client.open("Master_Admin").sheet1
        m_df = pd.DataFrame(m_sheet.get_all_records())
        match = m_df[(m_df['User'] == u) & (m_df['Password'] == p)]
        if not match.empty:
            user_row = match.iloc[0]
            st.session_state.update({"auth": True, "biz_name": str(user_row['Business_Name']), "sheet_name": str(user_row['Sheet_Name'])})
            st.rerun()
    st.stop()

# Load Business Data
client = get_client()
c_sheet = client.open(st.session_state["sheet_name"]).sheet1
df = pd.DataFrame(c_sheet.get_all_records())

# --- 4. BODY ---
st.header(f"🚀 {st.session_state['biz_name']}")

if menu == L["nav1"]:
    c1, c2 = st.columns(2)
    c1.metric("REVENUE", f"{pd.to_numeric(df['Prix']).sum()} DH")
    c2.metric("CLIENTS", len(df))
    st.plotly_chart(px.bar(df, x='Service', y='Prix', template="plotly_dark"))

elif menu == L["nav2"]:
    st.subheader(L["add"])
    with st.container():
        # Formulaire en Body
        col_a, col_b = st.columns(2)
        n_nom = col_a.text_input("Nom")
        n_phone = col_a.text_input("WhatsApp")
        n_serv = col_b.selectbox("Service", ["Netflix", "IPTV", "Canva"])
        n_prix = col_b.number_input("Prix", min_value=0)
        if st.button("🚀 Enregistrer"):
            c_sheet.append_row([n_nom, n_phone, "", n_serv, n_prix, str(datetime.now().date()), 1, "", "Actif"])
            st.success("Synced!")
            st.rerun()
    st.markdown("---")
    st.data_editor(df, use_container_width=True)

# L-baqi dial les TABS (Rappels, Reçus) khllihom kif kanou...
