import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px
import io

# SYSTEM STATUS: OMEGA V80 - SUPREME ARCHITECT (ZERO RADIOS, FULL BORDERS)
st.set_page_config(page_title="EMPIRE_PRO_V80", layout="wide", page_icon="🛡️")

# --- 1. LANGUAGE DICTIONARY ---
LANGS = {
    "FR": {
        "nav1": "📊 ANALYTICS", "nav2": "👥 GESTION", "nav3": "🔔 RAPPELS", "nav4": "📄 REÇUS",
        "rev": "REVENUE TOTAL", "act": "ACTIFS", "alrt": "ALERTES", "add_title": "➕ AJOUTER UN NOUVEAU CLIENT",
        "save": "🚀 Enregistrer au Cloud", "export": "📥 Télécharger Excel", "msg": "Bonjour, votre abonnement expire bientôt.",
        "sum_title": "📋 Résumé Business par Service", "logout": "Déconnexion", "propre": "Tout est propre."
    },
    "AR": {
        "nav1": "📊 الإحصائيات", "nav2": "👥 إدارة الزبناء", "nav3": "🔔 التنبيهات", "nav4": "📄 الوصولات",
        "rev": "إجمالي الأرباح", "act": "المشتركون", "alrt": "تنبيهات", "add_title": "➕ إضافة زبون جديد",
        "save": "🚀 حفظ في السحابة", "export": "📥 تحميل إكسيل", "msg": "السلام عليكم، اشتراككم سينتهي قريبا.",
        "sum_title": "📋 ملخص الخدمات", "logout": "خروج", "propre": "كل شيء منظم."
    }
}

# --- 2. THEMES & NAV ---
with st.sidebar:
    st.markdown("### ⚙️ Config")
    sel_lang = st.selectbox("🌍 Language", ["FR", "AR"])
    L = LANGS[sel_lang]
    sel_theme = st.selectbox("🎨 Theme", ["Vibrant Empire", "Soft Emerald", "Luxury Dark"])
    
    st.markdown("---")
    # 💡 NAVIGATION BLA D-DIWARAT (CSS HACK)
    st.markdown("### 🚀 Menu")
    menu = st.radio("Navigation", [L["nav1"], L["nav2"], L["nav3"], L["nav4"]], label_visibility="collapsed")
    
    if sel_theme == "Vibrant Empire":
        bg, card_bg, border_c, txt_m = "#fff5f7", "#ffffff", "#ec4899", "#db2777"
    elif sel_theme == "Soft Emerald":
        bg, card_bg, border_c, txt_m = "#f0fdf4", "#ffffff", "#10b981", "#047857"
    else: # Dark
        bg, card_bg, border_c, txt_m = "#0e1117", "#1f2937", "#3b82f6", "#00d2ff"

