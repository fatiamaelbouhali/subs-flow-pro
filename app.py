import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px
import io

# SYSTEM STATUS: OMEGA V74 - MULTI-LANG & THEME CUSTOMIZER
st.set_page_config(page_title="EMPIRE_V74_PRO", layout="wide", page_icon="🛡️")

# --- 1. LANGUAGE DICTIONARY ---
LANGS = {
    "FR": {
        "ident": "Identifiant Business:", "pass": "Mot de passe:", "btn_log": "Se Connecter",
        "tab1": "📊 ANALYTICS", "tab2": "👥 GESTION", "tab3": "🔔 RAPPELS", "tab4": "📄 REÇUS",
        "rev": "REVENUE TOTAL", "act": "ACTIFS", "alrt": "ALERTES", "add": "AJOUTER UN CLIENT",
        "save": "Enregistrer au Cloud", "export": "📥 Exporter Excel", "msg": "Bonjour, votre abonnement expire bientôt."
    },
    "AR": {
        "ident": "اسم المستخدم:", "pass": "كلمة السر:", "btn_log": "تسجيل الدخول",
        "tab1": "📊 الإحصائيات", "tab2": "👥 إدارة الزبناء", "tab3": "🔔 التنبيهات", "tab4": "📄 الوصولات",
        "rev": "إجمالي الأرباح", "act": "المشتركون", "alrt": "تنبيهات", "add": "إضافة زبون جديد",
        "save": "حفظ في السحابة", "export": "📥 تحميل إكسيل", "msg": "السلام عليكم، اشتراككم سينتهي قريبا."
    }
}

# --- 2. SIDEBAR SETTINGS (Language & Theme) ---
with st.sidebar:
    st.header("⚙️ Settings")
    sel_lang = st.selectbox("🌍 Language / اللغة", ["FR", "AR"])
    L = LANGS[sel_lang]
    
    sel_theme = st.select_slider("🎨 Theme Mode", options=["Luxury Dark", "Vibrant Light"])
    
    if sel_theme == "Luxury Dark":
        bg_col, txt_col, card_bg = "#0e1117", "#ffffff", "rgba(30, 41, 59, 0.7)"
    else:
        bg_col, txt_col, card_bg = "#fff5f7", "#1e3a8a", "#ffffff"

# ⚡ DYNAMIC CSS
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_col} !important; }}
    div[data-testid="stMetric"] {{ background: {card_bg} !important; border: 2px solid #6366f1; border-radius: 15px; padding: 20px; }}
    .biz-banner {{ background: linear-gradient(135deg, #f59e0b 0%, #ec4899 100%); padding: 20px; border-radius: 20px; color: white !important; text-align: center; font-size: 32px; font-weight: 900; margin-bottom: 25px; border: 3px solid #ffffff; }}
    
    /* 360° BORDER FIX FOR ALL INPUTS */
    .stTextInput input, .stNumberInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"], .stDateInput input {{
        border: 3px solid #800000 !important; border-radius: 14px !important; background-color: #ffffff !important;
        color: #1e3a8a !important; font-weight: 800 !important; height: 48px !important; padding: 5px 12px !important;
    }}
    label[data-testid="stWidgetLabel"] p {{ color: #800000 !important; font-weight: 900 !important; }}
    </style>
    """, unsafe_allow_html=True)

# MASTER ADMIN ID
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']))

client = get_gspread_client()

# --- 3. LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.markdown(f'<div class="biz-banner">🛡️ EMPIRE ACCESS - {sel_lang}</div>', unsafe_allow_html=True)
    u_in = st.text_input(L["ident"])
    p_in = st.text_input(L["pass"], type="password")
    if st.button(L["btn_log"]):
        try:
            m_sheet = client.open("Master_Admin").sheet1
            m_df = pd.DataFrame(m_sheet.get_all_records())
            match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
            if not match.empty:
                user_row = match.iloc[0]
                if str(user_row['Status']).strip() == 'Active':
                    st.session_state.update({"auth": True, "user": u_in, "biz_name": str(user_row['Business_Name']), "sheet_name": str(user_row['Sheet_Name'])})
                    st.rerun()
                else: st.error("🚫 Access Blocked.")
            else: st.error("❌ Invalid Login.")
        except Exception as e: st.error(f"Error: {e}")
    st.stop()

# --- 4. DATA OPS ---
try:
    c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
    df = pd.DataFrame(c_sheet_obj.get_all_records())
except: st.error("Base introuvable."); st.stop()

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
st.markdown(f'<div class="biz-banner">👤 {st.session_state["biz_name"]} 🚀</div>', unsafe_allow_html=True)
t1, t2, t3, t4 = st.tabs([L["tab1"], L["tab2"], L["tab3"], L["tab4"]])

# EXCEL EXPORT LOGIC
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

# TAB 1: ANALYTICS
with t1:
    c1, c2, c3 = st.columns(3)
    c1.metric(L["rev"], f"{df['Prix'].sum()} DH")
    c2.metric(L["act"], len(df[df['Status'] == 'Actif']))
    c3.metric(L["alrt"], len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
    st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="plotly_dark"), use_container_width=True)
    
    # 📥 EXCEL DOWNLOAD BUTTON
    st.sidebar.markdown("---")
    st.sidebar.download_button(label=L["export"], data=to_excel(df), file_name=f"{st.session_state['user']}_data.xlsx", mime="application/vnd.ms-excel")

# TAB 2: GESTION
with t2:
    with st.expander(L["add"]):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom / الإسم")
        n_phone = ca.text_input("WhatsApp")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Service Name") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix", min_value=0)
        n_deb = cc.date_input("Start Date", today)
        n_dur = cc.number_input("Months", min_value=1, value=1)
        if st.button(L["save"]):
            n_fin = n_deb + relativedelta(months=int(n_dur))
            new_r = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"]
            df_new = pd.concat([df.drop(columns=['Days', 'Date_Display'], errors='ignore'), pd.DataFrame([dict(zip(df.columns, new_r))])], ignore_index=True)
            c_sheet_obj.clear(); c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
            st.success("✅ Synced!"); st.rerun()

    st.markdown("---")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Save Changes"):
        final_df = edited.drop(columns=['Days', 'Date_Display'], errors='ignore')
        c_sheet_obj.clear(); c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
        st.success("✅ Updated!"); st.rerun()

# TAB 3: ALERTS
with t3:
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            col_l, col_r = st.columns([3, 1])
            col_l.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} j")
            wa_url = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(L['msg'])}"
            col_r.link_button("📲 WhatsApp", wa_url)

# TAB 4: REÇUS
with t4:
    if not df.empty:
        sel = st.selectbox("Client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"✅ *REÇU - {st.session_state['biz_name']}*\n👤 Client: *{c['Nom']}*\n📺 Service: *{c['Service']}*\n💰 Prix: *{c['Prix']} DH*\n⌛ Expire: *{c['Date_Display']}*\n🤝 *Merci !*"
        st.code(reçu)
        st.link_button("📲 WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")
