import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px
import io

# SYSTEM STATUS: OMEGA V89 - TRI-COLOR SUPREMACY (PINK, BLUE, MUSTARD)
st.set_page_config(page_title="EMPIRE_PRO_V89", layout="wide", page_icon="🛡️")

# --- 1. LANGUAGE DICTIONARY ---
LANGS = {
    "FR": {
        "nav1": "👥 GESTION", "nav2": "📊 ANALYTICS", "nav3": "🔔 RAPPELS", "nav4": "📄 REÇUS",
        "rev": "REVENUE TOTAL", "act": "CLIENTS ACTIFS", "alrt": "ALERTES (3j)", "add_title": "➕ ADD NEW CLIENT",
        "save": "🚀 EXECUTE ENROLLMENT", "export": "📥 Download Data", "msg": "Bonjour, votre abonnement expire bientôt.",
        "sum_title": "📋 RÉSUMÉ PAR SERVICE", "logout": "Déconnexion", "propre": "Ga3 l-Empire m-rgl!"
    },
    "AR": {
        "nav1": "👥 إدارة الزبناء", "nav2": "📊 الإحصائيات", "nav3": "🔔 التنبيهات", "nav4": "📄 الوصولات",
        "rev": "إجمالي الأرباح", "act": "المشتركون", "alrt": "تنبيهات", "add_title": "➕ إضافة زبون جديد",
        "save": "🚀 حفظ في السحابة", "export": "📥 تحميل البيانات", "msg": "السلام عليكم، اشتراككم سينتهي قريبا.",
        "sum_title": "📋 ملخص الخدمات", "logout": "خروج", "propre": "كل شيء منظم."
    }
}

# --- 2. SIDEBAR NAV & SETTINGS ---
with st.sidebar:
    st.markdown(f'<h2 style="color: white; font-weight: 900; font-style: italic;">EMPIRE<span style="color: #2dd4bf;">.</span></h2>', unsafe_allow_html=True)
    sel_lang = st.selectbox("🌍", ["FR", "AR"], label_visibility="collapsed")
    L = LANGS[sel_lang]
    st.markdown("---")
    menu = st.radio("NAV", [L["nav1"], L["nav2"], L["nav3"], L["nav4"]], label_visibility="collapsed")

