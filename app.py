import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px
import io

# SYSTEM STATUS: OMEGA V94 - THE SUPREME EMPIRE (FIXED VISIBILITY & LOGIC)
st.set_page_config(page_title="EMPIRE_PRO_V94", layout="wide", page_icon="🛡️")

# --- 1. LANGUAGE DICTIONARY ---
LANGS = {
    "FR": {
        "ident": "Identifiant Business:", "pass": "Mot de passe:", "btn_log": "Se Connecter",
        "nav1": "👥 GESTION", "nav2": "📊 ANALYTICS", "nav3": "🔔 RAPPELS", "nav4": "📄 REÇUS",
        "rev": "REVENUE TOTAL", "act": "CLIENTS ACTIFS", "alrt": "ALERTES", "add_title": "➕ AJOUTER UN NOUVEAU CLIENT",
        "save": "🚀 Enregistrer au Cloud", "export": "📥 Télécharger Excel", "msg": "Bonjour, votre abonnement expire bientôt.",
        "sum_title": "📋 Résumé Business par Service", "logout": "Déconnexion", "propre": "Tout est propre."
    },
    "AR": {
        "ident": "اسم المستخدم:", "pass": "كلمة السر:", "btn_log": "تسجيل الدخول",
        "nav1": "👥 إدارة الزبناء", "nav2": "📊 الإحصائيات", "nav3": "🔔 التنبيهات", "nav4": "📄 الوصولات",
        "rev": "إجمالي الأرباح", "act": "المشتركون", "alrt": "تنبيهات", "add_title": "➕ إضافة زبون جديد",
        "save": "🚀 حفظ في السحابة", "export": "📥 تحميل إكسيل", "msg": "السلام عليكم، اشتراككم سينتهي قريبا.",
        "sum_title": "📋 ملخص الخدمات", "logout": "خروج", "propre": "كل شيء منظم."
    }
}

# --- 2. SIDEBAR SETTINGS ---
with st.sidebar:
    st.markdown("### ⚙️ Config")
    sel_lang = st.selectbox("🌍 Language", ["FR", "AR"])
    L = LANGS[sel_lang]
    st.markdown("---")
    st.markdown("### 🚀 Menu")
    menu = st.radio("NAV", [L["nav1"], L["nav2"], L["nav3"], L["nav4"]], label_visibility="collapsed")

