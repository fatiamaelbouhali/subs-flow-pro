import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px
import io

# SYSTEM STATUS: OMEGA V79 - SIDEBAR NAVIGATION & BODY FORM
st.set_page_config(page_title="EMPIRE_PRO_V79", layout="wide", page_icon="🛡️")

# --- 1. LANGUAGE DICTIONARY ---
LANGS = {
    "FR": {
        "nav1": "📊 ANALYTICS", "nav2": "👥 GESTION DES CLIENTS", "nav3": "🔔 RAPPELS WHATSAPP", "nav4": "📄 GÉNÉRATEUR REÇUS",
        "rev": "REVENUE TOTAL", "act": "CLIENTS ACTIFS", "alrt": "ALERTES (3j)", "add_title": "➕ AJOUTER UN NOUVEAU CLIENT",
        "save": "🚀 Enregistrer au Cloud", "export": "📥 Télécharger Excel", "msg": "Bonjour, votre abonnement expire bientôt.",
        "sum_title": "📋 Résumé Business par Service", "logout": "Déconnexion", "propre": "Tout est propre."
    },
    "AR": {
        "nav1": "📊 الإحصائيات", "nav2": "👥 إدارة الزبناء", "nav3": "🔔 تنبيهات الواتساب", "nav4": "📄 وصل الأداء",
        "rev": "إجمالي الأرباح", "act": "المشتركون", "alrt": "تنبيهات (3 أيام)", "add_title": "➕ إضافة زبون جديد",
        "save": "🚀 حفظ في السحابة", "export": "📥 تحميل إكسيل", "msg": "السلام عليكم، اشتراككم سينتهي قريبا.",
        "sum_title": "📋 ملخص الأرباح حسب الخدمة", "logout": "خروج", "propre": "كل شيء منظم."
    }
}

# --- 2. SIDEBAR CONFIG (NAV + SETTINGS) ---
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    sel_lang = st.selectbox("🌍 Language", ["FR", "AR"])
    L = LANGS[sel_lang]
    
    sel_theme = st.selectbox("🎨 Theme Mode", ["Vibrant Empire", "Soft Emerald", "Luxury Dark", "Midnight Blue"])
    
    st.markdown("---")
    st.markdown("### 🚀 Navigation")
    menu = st.radio("Aller à:", [L["nav1"], L["nav2"], L["nav3"], L["nav4"]])
    
    if sel_theme == "Vibrant Empire":
        bg, card_bg, border_c, txt_m = "#fff5f7", "#ffffff", "#ec4899", "#db2777"
    elif sel_theme == "Soft Emerald":
        bg, card_bg, border_c, txt_m = "#f0fdf4", "#ffffff", "#10b981", "#047857"
    elif sel_theme == "Luxury Dark":
        bg, card_bg, border_c, txt_m = "#0e1117", "#1f2937", "#3b82f6", "#00d2ff"
    else: # Midnight
        bg, card_bg, border_c, txt_m = "#010b1a", "#101e33", "#00d2ff", "#38bdf8"