# ⚡ THE SUPREME COLORS CSS (ROSE, BLUE, MUSTARD)
st.markdown(f"""
    <style>
    /* 1. Background Rose Barad m3a Blue khfif */
    .stApp {{ 
        background-color: #fff5f7 !important; 
        background-image: radial-gradient(at 0% 0%, hsla(197,81%,92%,1) 0, transparent 50%), 
                          radial-gradient(at 100% 100%, hsla(339,49%,96%,1) 0, transparent 50%) !important;
    }}
    
    /* 2. Sidebar Navy Blue (React Style) */
    [data-testid="stSidebar"] {{ background-color: #0f172a !important; border-right: 3px solid #ec4899; }}
    
    /* 3. Navigation Buttons */
    div[role="radiogroup"] label {{ background-color: transparent !important; border-radius: 12px !important; padding: 12px 20px !important; transition: 0.3s !important; }}
    div[role="radiogroup"] label:hover {{ background-color: rgba(45, 212, 191, 0.1) !important; border: 1px solid #2dd4bf !important; }}
    div[role="radiogroup"] label[data-checked="true"] {{ background: #2dd4bf !important; border: none !important; box-shadow: 0 4px 15px rgba(45, 212, 191, 0.4) !important; }}
    div[role="radiogroup"] label[data-checked="true"] p {{ color: #0f172a !important; font-weight: 900 !important; }}
    div[role="radiogroup"] [data-testid="stWidgetLabel"] + div div div {{ display: none !important; }}

    /* 4. Banner Pro (Mustard to Pink) */
    .biz-banner {{ 
        background: linear-gradient(135deg, #f59e0b 0%, #ec4899 100%); 
        padding: 25px; border-radius: 20px; color: white !important; text-align: center; 
        font-size: 35px; font-weight: 900; margin-bottom: 25px; border: 4px solid #ffffff; 
        box-shadow: 0 10px 30px rgba(236, 72, 153, 0.3);
    }}

    /* 5. Metrics (White & Blue Border) */
    div[data-testid="stMetric"] {{ background: white !important; border: 2px solid #1e3a8a; border-radius: 15px; padding: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
    div[data-testid="stMetricValue"] > div {{ color: #db2777 !important; font-weight: 900 !important; }}

    /* 6. Inputs - Bordo Borders (360 Fix) */
    .stTextInput input, .stNumberInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"], .stDateInput input {{
        border: 3px solid #800000 !important; border-radius: 12px !important;
        background-color: #ffffff !important; color: #1e3a8a !important;
        font-weight: 800 !important; height: 48px !important;
    }}
    label p {{ color: #800000 !important; font-weight: 900 !important; }}

    /* 7. Summary Table */
    .luxury-table {{ width: 100%; border-collapse: collapse; border-radius: 15px; overflow: hidden; margin: 20px 0; }}
    .luxury-table thead tr {{ background-color: #f59e0b !important; color: white !important; font-weight: 900; }}
    .luxury-table td {{ padding: 15px; text-align: center; background-color: white; color: #1e3a8a; font-weight: bold; border-bottom: 1px solid #ddd; }}
    
    .stButton button {{
        background: linear-gradient(90deg, #f59e0b 0%, #1e3a8a 100%) !important;
        color: white !important; border-radius: 12px !important; font-weight: 900 !important; padding: 12px 40px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONNECTION ---
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"
def get_client():
    creds = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']))

client = get_client()

# --- 4. LOGIN ---
if "auth" not in st.session_state:
    st.markdown('<div class="biz-banner">🛡️ EMPIRE SaaS GATEWAY</div>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 2, 1])
    with col_log:
        u_in = st.text_input("Username:")
        p_in = st.text_input("Password:", type="password")
        if st.button("Unlock"):
            m_sheet = client.open("Master_Admin").sheet1
            m_df = pd.DataFrame(m_sheet.get_all_records())
            match = m_df[(m_df['User'].astype(str) == str(u_in)) & (m_df['Password'].astype(str) == str(p_in))]
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

# SIDEBAR FOOTER
with st.sidebar:
    st.markdown("---")
    if st.button(L["logout"]): st.session_state.clear(); st.rerun()

# --- 6. BODY ---
st.markdown(f'<div class="biz-banner">👤 {st.session_state["biz_name"]} 🚀</div>', unsafe_allow_html=True)

# PAGE GESTION
if menu == L["nav1"]:
    st.markdown(f"### {L['add_title']}")
    ca, cb, cc = st.columns(3)
    with ca:
        n_nom = st.text_input("Nom / الإسم")
        n_phone = st.text_input("WhatsApp")
    with cb:
        n_email = st.text_input("Email")
        s_choice = st.selectbox("Service", ["Netflix", "IPTV", "Canva", "ChatGPT", "Autre"])
        final_s = st.text_input("Service Name") if s_choice == "Autre" else s_choice
    with cc:
        n_prix = st.number_input("Prix", min_value=0)
        n_deb = st.date_input("Start Date", today)
        n_dur = st.number_input("Months", min_value=1, value=1)
    if st.button(L["save"], use_container_width=True):
        if n_nom and n_phone:
            n_fin = n_deb + relativedelta(months=int(n_dur))
            new_r = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"]
            df_clean = df.drop(columns=['Days', 'Date_Display'], errors='ignore')
            df_new = pd.concat([df_clean, pd.DataFrame([dict(zip(df_clean.columns, new_r))])], ignore_index=True)
            c_sheet_obj.clear(); c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
            st.success("PROTOCOL SYNCED!"); st.rerun()
    st.markdown("---")
    st.data_editor(df, use_container_width=True, num_rows="dynamic")

# PAGE ANALYTICS
elif menu == L["nav2"]:
    c1, c2, c3 = st.columns(3)
    c1.metric(L["rev"], f"{df['Prix'].sum()} DH")
    c2.metric(L["act"], len(df[df['Status'] == 'Actif']))
    c3.metric(L["alrt"], len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
    st.markdown(f"### {L['sum_title']}")
    if not df.empty:
        sum_df = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        sum_df.columns = ['Service', 'Clients', 'CA Total']
        st.write(sum_df.to_html(classes='luxury-table', index=False, border=0), unsafe_allow_html=True)
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="simple_white"), use_container_width=True)

# PAGE RAPPELS
elif menu == L["nav3"]:
    st.header(L["nav3"])
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} j")
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(L['msg'])}"
            cr.link_button("📲 TIRER", wa)
    else: st.success(L["propre"])

# PAGE REÇUS
elif menu == L["nav4"]:
    st.header(L["nav4"])
    sel = st.selectbox("Select Target:", df['Nom'].unique())
    c = df[df['Nom'] == sel].iloc[0]
    reçu = f"✅ *REÇU - {st.session_state['biz_name']}*\n👤 User: {c['Nom']}\n💰 Prix: {c['Prix']} DH\n⌛ Expire: {c['Date_Display']}"
    st.code(reçu)
    st.link_button("📲 SEND", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")
