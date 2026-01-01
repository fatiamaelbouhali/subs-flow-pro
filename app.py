import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px
import io
import re

# SYSTEM STATUS: OMEGA V113 - FINAL LOGIN REPAIR & SUPREME SaaS
st.set_page_config(page_title="EMPIRE_PRO_V113", layout="wide", page_icon="🛡️")

# 💡 TODAY GLOBAL
today = datetime.now().date()

# 💡 WHATSAPP CLEANER
def clean_num(p):
    num = re.sub(r'[^0-9]', '', str(p))
    if num.startswith('00212'): num = num[5:]
    if num.startswith('0'): num = '212' + num[1:]
    elif len(num) == 9: num = '212' + num
    return num

# --- 1. LANGUAGE DICTIONARY (FIXED & UNIFIED) ---
LANGS = {
    "FR": {
        "ident": "Business Identity", "pass": "Access Key", "btn_log": "AUTHORIZE ACCESS",
        "nav1": "📊 ANALYTICS", "nav2": "👥 GESTION", "nav3": "🔔 RAPPELS", "nav4": "📄 REÇUS",
        "rev": "REVENUE TOTAL", "act": "ACTIFS", "alrt": "ALERTES", "add_title": "➕ AJOUTER UN NOUVEAU CLIENT",
        "save": "🚀 EXECUTE ENROLLMENT", "export": "📥 DOWNLOAD DATA (EXCEL)", "logout": "Déconnexion",
        "sum_title": "📋 RÉSUMÉ PAR SERVICE", "propre": "Tout est propre."
    },
    "AR": {
        "ident": "هوية العمل:", "pass": "مفتاح الدخول:", "btn_log": "تفعيل الدخول",
        "nav1": "📊 الإحصائيات", "nav2": "👥 إدارة الزبناء", "nav3": "🔔 التنبيهات", "nav4": "📄 الوصولات",
        "rev": "إجمالي الأرباح", "act": "المشتركون", "alrt": "تنبيهات", "add_title": "➕ إضافة زبون جديد",
        "save": "🚀 حفظ في السحابة", "export": "📥 تحميل البيانات (إكسيل)", "logout": "خروج",
        "sum_title": "📋 ملخص الخدمات", "propre": "كل شيء منظم."
    }
}

