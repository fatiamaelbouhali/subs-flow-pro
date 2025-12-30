import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px
import io

# SYSTEM STATUS: OMEGA V75 - 4 THEMES & ALL FEATURES RESTORED
st.set_page_config(page_title="EMPIRE_PRO_V75", layout="wide", page_icon="🛡️")

# --- 1. LANGUAGE DICTIONARY ---
LANGS = {
    "FR": {
        "ident": "Identifiant Business:", "pass": "Mot de passe:", "btn_log": "Se Connecter",
        "tab1": "📊 ANALYTICS", "tab2": "👥 GESTION", "tab3": "🔔 RAPPELS", "tab4": "📄 REÇUS",
        "rev": "REVENUE TOTAL", "act": "ACTIFS", "alrt": "ALERTES", "add": "AJOUTER UN CLIENT",
        "save": "Enregistrer au Cloud", "export": "📥 Exporter Excel", "msg": "Bonjour, votre abonnement expire bientôt.",
        "sum_title": "📋 Résumé par Service"
    },
    "AR": {
        "ident": "اسم المستخدم:", "pass": "كلمة السر:", "btn_log": "تسجيل الدخول",
        "tab1": "📊 الإحصائيات", "tab2": "👥 إدارة الزبناء", "tab3": "🔔 التنبيهات", "tab4": "📄 الوصولات",
        "rev": "إجمالي الأرباح", "act": "المشتركون", "alrt": "تنبيهات", "add": "إضافة زبون جديد",
        "save": "حفظ في السحابة", "export": "📥 تحميل إكسيل", "msg": "السلام عليكم، اشتراككم سينتهي قريبا.",
        "sum_title": "📋 ملخص الخدمات"
    }
}

# --- 2. 4 PREMIUM THEMES ---
with st.sidebar:
    st.header("⚙️ Config")
    sel_lang = st.selectbox("🌍 Language", ["FR", "AR"])
    L = LANGS[sel_lang]
    
    sel_theme = st.selectbox("🎨 Theme Mode", ["Luxury Dark", "Vibrant Rose", "Midnight Blue", "Soft Emerald"])
    
    if sel_theme == "Luxury Dark":
        bg, txt, metric_bg, border_col = "#0e1117", "#ffffff", "rgba(30, 41, 59, 0.7)", "#00d2ff"
    elif sel_theme == "Vibrant Rose":
        bg, txt, metric_bg, border_col = "#fff5f7", "#1e3a8a", "#ffffff", "#ec4899"
    elif sel_theme == "Midnight Blue":
        bg, txt, metric_bg, border_col = "#010b1a", "#ffffff", "#101e33", "#3b82f6"
    else: # Soft Emerald
        bg, txt, metric_bg, border_col = "#f0fdf4", "#064e3b", "#ffffff", "#10b981"

# ⚡ DYNAMIC CSS
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    div[data-testid="stMetric"] {{ background: {metric_bg} !important; border: 2px solid {border_col}; border-radius: 15px; padding: 15px; }}
    .stMetricValue > div {{ color: {border_col} !important; font-weight: 900 !important; }}
    .biz-banner {{ background: linear-gradient(135deg, #f59e0b 0%, #ec4899 100%); padding: 20px; border-radius: 15px; color: white !important; text-align: center; font-size: 30px; font-weight: 900; margin-bottom: 25px; border: 3px solid #ffffff; }}
    
    /* 360° BORDER FIX */
    .stTextInput input, .stNumberInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"], .stDateInput input {{
        border: 3px solid #800000 !important; border-radius: 12px !important; background-color: #ffffff !important;
        color: #1e3a8a !important; font-weight: 800 !important; height: 45px !important; padding: 5px 12px !important;
    }}
    label[data-testid="stWidgetLabel"] p {{ color: #800000 !important; font-weight: 900 !important; }}
    
    /* Summary Table Styling */
    .summary-table {{ width: 100%; border-collapse: collapse; border-radius: 15px; overflow: hidden; margin: 15px 0; }}
    .summary-table thead {{ background: {border_col}; color: white; font-weight: bold; }}
    .summary-table td {{ padding: 12px; border-bottom: 1px solid #ddd; background: white; color: black; text-align: center; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# MASTER ADMIN ID
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']))

client = get_gspread_client()

# --- 3. LOGIN ---
if "auth" not in st.session_state:
    st.markdown(f'<div class="biz-banner">🛡️ EMPIRE GATEWAY - {sel_lang}</div>', unsafe_allow_html=True)
    u_in = st.text_input(L["ident"])
    p_in = st.text_input(L["pass"], type="password")
    if st.button(L["btn_log"]):
        m_sheet = client.open("Master_Admin").sheet1
        m_df = pd.DataFrame(m_sheet.get_all_records())
        match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
        if not match.empty:
            user_row = match.iloc[0]
            if str(user_row['Status']).strip() == 'Active':
                st.session_state.update({"auth": True, "user": u_in, "biz_name": str(user_row['Business_Name']), "sheet_name": str(user_row['Sheet_Name'])})
                st.rerun()
    st.stop()

# --- 4. DATA LOADING ---
try:
    c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
    df = pd.DataFrame(c_sheet_obj.get_all_records())
except: st.error("Error Sheet"); st.stop()

today = datetime.now().date()
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = pd.to_datetime(df['Date Fin']).dt.strftime('%Y-%m-%d').fillna("N/A")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 5. MAIN UI ---
st.markdown(f'<div class="biz-banner">🚀 {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)
t1, t2, t3, t4 = st.tabs([L["tab1"], L["tab2"], L["tab3"], L["tab4"]])

# TAB 1: ANALYTICS + SUMMARY
with t1:
    c1, c2, c3 = st.columns(3)
    c1.metric(L["rev"], f"{df['Prix'].sum()} DH")
    c2.metric(L["act"], len(df[df['Status'] == 'Actif']))
    c3.metric(L["alrt"], len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
    
    st.markdown(f"### {L['sum_title']}")
    if not df.empty:
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'Total (DH)']
        st.write(summary.to_html(classes='summary-table', index=False, border=0), unsafe_allow_html=True)
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="plotly_dark"), use_container_width=True)

# TAB 2: GESTION
with t2:
    with st.expander(L["add"]):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom")
        n_phone = ca.text_input("WhatsApp")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Préciser") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix", min_value=0)
        n_deb = cc.date_input("Début", today)
        n_dur = cc.number_input("Mois", min_value=1, value=1)
        if st.button(L["save"]):
            n_fin = n_deb + relativedelta(months=int(n_dur))
            new_r = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"]
            df_clean = df.drop(columns=['Days', 'Date_Display'], errors='ignore') if not df.empty else pd.DataFrame(columns=["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status"])
            df_new = pd.concat([df_clean, pd.DataFrame([dict(zip(df_clean.columns, new_r))])], ignore_index=True)
            c_sheet_obj.clear(); c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
            st.success("✅ Synced!"); st.rerun()

    st.markdown("---")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder Changes"):
        final_df = edited.drop(columns=['Days', 'Date_Display'], errors='ignore')
        c_sheet_obj.clear(); c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
        st.success("✅ Cloud Updated!"); st.rerun()

# TAB 3: RELANCES
with t3:
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} j")
            wa_url = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(L['msg'])}"
            cr.link_button("📲 Rappeler", wa_url)

# EXCEL EXPORT
def to_excel_v2(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='EmpireData')
    return output.getvalue()

st.sidebar.markdown("---")
st.sidebar.download_button(label=L["export"], data=to_excel_v2(df), file_name=f"{st.session_state['user']}_backup.xlsx", mime="application/vnd.ms-excel")
