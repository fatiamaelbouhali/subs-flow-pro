import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px
import io

# SYSTEM STATUS: OMEGA V85 - RECOVERY & SUPREME ARCHITECT
st.set_page_config(page_title="EMPIRE_PRO_V85", layout="wide", page_icon="🛡️")

# --- 1. LANGUAGE DICTIONARY ---
LANGS = {
    "FR": {
        "ident": "Identifiant Business:", "pass": "Mot de passe:", "btn_log": "Se Connecter",
        "nav1": "📊 ANALYTICS", "nav2": "👥 GESTION", "nav3": "🔔 RAPPELS", "nav4": "📄 REÇUS",
        "rev": "REVENUE TOTAL", "act": "ACTIFS", "alrt": "ALERTES", "add_title": "➕ AJOUTER UN NOUVEAU CLIENT",
        "save": "🚀 Enregistrer au Cloud", "export": "📥 Télécharger Excel", "msg": "Bonjour, votre abonnement expire bientôt.",
        "sum_title": "📋 Résumé Business par Service", "logout": "Déconnexion", "propre": "Tout est propre."
    },
    "AR": {
        "ident": "اسم المستخدم:", "pass": "كلمة السر:", "btn_log": "تسجيل الدخول",
        "nav1": "📊 الإحصائيات", "nav2": "👥 إدارة الزبناء", "nav3": "🔔 التنبيهات", "nav4": "📄 الوصولات",
        "rev": "إجمالي الأرباح", "act": "المشتركون", "alrt": "تنبيهات", "add_title": "➕ إضافة زبون جديد",
        "save": "🚀 حفظ في السحابة", "export": "📥 تحميل إكسيل", "msg": "السلام عليكم، اشتراككم سينتهي قريبا.",
        "sum_title": "📋 ملخص الخدمات", "logout": "خروج", "propre": "كل شيء منظم."
    }
}

# --- 2. SIDEBAR (NAV & SETTINGS) ---
with st.sidebar:
    st.markdown("### ⚙️ Config")
    sel_lang = st.selectbox("🌍 Language", ["FR", "AR"])
    L = LANGS[sel_lang]
    st.markdown("---")
    st.markdown("### 🚀 Menu")
    # NAVIGATION SANS RADIOS (STYLE PRO)
    menu = st.radio("Navigation", [L["nav1"], L["nav2"], L["nav3"], L["nav4"]], label_visibility="collapsed")

# ⚡ THE SUPREME CSS - 360° BORDERS & VIBRANT SOUL
st.markdown(f"""
    <style>
    .stApp {{ background-color: #fff5f7 !important; }}
    
    /* 1. SIDEBAR NAV BUTTONS LOOK */
    div[role="radiogroup"] {{ gap: 10px; }}
    div[role="radiogroup"] label {{ 
        background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px 15px; 
        transition: 0.3s; cursor: pointer; width: 100%;
    }}
    div[role="radiogroup"] label:hover {{ border: 1px solid #ec4899; background: #fff1f2; }}
    div[data-testid="stRadioButtonContactLabel"] p {{
        font-size: 16px !important; font-weight: 800 !important; color: #1e3a8a !important;
    }}
    div[role="radiogroup"] [data-testid="stWidgetLabel"] + div div div {{ display: none !important; }}

    /* 2. FULL 360° BORDERS FIX */
    .stTextInput input, .stNumberInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"], .stDateInput input {{
        border: 3px solid #800000 !important; 
        border-bottom: 3px solid #800000 !important;
        border-radius: 14px !important;
        background-color: #ffffff !important;
        color: #1e3a8a !important;
        font-weight: 800 !important;
        height: 48px !important;
    }}
    label p {{ color: #800000 !important; font-weight: 900 !important; }}

    /* 3. Banner & Metrics */
    .biz-banner {{ background: linear-gradient(135deg, #f59e0b 0%, #ec4899 100%); padding: 20px; border-radius: 20px; color: white !important; text-align: center; font-size: 32px; font-weight: 900; margin-bottom: 25px; border: 4px solid #ffffff; box-shadow: 0 10px 30px rgba(236,72,153,0.3); }}
    div[data-testid="stMetric"] {{ background: white !important; border: 2px solid #1e3a8a; border-radius: 15px; padding: 15px; }}
    div[data-testid="stMetricValue"] > div {{ color: #db2777 !important; font-weight: 900 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONNECTION ---
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"
def get_gspread_client():
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']))

client = get_gspread_client()

# --- 4. LOGIN ---
if "auth" not in st.session_state:
    st.markdown(f'<div class="biz-banner">🛡️ EMPIRE ACCESS GATEWAY</div>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 2, 1])
    with col_log:
        u_in = st.text_input(L["ident"])
        p_in = st.text_input(L["pass"], type="password")
        if st.button(L["btn_log"]):
            m_sheet = client.open("Master_Admin").sheet1
            m_df = pd.DataFrame(m_sheet.get_all_records())
            match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
            if not match.empty:
                user_row = match.iloc[0]
                st.session_state.update({"auth": True, "user": u_in, "biz_name": str(user_row['Business_Name']), "sheet_name": str(user_row['Sheet_Name'])})
                st.rerun()
    st.stop()

# --- 5. DATA ---
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

# --- 6. BODY ---
st.markdown(f'<div class="biz-banner">👤 {st.session_state["biz_name"]} 🚀</div>', unsafe_allow_html=True)

if menu == L["nav1"]:
    c1, c2, c3 = st.columns(3)
    c1.metric(L["rev"], f"{df['Prix'].sum()} DH")
    c2.metric(L["act"], len(df[df['Status'] == 'Actif']))
    c3.metric(L["alrt"], len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
    st.markdown(f"### {L['sum_title']}")
    summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
    st.table(summary)

elif menu == L["nav2"]:
    st.markdown(f"<h2 style='text-align: center; color: #800000;'>{L['add_title']}</h2>", unsafe_allow_html=True)
    _, col_form, _ = st.columns([1, 6, 1])
    with col_form:
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom / الإسم")
        n_phone = ca.text_input("WhatsApp")
        n_email = cb.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "IPTV", "Autre"])
        final_s = st.text_input("Préciser") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix", min_value=0)
        n_deb = cc.date_input("Start Date", today)
        n_dur = st.number_input("Months", min_value=1, value=1)
        if st.button(L["save"], use_container_width=True):
            n_fin = n_deb + relativedelta(months=int(n_dur))
            c_sheet_obj.append_row([n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"])
            st.success("✅ Synced!"); st.rerun()
    st.markdown("---")
    st.data_editor(df, use_container_width=True, num_rows="dynamic")

elif menu == L["nav3"]:
    st.header(L["nav3"])
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} j")
            cr.link_button("📲 WhatsApp", f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(L['msg'])}")
    else: st.info(L["propre"])

elif menu == L["nav4"]:
    st.header(L["nav4"])
    sel = st.selectbox("Client:", df['Nom'].unique())
    c = df[df['Nom'] == sel].iloc[0]
    st.code(f"✅ REÇU - {st.session_state['biz_name']}\n👤 Client: {c['Nom']}\n💰 Prix: {c['Prix']} DH")

with st.sidebar:
    st.markdown("---")
    if st.button(L["logout"]): st.session_state.clear(); st.rerun()
