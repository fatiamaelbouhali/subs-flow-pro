import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px
import io

# SYSTEM STATUS: OMEGA V88 - VIBRANT PROFESSIONAL UI (GESTION FIRST)
st.set_page_config(page_title="EMPIRE_PRO_V88", layout="wide", page_icon="🛡️")

# ⚡ THE SUPREME VIBRANT CSS - HIGH CONTRAST & LUXURY
st.markdown("""
    <style>
    /* 1. Global Light Vibrant Theme */
    .stApp { background-color: #f8fafc !important; }
    
    /* 2. Professional Sidebar (Navy Blue) */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 2px solid #e2e8f0 !important;
    }
    
    /* Sidebar Text & Labels */
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }

    /* 3. Navigation Links (Teal & White) */
    div[role="radiogroup"] { gap: 8px !important; }
    div[role="radiogroup"] label {
        background-color: transparent !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        transition: 0.3s !important;
        border: 1px solid transparent !important;
    }
    div[role="radiogroup"] label:hover { background-color: rgba(45, 212, 191, 0.1) !important; border-color: #2dd4bf !important; }
    
    /* Active Tab Style */
    div[role="radiogroup"] label[data-checked="true"] {
        background: #2dd4bf !important; /* Vibrant Teal */
        color: #0f172a !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(45, 212, 191, 0.4) !important;
    }
    div[role="radiogroup"] label[data-checked="true"] p { color: #0f172a !important; font-weight: 900 !important; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] + div div div { display: none !important; }

    /* 4. Metrics Cards Luxury (White & Pro Blue) */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05) !important;
    }
    div[data-testid="stMetricValue"] > div { color: #0f172a !important; font-size: 38px !important; font-weight: 900; }
    div[data-testid="stMetricLabel"] p { color: #64748b !important; font-size: 15px !important; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }

    /* 5. Inputs & Borders (360° Perfection) */
    .stTextInput input, .stNumberInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"], .stDateInput input {
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        height: 48px !important;
    }
    label p { color: #334155 !important; font-weight: 800 !important; }

    /* 6. Professional Table (Summary) */
    .summary-table {
        width: 100%; border-collapse: collapse; border-radius: 15px; overflow: hidden;
        margin: 20px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }
    .summary-table thead tr { background-color: #0f172a !important; color: white !important; font-weight: 900; }
    .summary-table td { padding: 15px; text-align: center; background-color: white; color: #0f172a; font-weight: 700; border-bottom: 1px solid #f1f5f9; }

    /* Buttons Pro */
    .stButton button {
        background: #2dd4bf !important;
        color: #0f172a !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 30px !important;
        box-shadow: 0 4px 12px rgba(45, 212, 191, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CONFIG & CONNECTION ---
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"
def get_client():
    creds = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']))

client = get_client()

# --- 2. LOGIN ---
if "auth" not in st.session_state:
    st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh;">
            <div style="background: white; padding: 40px; border-radius: 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.1); width: 450px; text-align: center; border: 1px solid #e2e8f0;">
                <h1 style="color: #0f172a; font-weight: 900; letter-spacing: -2px; font-size: 35px;">EMPIRE <span style="color: #2dd4bf;">GATEWAY</span></h1>
                <p style="color: #64748b; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 30px;">Professional SaaS Solution</p>
    """, unsafe_allow_html=True)
    u = st.text_input("Username:")
    p = st.text_input("Access Key:", type="password")
    if st.button("AUTHORIZE ACCESS"):
        m_sheet = client.open("Master_Admin").sheet1
        m_df = pd.DataFrame(m_sheet.get_all_records())
        match = m_df[(m_df['User'].astype(str) == str(u)) & (m_df['Password'].astype(str) == str(p))]
        if not match.empty:
            user_row = match.iloc[0]
            st.session_state.update({"auth": True, "user": u, "biz_name": str(user_row['Business_Name']), "sheet_name": str(user_row['Sheet_Name'])})
            st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# --- 3. DATA LOADING ---
c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
df = pd.DataFrame(c_sheet_obj.get_all_records())
today = datetime.now().date()