# ⚡ DYNAMIC CSS
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; }}
    div[data-testid="stMetric"] {{ background: {card_bg} !important; border: 2px solid #f59e0b; border-radius: 15px; padding: 15px; }}
    div[data-testid="stMetricValue"] > div {{ color: {txt_m} !important; font-weight: 900 !important; }}
    .biz-banner {{ background: linear-gradient(135deg, #f59e0b 0%, {border_c} 100%); padding: 20px; border-radius: 15px; color: white !important; text-align: center; font-size: 30px; font-weight: 900; margin-bottom: 25px; border: 3px solid #ffffff; }}
    
    /* 360° BORDERS - BORDO LUXURY (FOR ALL INPUTS) */
    .stTextInput input, .stNumberInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"], .stDateInput input {{
        border: 3px solid #800000 !important; border-radius: 12px !important; background-color: #ffffff !important;
        color: #1e3a8a !important; font-weight: 800 !important; height: 45px !important;
    }}
    label p {{ color: #800000 !important; font-weight: 900 !important; }}
    
    .luxury-table {{ width: 100%; border-collapse: collapse; border-radius: 15px; overflow: hidden; margin: 20px 0; }}
    .luxury-table thead tr {{ background-color: #f59e0b !important; color: white !important; font-weight: 900; }}
    .luxury-table td {{ padding: 12px; text-align: center; background-color: white; color: #1e3a8a; font-weight: bold; border-bottom: 1px solid #ddd; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. GOOGLE CONNECTION ---
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"
def get_gspread_client():
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']))

client = get_gspread_client()

# --- 4. LOGIN ---
if "auth" not in st.session_state:
    st.markdown(f'<div class="biz-banner">🛡️ EMPIRE ACCESS - {sel_lang}</div>', unsafe_allow_html=True)
    u_in = st.text_input("Username:")
    p_in = st.text_input("Password:", type="password")
    if st.button("Se Connecter"):
        m_sheet = client.open("Master_Admin").sheet1
        m_df = pd.DataFrame(m_sheet.get_all_records())
        match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
        if not match.empty:
            user_row = match.iloc[0]
            if str(user_row['Status']).strip() == 'Active':
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
def to_excel_dynamic(df):
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
    st.download_button(L["export"], to_excel_dynamic(df), f"{st.session_state['user']}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    if st.button(L["logout"]): st.session_state.clear(); st.rerun()

# --- 6. MAIN INTERFACE (SIDEBAR NAV LOGIC) ---
st.markdown(f'<div class="biz-banner">🛡️ {st.session_state["biz_name"]} 🚀</div>', unsafe_allow_html=True)

# 📊 ANALYTICS PAGE
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

# 👥 GESTION PAGE (FORM + EDITOR)
elif menu == L["nav2"]:
    st.header(L["add_title"])
    # 💡 FORMULAIRE MA7LOUL DIMA (BODY)
    c_a, c_b, c_c = st.columns(3)
    with c_a:
        n_nom = st.text_input("Nom / الإسم")
        n_phone = st.text_input("WhatsApp")
    with c_b:
        n_email = st.text_input("Email")
        s_choice = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = st.text_input("Détails Service") if s_choice == "Autre" else s_choice
    with c_c:
        n_prix = st.number_input("Prix", min_value=0)
        n_deb = st.date_input("Date Début", today)
        n_dur = st.number_input("Mois", min_value=1, value=1)

    if st.button(L["save"]):
        if n_nom and n_phone:
            n_fin = n_deb + relativedelta(months=int(n_dur))
            new_r = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"]
            df_clean = df.drop(columns=['Days', 'Date_Display'], errors='ignore') if not df.empty else pd.DataFrame(columns=["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status"])
            df_new = pd.concat([df_clean, pd.DataFrame([dict(zip(df_clean.columns, new_r))])], ignore_index=True)
            c_sheet_obj.clear(); c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
            st.success("✅ Synchronisé !"); st.rerun()

    st.markdown("---")
    st.subheader("📋 Liste & Édition Rapide")
    if not df.empty:
        cols_edit = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Days"]
        edited = st.data_editor(df[cols_edit], use_container_width=True, num_rows="dynamic", disabled=["Days", "Date Fin"])
        if st.button("💾 Sauvegarder les modifications"):
            final_df = edited.drop(columns=['Days', 'Date_Display'], errors='ignore')
            c_sheet_obj.clear(); c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Database Cloud Updated!"); st.rerun()

# 🔔 RAPPELS PAGE
elif menu == L["nav3"]:
    st.header(L["tab3"])
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} jours (Fin: {r['Date_Display']})")
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(L['msg'])}"
            cr.link_button("📲 Rappeler", wa)
            st.markdown("---")
    else: st.success(L["propre"])

# 📄 REÇUS PAGE
elif menu == L["nav4"]:
    st.header(L["tab4"])
    if not df.empty:
        sel = st.selectbox("Choisir client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = (f"✅ *REÇU DE PAIEMENT - {st.session_state['biz_name']}*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👤 Client: *{c['Nom']}*\n"
                f"📺 Service: *{c['Service']}*\n"
                f"💰 Prix: *{c['Prix']} DH*\n"
                f"⌛ Expire le: *{c['Date_Display']}*\n"
                f"━━━━━━━━━━━━━━━━━━")
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")