# --- 2. THEMES & SIDEBAR CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #fff5f7 !important; }
    [data-testid="stSidebar"] { background-color: #f1f5f9 !important; border-right: 2px solid #e2e8f0; }
    
    /* Metrics Fix: BLUE & BOLD */
    div[data-testid="stMetricValue"] > div { color: #1e3a8a !important; font-weight: 900 !important; font-size: 38px !important; }
    div[data-testid="stMetricLabel"] p { color: #1e3a8a !important; font-weight: 900 !important; }
    div[data-testid="stMetric"] { background: white !important; border: 2px solid #1e3a8a; border-radius: 15px; padding: 15px; }

    /* Input Borders 360° */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="base-input"], .stDateInput div {
        border: 3px solid #800000 !important; border-radius: 14px !important;
        background-color: #ffffff !important; padding: 2px !important;
    }
    input, select, textarea, div[role="button"] { color: #1e3a8a !important; font-weight: 800 !important; }

    /* Summary Table Style */
    .luxury-table { width: 100%; border-collapse: collapse; border-radius: 15px; overflow: hidden; margin: 20px 0; }
    .luxury-table thead tr { background-color: #f59e0b !important; color: white !important; font-weight: 900; }
    .luxury-table td { padding: 15px; text-align: center; background-color: white; color: #1e3a8a; font-weight: bold; border-bottom: 1px solid #ddd; }

    .biz-banner { background: linear-gradient(135deg, #f97316 0%, #ec4899 100%); padding: 20px; border-radius: 20px; color: white !important; text-align: center; font-size: 30px; font-weight: 900; margin-bottom: 25px; border: 4px solid #ffffff; }
    .stButton button { background: linear-gradient(90deg, #f97316 0%, #1e3a8a 100%) !important; color: white !important; border-radius: 12px !important; font-weight: 900 !important; padding: 10px 40px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONNECTION ---
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"
def get_client():
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']))

client = get_client()

# --- 4. LOGIN SYSTEM (FIXED KEYERROR) ---
if "auth" not in st.session_state:
    st.markdown('<div class="biz-banner">🛡️ EMPIRE ACCESS GATEWAY</div>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 2, 1])
    with col_log:
        sel_l_login = st.selectbox("Language / اللغة", ["FR", "AR"])
        L_log = LANGS[sel_l_login]
        u_in = st.text_input(L_log["ident"])
        p_in = st.text_input(L_log["pass"], type="password")
        if st.button(L_log["btn_log"], use_container_width=True):
            try:
                m_sheet = client.open("Master_Admin").sheet1
                m_df = pd.DataFrame(m_sheet.get_all_records())
                match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
                if not match.empty:
                    user_row = match.iloc[0]
                    if str(user_row['Status']).strip() == 'Active':
                        st.session_state.update({"auth": True, "user": u_in, "lang": sel_l_login, "biz_name": str(user_row['Business_Name']), "sheet_name": str(user_row['Sheet_Name'])})
                        st.rerun()
                    else: st.error("🚫 Access Suspended.")
                else: st.error("❌ Invalid Credentials.")
            except Exception as e: st.error(f"Error Master: {e}")
    st.stop()

# --- 5. DATA ---
L = LANGS[st.session_state["lang"]]
try:
    c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
    df = pd.DataFrame(c_sheet_obj.get_all_records())
except: st.error("Database Error"); st.stop()

if not df.empty:
    df.columns = [c.strip() for c in df.columns]
    mapping = {"Date Debut": "Date Début", "Months": "Durée (Mois)", "Duree": "Durée (Mois)"}
    df.rename(columns=mapping, inplace=True)
    required_cols = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status"]
    for col in required_cols:
        if col not in df.columns: df[col] = 0 if col == 'Prix' else ""
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = pd.to_datetime(df['Date Fin']).dt.strftime('%Y-%m-%d').fillna("N/A")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# SIDEBAR DOWNLOAD & LOGOUT
def to_excel_pro(df):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='EmpireData')
        workbook = writer.book
        worksheet = writer.sheets['EmpireData']
        header_f = workbook.add_format({'bold': True, 'bg_color': '#f97316', 'font_color': 'white', 'border': 1})
        for i, col in enumerate(df.columns):
            worksheet.write(0, i, col, header_f)
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, column_len)
        writer.close()
    return out.getvalue()

with st.sidebar:
    st.markdown('<div style="background: #334155; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px;"><h2 style="color: white; margin:0; font-size:20px;">EMPIRE.</h2></div>', unsafe_allow_html=True)
    menu = st.radio("NAV", [L["nav1"], L["nav2"], L["nav3"], L["nav4"]], label_visibility="collapsed")
    st.markdown("---")
    st.download_button(label=L["export"], data=to_excel_pro(df), file_name=f"{st.session_state['user']}_pro.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    if st.button(L["logout"]): st.session_state.clear(); st.rerun()

# --- 6. BODY ---
st.markdown(f'<div class="biz-banner">👤 {st.session_state["biz_name"]} 🚀</div>', unsafe_allow_html=True)

# NAV 1: ANALYTICS (FIRST)
if menu == L["nav1"]:
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

# NAV 2: GESTION
elif menu == L["nav2"]:
    st.markdown(f"<h2 style='text-align: center; color: #800000;'>{L['add_title']}</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        n_nom = st.text_input("Nom / الإسم")
        n_phone = st.text_input("WhatsApp")
        n_stat = st.selectbox("Status", ["Actif", "Payé", "En Attente", "Annulé"])
    with col2:
        n_email = st.text_input("Email")
        s_choice = st.selectbox("Service", ["Netflix", "IPTV", "Canva", "ChatGPT", "Autre"])
        final_s = st.text_input("Service Name") if s_choice == "Autre" else s_choice
    with col3:
        n_prix = st.number_input("Prix (DH)", min_value=0)
        n_deb = st.date_input("Start Date", today)
        n_dur = st.number_input("Months", min_value=1, value=1)
    if st.button(L["save"], use_container_width=True):
        if n_nom and n_phone:
            n_fin = n_deb + relativedelta(months=int(n_dur))
            new_r = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), n_stat]
            df_core = df.drop(columns=['Days', 'Date_Display'], errors='ignore')
            df_new = pd.concat([df_core, pd.DataFrame([dict(zip(df_core.columns, new_r))])], ignore_index=True)
            c_sheet_obj.clear(); c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
            st.success("✅ Synchro OK!"); st.rerun()
    st.markdown("---")
    st.data_editor(df, use_container_width=True, num_rows="dynamic")

# NAV 3: RAPPELS
elif menu == L["nav3"]:
    st.header(L["nav3"])
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} j")
            msg = (f"Bonjour *{r['Nom']}*,\n\nVotre abonnement *{r['Service']}* arrive à expiration dans *{r['Days']} jours* ⏳\n"
                   f"Date de fin : *{r['Date_Display']}* 📅\n\nMerci pour votre confiance,\n*{st.session_state['biz_name'].upper()}*")
            wa = f"https://wa.me/{clean_num(r['Phone'])}?text={urllib.parse.quote(msg)}"
            cr.link_button("📲 TIRER", wa)
    else: st.success(L["propre"])

# NAV 4: REÇUS
elif menu == L["nav4"]:
    if not df.empty:
        sel = st.selectbox("Client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        rt = f"✅ *REÇU - {st.session_state['biz_name'].upper()}*\n👤 Client: *{c['Nom']}*\n💰 Prix: *{c['Prix']} DH*\n🛠️ Service: *{c['Service']}*\n⌛ Expire: *{c['Date_Display']}*\n🤝 Merci !"
        st.markdown(f'<div class="receipt-card"><pre style="color:white; font-size:18px; font-weight:bold; white-space: pre-wrap;">{rt}</pre></div>', unsafe_allow_html=True)
        st.link_button("📲 SEND", f"https://wa.me/{clean_num(c['Phone'])}?text={urllib.parse.quote(rt)}")
