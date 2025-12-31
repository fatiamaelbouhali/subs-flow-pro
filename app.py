import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px
import io

# SYSTEM STATUS: OMEGA V87 - THE REACT-STYLE EMPIRE (ULTRA DARK PRO)
st.set_page_config(page_title="EMPIRE_PRO_V87", layout="wide", page_icon="🛡️")

# ⚡ THE SUPREME REACT-STYLE CSS (SLATE 950 & TEAL)
st.markdown("""
    <style>
    /* 1. Global Futuristic Dark Theme */
    .stApp {
        background-color: #020617 !important;
        background-image: radial-gradient(circle at top right, rgba(20, 184, 166, 0.05), transparent),
                          radial-gradient(circle at bottom left, rgba(139, 92, 246, 0.05), transparent) !important;
        color: #f8fafc !important;
    }

    /* 2. Professional Sidebar (Slate 900) */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* 3. Navigation Buttons (Teal-500 Style) */
    div[role="radiogroup"] { gap: 15px !important; }
    div[role="radiogroup"] label {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[role="radiogroup"] label:hover {
        background-color: rgba(20, 184, 166, 0.1) !important;
        border-color: #14b8a6 !important;
        transform: translateX(5px);
    }
    div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(90deg, rgba(20, 184, 166, 0.2) 0%, transparent 100%) !important;
        border: 1px solid #14b8a6 !important;
        border-left: 5px solid #14b8a6 !important;
    }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] + div div div { display: none !important; }

    /* 4. Luxury Metrics Cards */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
    }
    div[data-testid="stMetricValue"] > div { 
        color: #14b8a6 !important; 
        font-size: 38px !important; 
        font-weight: 900 !important;
        letter-spacing: -1px !important;
    }
    div[data-testid="stMetricLabel"] p { color: #94a3b8 !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 2px; }

    /* 5. Inputs (Glassmorphism) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #020617 !important;
        border: 2px solid #1e293b !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    label p { color: #14b8a6 !important; font-weight: 900 !important; text-transform: uppercase; font-size: 0.8rem; }

    /* 6. Professional Header Banner */
    .react-banner {
        background: rgba(15, 23, 42, 0.8);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding: 20px 40px;
        margin: -4rem -4rem 2rem -4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CONFIG DICTIONARY ---
LANGS = {
    "FR": {"nav1": "📊 ANALYTICS", "nav2": "👥 GESTION", "nav3": "🔔 RAPPELS", "nav4": "📄 REÇUS", "logout": "Déconnexion", "ident": "Username", "pass": "Access Key"},
    "AR": {"nav1": "📊 الإحصائيات", "nav2": "👥 إدارة الزبناء", "nav3": "🔔 التنبيهات", "nav4": "📄 الوصولات", "logout": "خروج", "ident": "إسم المستخدم", "pass": "كلمة السر"}
}

# MASTER ADMIN ID
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_client():
    creds = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']))

client = get_client()

# --- 2. LOGIN SYSTEM (REACT LOOK) ---
if "auth" not in st.session_state:
    st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh;">
            <div style="background: rgba(15, 23, 42, 0.5); padding: 40px; border-radius: 30px; border: 1px solid rgba(255,255,255,0.1); width: 400px; text-align: center;">
                <h1 style="color: white; font-weight: 900; letter-spacing: -2px; font-size: 32px;">EMPIRE <span style="color: #14b8a6;">GATEWAY</span></h1>
                <p style="color: #64748b; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 30px;">Secured Enterprise SaaS</p>
    """, unsafe_allow_html=True)
    
    u_in = st.text_input("Commander Identity")
    p_in = st.text_input("Access Key", type="password")
    
    if st.button("AUTHORIZE ACCESS"):
        try:
            m_sheet = client.open("Master_Admin").sheet1
            m_df = pd.DataFrame(m_sheet.get_all_records())
            match = m_df[(m_df['User'].astype(str) == str(u_in)) & (m_df['Password'].astype(str) == str(p_in))]
            if not match.empty:
                user_row = match.iloc[0]
                st.session_state.update({"auth": True, "user": u_in, "biz_name": str(user_row['Business_Name']), "sheet_name": str(user_row['Sheet_Name'])})
                st.rerun()
        except: st.error("Invalid Credentials.")
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# --- 3. DATA LOADING ---
try:
    c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
    df = pd.DataFrame(c_sheet_obj.get_all_records())
