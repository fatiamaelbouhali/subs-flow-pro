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

# SYSTEM STATUS: OMEGA V100 - THE FINAL STRIKE (WHATSAPP FIX & LOGO REBORN)
st.set_page_config(page_title="EMPIRE_PRO_V100", layout="wide", page_icon="🛡️")

# 💡 FUNCTION BACH T-NE99I L-NEMRA (FIX WHATSAPP ERROR)
def clean_phone(phone_str):
    num = re.sub(r'\D', '', str(phone_str)) # 7yed ga3 l-7ourouf o l-khwa
    if num.startswith('0'):
        num = '212' + num[1:] # Force Morocco Code
    if not num.startswith('212') and len(num) == 9:
        num = '212' + num
    return num

# --- 1. LANGUAGE DICTIONARY ---
LANGS = {
    "FR": {
        "ident": "Business Identity", "pass": "Access Key", "btn_log": "AUTHORIZE ACCESS",
        "nav1": "👥 GESTION", "nav2": "📊 ANALYTICS", "nav3": "🔔 RAPPELS", "nav4": "📄 REÇUS",
        "rev": "REVENUE TOTAL", "act": "ACTIFS", "alrt": "ALERTES", "add_title": "➕ AJOUTER UN NOUVEAU CLIENT",
        "save": "🚀 EXECUTE ENROLLMENT", "export": "📥 DOWNLOAD DATA", "msg": "Bonjour, votre abonnement expire bientôt.",
        "sum_title": "📋 RÉSUMÉ PAR SERVICE", "logout": "Déconnexion"
    },
    "AR": {
        "ident": "هوية العمل:", "pass": "مفتاح الدخول:", "btn_log": "تفعيل الدخول",
        "nav1": "👥 إدارة الزبناء", "nav2": "📊 الإحصائيات", "nav3": "🔔 التنبيهات", "nav4": "📄 الوصولات",
        "rev": "إجمالي الأرباح", "act": "المشتركون", "alrt": "تنبيهات", "add_title": "➕ إضافة زبون جديد",
        "save": "🚀 حفظ في السحابة", "export": "📥 تحميل البيانات", "msg": "السلام عليكم، اشتراككم سينتهي قريبا.",
        "sum_title": "📋 ملخص الخدمات", "logout": "خروج"
    }
}