# ⚡ THE NUCLEAR CSS - 360° BORDERS & CENTERED ALIGNMENT
st.markdown(f"""
    <style>
    .stApp {{ background-color: #fffaf5 !important; }}
    [data-testid="stSidebar"] {{ background-color: #f1f5f9 !important; border-right: 3px solid #f97316; }}
    
    /* 360° BORDO BORDERS FOR ALL INPUTS (FIXED) */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="base-input"], .stDateInput div {{
        border: 3px solid #800000 !important; 
        border-radius: 14px !important;
        background-color: #ffffff !important;
        padding: 2px !important;
        box-shadow: none !important;
    }}
    
    input, select, textarea, div[role="button"], .stNumberInput input {{
        border: none !important;
        background-color: transparent !important;
        color: #1e3a8a !important; 
        font-weight: 800 !important;
        font-size: 1rem !important;
        height: 42px !important;
    }}

    label p {{ color: #800000 !important; font-weight: 900 !important; font-size: 1rem !important; margin-bottom: 5px !important; }}

    /* Banner & Metrics */
    .biz-banner {{ background: linear-gradient(135deg, #f97316 0%, #4b5563 100%); padding: 20px; border-radius: 20px; color: white !important; text-align: center; font-size: 32px; font-weight: 900; margin-bottom: 25px; border: 4px solid #ffffff; }}
    div[data-testid="stMetric"] {{ background: white !important; border: 2px solid #1e3a8a; border-radius: 15px; padding: 15px; }}
    div[data-testid="stMetricValue"] > div {{ color: #db2777 !important; font-weight: 900 !important; }}

    /* Buttons */
    .stButton button {{
        background: linear-gradient(90deg, #f97316 0%, #4b5563 100%) !important;
        color: white !important; border-radius: 12px !important; font-weight: 900 !important; padding: 10px 40px !important;
    }}
    
    /* Center the Data Editor text */
    [data-testid="stDataFrame"] td {{ text-align: center !important; font-weight: 700 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONNECTION ---
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"
def get_client():
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']))

client = get_client()

# --- 4. LOGIN ---
if "auth" not in st.session_state:
    st.markdown('<div class="biz-banner">🛡️ EMPIRE GATEWAY</div>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 2, 1])
    with col_log:
        u_in = st.text_input(L["ident"])
        p_in = st.text_input(L["pass"], type="password")
        if st.button(L["btn_log"]):
            m_sheet = client.open("Master_Admin").sheet1
            m_df = pd.DataFrame(m_sheet.get_all_records())
            match = m_df[(m_df['User'].astype(str) == str(u_in)) & (m_df['Password'].astype(str) == str(p_in))]
            if not match.empty:
                user_row = match.iloc[0]
                st.session_state.update({"auth": True, "user": u_in, "biz_name": str(user_row['Business_Name']), "sheet_name": str(user_row['Sheet_Name'])})
                st.rerun()
    st.stop()

# --- 5. DATA ---
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

# SIDEBAR FOOTER & EXCEL
def to_excel_pro(df):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='EmpireData')
        workbook = writer.book
        worksheet = writer.sheets['EmpireData']
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, column_len)
        writer.close()
    return out.getvalue()

with st.sidebar:
    st.markdown("---")
    st.download_button(L["export"], to_excel_pro(df), f"{st.session_state['user']}_pro.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    if st.button(L["logout"]): st.session_state.clear(); st.rerun()

# --- 6. BODY ---
st.markdown(f'<div class="biz-banner">👤 {st.session_state["biz_name"]} 🚀</div>', unsafe_allow_html=True)

# PAGE GESTION
if menu == L["nav1"]:
    st.markdown(f"<h2 style='text-align: center; color: #800000;'>{L['add_title']}</h2>", unsafe_allow_html=True)
    # 💡 CENTERED & ALIGNED FORM (4 COLUMNS)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        n_nom = st.text_input("Nom / الإسم")
        n_phone = st.text_input("WhatsApp")
    with col2:
        n_email = st.text_input("Email")
        s_choice = st.selectbox("Service", ["Netflix", "IPTV", "Canva", "ChatGPT", "Autre"])
        final_s = st.text_input("Préciser Service") if s_choice == "Autre" else s_choice
    with col3:
        n_prix = st.number_input("Prix (DH)", min_value=0)
        n_deb = st.date_input("Date de Début", today)
    with col4:
        n_dur = st.number_input("Durée (Mois)", min_value=1, value=1)
        n_stat = st.selectbox("Status", ["Actif", "Payé", "En Attente", "Annulé"])

    if st.button(L["save"], use_container_width=True):
        if n_nom and n_phone:
            n_fin = n_deb + relativedelta(months=int(n_dur))
            new_r = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), n_stat]
            df_clean = df.drop(columns=['Days', 'Date_Display'], errors='ignore')
            df_new = pd.concat([df_clean, pd.DataFrame([dict(zip(df_clean.columns, new_r))])], ignore_index=True)
            c_sheet_obj.clear(); c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
            st.success("✅ Synchro OK!"); st.rerun()
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
    if not df.empty:
        sel = st.selectbox("Target:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"✅ *REÇU - {st.session_state['biz_name']}*\n👤 Client: *{c['Nom']}*\n💰 Prix: *{c['Prix']} DH*\n⌛ Expire: *{c['Date_Display']}*"
        st.code(reçu)
        st.link_button("📲 SEND", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")