except: st.error("Sync Error"); st.stop()

today = datetime.now().date()
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = pd.to_datetime(df['Date Fin']).dt.strftime('%Y-%m-%d').fillna("N/A")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f'<h2 style="color: white; font-weight: 900; font-style: italic;">EMPIRE<span style="color: #14b8a6;">.</span></h2>', unsafe_allow_html=True)
    sel_lang = st.selectbox("Language", ["FR", "AR"], label_visibility="collapsed")
    L = LANGS[sel_lang]
    st.markdown("---")
    menu = st.radio("NAV", [L["nav1"], L["nav2"], L["nav3"], L["nav4"]], label_visibility="collapsed")
    st.markdown("---")
    if st.button(L["logout"]): st.session_state.clear(); st.rerun()

# --- 5. MAIN INTERFACE ---
# Custom React-Style Top Header
st.markdown(f"""
    <div class="react-banner">
        <div>
            <h2 style="margin:0; font-weight: 900; color: white;">{st.session_state['biz_name']}</h2>
            <p style="margin:0; color: #14b8a6; font-size: 10px; font-weight: 900; letter-spacing: 3px;">CLOUD SYNC ACTIVE</p>
        </div>
        <div style="text-align: right;">
            <p style="margin:0; color: #64748b; font-size: 10px; font-weight: 900;">ADMIN_COMMANDER</p>
            <p style="margin:0; color: white; font-size: 12px; font-weight: bold;">{st.session_state['user'].upper()}</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# NAV 1: ANALYTICS
if menu == L["nav1"]:
    c1, c2, c3 = st.columns(3)
    c1.metric("REVENUE TOTAL", f"{df['Prix'].sum()} DH")
    c2.metric("CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
    c3.metric("ALERTES CRITIQUES", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
    st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="plotly_dark"), use_container_width=True)

# NAV 2: GESTION
elif menu == L["nav2"]:
    st.markdown("### ➕ ADD NEW ASSET")
    ca, cb, cc = st.columns(3)
    n_nom = ca.text_input("Nom Client")
    n_phone = ca.text_input("WhatsApp Number")
    n_serv = cb.selectbox("Service Type", ["Netflix", "IPTV", "Canva", "ChatGPT", "Autre"])
    n_prix = cb.number_input("Value (DH)", min_value=0)
    n_dur = cc.number_input("Duration (Months)", min_value=1)
    if st.button("EXECUTE ENROLLMENT"):
        n_fin = today + relativedelta(months=int(n_dur))
        c_sheet_obj.append_row([n_nom, n_phone, "", n_serv, n_prix, str(today), n_dur, str(n_fin), "Actif"])
        st.success("PROTOCOL SYNCED!"); st.rerun()
    st.markdown("---")
    st.data_editor(df, use_container_width=True, num_rows="dynamic")

# NAV 3: RAPPELS
elif menu == L["nav3"]:
    st.markdown("### 🔔 RELIABILITY PROTOCOL")
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            st.warning(f"👤 {r['Nom']} | 📺 {r['Service']} | ⏳ {r['Days']} j")
            wa = f"https://wa.me/{r['Phone']}?text=Bonjour, votre abonnement expire bientôt."
            st.link_button("📲 TIRER", wa)

# NAV 4: RECEIPTS
elif menu == L["nav4"]:
    st.markdown("### 📄 DOCUMENT GENERATOR")
    sel = st.selectbox("Select Target", df['Nom'].unique())
    c = df[df['Nom'] == sel].iloc[0]
    st.code(f"EMPIRE RECEIPT\nUser: {c['Nom']}\nService: {c['Service']}\nStatus: PAID")