# ⚡ THE SUPREME CSS FIX
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    
    /* 1. HIDE RADIO CIRCLES (MAKE IT CLICKABLE LINKS) */
    div[role="radiogroup"] {{ gap: 10px; }}
    div[role="radiogroup"] label {{ 
        background: transparent; border-radius: 10px; padding: 5px 15px; 
        transition: 0.3s; cursor: pointer; border: 1px solid transparent;
    }}
    div[role="radiogroup"] label:hover {{ background: rgba(236, 72, 153, 0.1); border: 1px solid #ec4899; }}
    div[data-testid="stRadioButtonContactLabel"] div[data-testid="stMarkdownContainer"] p {{
        font-size: 18px !important; font-weight: 800 !important; color: #1e3a8a !important;
    }}
    /* Hide the circle itself */
    div[role="radiogroup"] [data-testid="stWidgetLabel"] + div div div {{ display: none !important; }}

    /* 2. 360° BORDER FIX FOR INPUTS */
    .stTextInput input, .stNumberInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"], .stDateInput input {{
        border: 3px solid #800000 !important; border-radius: 12px !important;
        background-color: #ffffff !important; color: #1e3a8a !important;
        font-weight: 800 !important; height: 48px !important; padding: 5px 12px !important;
        box-shadow: none !important;
    }}
    label p {{ color: #800000 !important; font-weight: 900 !important; }}

    /* 3. Banner & Metrics */
    .biz-banner {{ background: linear-gradient(135deg, #f59e0b 0%, #ec4899 100%); padding: 20px; border-radius: 15px; color: white !important; text-align: center; font-size: 32px; font-weight: 900; margin-bottom: 25px; border: 3px solid #ffffff; }}
    div[data-testid="stMetric"] {{ background: {card_bg} !important; border: 2px solid #f59e0b; border-radius: 15px; padding: 15px; }}
    
    /* Luxury Table */
    .luxury-table {{ width: 100%; border-collapse: collapse; border-radius: 15px; overflow: hidden; margin: 20px 0; }}
    .luxury-table thead tr {{ background-color: #f59e0b !important; color: white !important; font-weight: 900; }}
    .luxury-table td {{ padding: 15px; text-align: center; background-color: white; color: #1e3a8a; font-weight: bold; border-bottom: 1px solid #ddd; }}
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
    st.markdown(f'<div class="biz-banner">🛡️ EMPIRE GATEWAY</div>', unsafe_allow_html=True)
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
try:
    c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
    df = pd.DataFrame(c_sheet_obj.get_all_records())
except: st.error("Database Error"); st.stop()

today = datetime.now().date()
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = pd.to_datetime(df['Date Fin']).dt.strftime('%Y-%m-%d').fillna("N/A")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# EXCEL LOGIC
def to_excel_pro(df):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='EmpireData')
        worksheet = writer.sheets['EmpireData']
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, column_len)
        writer.close()
    return out.getvalue()

# SIDEBAR FOOTER
with st.sidebar:
    st.markdown("---")
    st.download_button(L["export"], to_excel_pro(df), f"{st.session_state['user']}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    if st.button(L["logout"]): st.session_state.clear(); st.rerun()

# --- 6. BODY INTERFACE ---
st.markdown(f'<div class="biz-banner">🛡️ {st.session_state["biz_name"]} 🚀</div>', unsafe_allow_html=True)

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

elif menu == L["nav2"]:
    st.header(L["add_title"])
    ca, cb, cc = st.columns(3)
    with ca:
        n_nom = st.text_input("Nom / الإسم")
        n_phone = st.text_input("WhatsApp")
    with cb:
        n_email = st.text_input("Email")
        s_choice = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = st.text_input("Service Name") if s_choice == "Autre" else s_choice
    with cc:
        n_prix = st.number_input("Prix", min_value=0)
        n_deb = st.date_input("Start Date", today)
        n_dur = st.number_input("Months", min_value=1, value=1)
    if st.button(L["save"]):
        if n_nom and n_phone:
            n_fin = n_deb + relativedelta(months=int(n_dur))
            new_r = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"]
            df_clean = df.drop(columns=['Days', 'Date_Display'], errors='ignore') if not df.empty else pd.DataFrame(columns=["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status"])
            df_new = pd.concat([df_clean, pd.DataFrame([dict(zip(df_clean.columns, new_r))])], ignore_index=True)
            c_sheet_obj.clear(); c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
            st.success("✅ Synchronisé !"); st.rerun()
    st.markdown("---")
    st.data_editor(df, use_container_width=True, num_rows="dynamic", disabled=["Days", "Date Fin"])

elif menu == L["nav3"]:
    st.header(L["nav3"])
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} j")
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(L['msg'])}"
            cr.link_button("📲 WhatsApp", wa)
            st.markdown("---")
    else: st.success(L["propre"])

elif menu == L["nav4"]:
    st.header(L["nav4"])
    if not df.empty:
        sel = st.selectbox("Client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"✅ *REÇU - {st.session_state['biz_name']}*\n👤 Client: *{c['Nom']}*\n📺 Service: *{c['Service']}*\n💰 Prix: *{c['Prix']} DH*\n⌛ Expire: *{c['Date_Display']}*\n🤝 *Merci !*"
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")