if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = pd.to_datetime(df['Date Fin']).dt.strftime('%Y-%m-%d').fillna("N/A")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 4. SIDEBAR NAVIGATION (ORDERED: GESTION FIRST) ---
LANGS = {
    "FR": {"nav1": "👥 GESTION", "nav2": "📊 ANALYTICS", "nav3": "🔔 RAPPELS", "nav4": "📄 REÇUS", "logout": "Déconnexion", "export": "Télécharger Data"},
    "AR": {"nav1": "👥 إدارة الزبناء", "nav2": "📊 الإحصائيات", "nav3": "🔔 التنبيهات", "nav4": "📄 الوصولات", "logout": "خروج", "export": "تحميل البيانات"}
}

with st.sidebar:
    st.markdown(f'<h2 style="color: white; font-weight: 900; font-style: italic;">EMPIRE<span style="color: #2dd4bf;">.</span></h2>', unsafe_allow_html=True)
    sel_lang = st.selectbox("🌍", ["FR", "AR"], label_visibility="collapsed")
    L = LANGS[sel_lang]
    st.markdown("---")
    # GESTION IS NOW THE FIRST ITEM
    menu = st.radio("NAV", [L["nav1"], L["nav2"], L["nav3"], L["nav4"]], label_visibility="collapsed")
    st.markdown("---")
    if st.button(L["logout"]): st.session_state.clear(); st.rerun()

# --- 5. BODY ---
st.markdown(f'<h1 style="color: #0f172a; font-weight: 900; font-size: 42px; margin-bottom: 0;">🚀 {st.session_state["biz_name"]}</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #2dd4bf; font-weight: 800; letter-spacing: 3px; font-size: 12px; margin-top:0;">CLOUD SYNC ACTIVE</p>', unsafe_allow_html=True)
st.markdown("---")

# PAGE: GESTION (THE NEW HOME)
if menu == L["nav1"]:
    st.markdown("### ➕ ADD NEW CLIENT")
    ca, cb, cc = st.columns(3)
    n_nom = ca.text_input("Nom Complet")
    n_phone = ca.text_input("WhatsApp (ex: 212...)")
    n_email = ca.text_input("Email")
    s_choice = cb.selectbox("Service", ["Netflix", "IPTV", "Canva", "ChatGPT", "Autre"])
    final_s = cb.text_input("Nom Service") if s_choice == "Autre" else s_choice
    n_prix = cc.number_input("Prix (DH)", min_value=0)
    n_dur = cc.number_input("Durée (Mois)", min_value=1)
    if st.button("🚀 EXECUTE ENROLLMENT"):
        n_fin = today + relativedelta(months=int(n_dur))
        new_row = [n_nom, n_phone, n_email, final_s, n_prix, str(today), n_dur, str(n_fin), "Actif"]
        # Force sync logic
        df_clean = df.drop(columns=['Days', 'Date_Display'], errors='ignore')
        df_new = pd.concat([df_clean, pd.DataFrame([dict(zip(df_clean.columns, new_row))])], ignore_index=True)
        c_sheet_obj.clear(); c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
        st.success("PROTOCOL SYNCED!"); st.rerun()
    st.markdown("---")
    st.markdown("### 📋 ACTIVE DATABASE")
    st.data_editor(df, use_container_width=True, num_rows="dynamic")

# PAGE: ANALYTICS (WITH SUMMARY TABLE)
elif menu == L["nav2"]:
    c1, c2, c3 = st.columns(3)
    c1.metric("REVENUE TOTAL", f"{df['Prix'].sum()} DH")
    c2.metric("ACTIFS", len(df[df['Status'] == 'Actif']))
    c3.metric("ALERTES (3j)", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
    
    st.markdown("### 📋 RÉSUMÉ PAR SERVICE")
    if not df.empty:
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'Total (DH)']
        st.write(summary.to_html(classes='summary-table', index=False, border=0), unsafe_allow_html=True)
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="simple_white"), use_container_width=True)

# PAGE: RAPPELS
elif menu == L["nav3"]:
    st.header("🔔 RELIABILITY PROTOCOL")
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} jours")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire bientôt. On renouvelle?"
            cr.link_button("📲 WHATSAPP", f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}")
    else: st.success("Ga3 l-Empire m-rgl!")

# PAGE: REÇUS
elif menu == L["nav4"]:
    st.header("📄 DOCUMENT GENERATOR")
    if not df.empty:
        sel = st.selectbox("Target:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"✅ REÇU - {st.session_state['biz_name']}\n👤 User: {c['Nom']}\n💰 Prix: {c['Prix']} DH\n⌛ Expire: {c['Date_Display']}"
        st.code(reçu)
        st.link_button("📲 SEND VIA WHATSAPP", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")