# --- 2. THEMES & SIDEBAR CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #fff5f7 !important; }
    [data-testid="stSidebar"] { background-color: #f1f5f9 !important; border-right: 2px solid #e2e8f0; }
    
    /* 💡 LOGO EMPIRE BOX - ORANGE PRO (Mustard) */
    .sidebar-logo {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
        padding: 25px; border-radius: 15px; 
        text-align: center; margin-bottom: 25px;
        color: white !important; font-size: 24px; font-weight: 900;
        box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
    }

    div[role="radiogroup"] label {
        background-color: white !important; border-radius: 12px !important; 
        padding: 12px 20px !important; transition: 0.3s !important; 
        border: 1px solid #e2e8f0 !important; margin-bottom: 8px !important;
    }
    div[role="radiogroup"] label[data-checked="true"] { 
        background: #14b8a6 !important; border: none !important; 
        box-shadow: 0 4px 15px rgba(20, 184, 166, 0.4) !important; 
    }
    div[role="radiogroup"] label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] + div div div { display: none !important; }

    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="base-input"], .stDateInput div {
        border: 3px solid #800000 !important; border-radius: 14px !important;
        background-color: #ffffff !important; padding: 2px !important;
    }
    input, select, textarea, div[role="button"] { color: #1e3a8a !important; font-weight: 800 !important; }

    .luxury-table { width: 100%; border-collapse: collapse; border-radius: 15px; overflow: hidden; margin: 20px 0; }
    .luxury-table thead tr { background-color: #f97316 !important; color: white !important; font-weight: 900; }
    .luxury-table td { padding: 15px; text-align: center; background-color: white; color: #1e3a8a; font-weight: bold; border-bottom: 1px solid #ddd; }

    .receipt-card {
        background-color: #1e3a8a !important; padding: 30px !important;
        border-radius: 2.5rem !important; color: #ffffff !important;
        font-family: 'Courier New', monospace; border: 2px solid rgba(255,255,255,0.1);
    }
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
    st.markdown('<div style="background: linear-gradient(135deg, #f97316 0%, #1e3a8a 100%); padding: 30px; border-radius: 20px; color: white; text-align: center; font-size: 30px; font-weight: 900; margin-bottom: 25px;">🛡️ EMPIRE GATEWAY</div>', unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 2, 1])
    with col_log:
        sel_lang = st.selectbox("Language", ["FR", "AR"])
        L_log = LANGS[sel_lang]
        u_in = st.text_input(L_log["ident"])
        p_in = st.text_input(L_log["pass"], type="password")
        if st.button(L_log["btn_log"], use_container_width=True):
            m_sheet = client.open("Master_Admin").sheet1
            m_df = pd.DataFrame(m_sheet.get_all_records())
            match = m_df[(m_df['User'].astype(str) == str(u_in)) & (m_df['Password'].astype(str) == str(p_in))]
            if not match.empty:
                user_row = match.iloc[0]
                st.session_state.update({"auth": True, "user": u_in, "lang": sel_lang, "biz_name": str(user_row['Business_Name']), "sheet_name": str(user_row['Sheet_Name'])})
                st.rerun()
    st.stop()

# --- 5. DATA ---
L = LANGS[st.session_state["lang"]]
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

# --- 6. SIDEBAR NAV ---
with st.sidebar:
    st.markdown('<div class="sidebar-logo">EMPIRE<span style="color: #2dd4bf;">.</span></div>', unsafe_allow_html=True)
    menu = st.radio("NAV", [L["nav1"], L["nav2"], L["nav3"], L["nav4"]], label_visibility="collapsed")
    st.markdown("---")
    if st.button(L["logout"]): st.session_state.clear(); st.rerun()

# --- 7. BODY ---
st.markdown(f'<div style="background: linear-gradient(135deg, #f97316 0%, #ec4899 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; font-size: 30px; font-weight: 900; margin-bottom: 25px;">👤 {st.session_state["biz_name"]} 🚀</div>', unsafe_allow_html=True)

# PAGE GESTION
if menu == L["nav1"]:
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
            df_clean = df.drop(columns=['Days', 'Date_Display'], errors='ignore')
            df_new = pd.concat([df_clean, pd.DataFrame([dict(zip(df_clean.columns, new_r))])], ignore_index=True)
            c_sheet_obj.clear(); c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
            st.success("✅ PROTOCOL SYNCED!"); st.rerun()
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
            # 💡 FIX: Clean phone number before sending
            cleaned_num = clean_phone(r['Phone'])
            wa = f"https://wa.me/{cleaned_num}?text={urllib.parse.quote(L['msg'])}"
            cr.link_button("📲 TIRER", wa)
    else: st.success("Empire is Safe!")

# PAGE REÇUS
elif menu == L["nav4"]:
    st.header(L["nav4"])
    if not df.empty:
        sel = st.selectbox("Client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        receipt_text = f"✅ *REÇU - {st.session_state['biz_name'].upper()}*\n👤 Client: *{c['Nom']}*\n💰 Prix: *{c['Prix']} DH*\n🛠️ Service: *{c['Service']}*\n⌛ Expire: *{c['Date_Display']}*\n🙏 Merci !"
        st.markdown(f'<div class="receipt-card"><pre style="color:white; font-size:18px; font-weight:bold; white-space: pre-wrap;">{receipt_text}</pre></div>', unsafe_allow_html=True)
        # 💡 FIX: Clean phone number before sending
        cleaned_num = clean_phone(c['Phone'])
        st.link_button("📲 ENVOYER VIA WHATSAPP", f"https://wa.me/{cleaned_num}?text={urllib.parse.quote(receipt_text)}")
