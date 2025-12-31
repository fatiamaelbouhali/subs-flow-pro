import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px
import io

# SYSTEM STATUS: OMEGA V98 - REACT STYLE HYBRID (PERFECT UI)
st.set_page_config(page_title="EMPIRE_PRO_V98", layout="wide", page_icon="🛡️")

# ⚡ THE SUPREME HYBRID CSS (BORDO, ROYAL BLUE, ROSE BARAD, TEAL)
st.markdown("""
    <style>
    /* 1. Background Style */
    .stApp { background-color: #fff5f7 !important; }
    
    /* 2. Sidebar React-Style */
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 3px solid #ec4899; }
    div[role="radiogroup"] label {
        background-color: transparent !important; border-radius: 12px !important; 
        padding: 12px 20px !important; transition: 0.3s !important; border: 1px solid transparent !important;
    }
    div[role="radiogroup"] label:hover { background-color: rgba(45, 212, 191, 0.1) !important; border: 1px solid #2dd4bf !important; }
    div[role="radiogroup"] label[data-checked="true"] { 
        background: #2dd4bf !important; border: none !important; box-shadow: 0 4px 15px rgba(45, 212, 191, 0.4) !important; 
    }
    div[role="radiogroup"] label[data-checked="true"] p { color: #0f172a !important; font-weight: 900 !important; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] + div div div { display: none !important; }

    /* 3. INPUT CASES - 360° BORDO BORDERS (THE REACT LOOK) */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="base-input"], .stDateInput div {
        border: 3px solid #800000 !important; border-radius: 14px !important;
        background-color: #ffffff !important; padding: 2px !important; box-shadow: none !important;
    }
    input, select, textarea, div[role="button"], .stNumberInput input {
        border: none !important; background-color: transparent !important;
        color: #1e3a8a !important; font-weight: 800 !important; font-size: 1rem !important;
    }
    label p { color: #800000 !important; font-weight: 900 !important; font-size: 1rem !important; }

    /* 4. Banner Pro */
    .biz-banner { 
        background: linear-gradient(135deg, #f97316 0%, #1e3a8a 100%); 
        padding: 25px; border-radius: 20px; color: white !important; text-align: center; 
        font-size: 32px; font-weight: 900; margin-bottom: 25px; border: 4px solid #ffffff; 
    }

    /* 5. THE RECEIPT CARD (BLUE BOX FROM YOUR CODE) */
    .receipt-card {
        background-color: #1e3a8a !important;
        padding: 40px !important;
        border-radius: 2.5rem !important;
        color: #ffffff !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.3) !important;
        position: relative;
        overflow: hidden;
        font-family: 'Courier New', Courier, monospace;
        border: 2px solid rgba(255,255,255,0.1);
    }
    .receipt-card::after {
        content: ""; position: absolute; top: 0; right: 0; width: 150px; height: 150px;
        background: #f97316; opacity: 0.1; transform: rotate(45deg) translate(50%, -50%);
    }
    .receipt-text { font-size: 20px !important; font-weight: 900 !important; line-height: 1.6; }

    /* 6. Buttons */
    .stButton button {
        background: linear-gradient(90deg, #f97316 0%, #1e3a8a 100%) !important;
        color: white !important; border-radius: 15px !important; font-weight: 900 !important; padding: 12px 40px !important;
    }
    .send-btn {
        background-color: #22c55e !important; color: white !important;
        width: 100%; padding: 15px; border-radius: 15px; border: none; font-weight: 900;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CONFIG DICTIONARY ---
LANGS = {
    "FR": {
        "ident": "Business Identity", "pass": "Access Key", "btn_log": "AUTHORIZE ACCESS",
        "nav1": "👥 GESTION", "nav2": "📊 ANALYTICS", "nav3": "🔔 RAPPELS", "nav4": "📄 REÇUS",
        "rev": "REVENUE TOTAL", "act": "CLIENTS ACTIFS", "alrt": "ALERTES", "add_title": "➕ AJOUTER UN NOUVEAU CLIENT",
        "save": "🚀 EXECUTE ENROLLMENT", "export": "📥 DOWNLOAD DATA", "msg": "Bonjour, votre abonnement expire bientôt."
    },
    "AR": {
        "ident": "هوية العمل:", "pass": "مفتاح الدخول:", "btn_log": "تفعيل الدخول",
        "nav1": "👥 إدارة الزبناء", "nav2": "📊 الإحصائيات", "nav3": "🔔 التنبيهات", "nav4": "📄 الوصولات",
        "rev": "إجمالي الأرباح", "act": "المشتركون", "alrt": "تنبيهات", "add_title": "➕ إضافة زبون جديد",
        "save": "🚀 حفظ في السحابة", "export": "📥 تحميل البيانات", "msg": "السلام عليكم، اشتراككم سينتهي قريبا."
    }
}

# --- 2. SIDEBAR NAV ---
with st.sidebar:
    st.markdown(f'<h2 style="color: white; font-weight: 900; font-style: italic;">EMPIRE<span style="color: #2dd4bf;">.</span></h2>', unsafe_allow_html=True)
    sel_lang = st.selectbox("Language", ["FR", "AR"], label_visibility="collapsed")
    L = LANGS[sel_lang]
    st.markdown("---")
    menu = st.radio("NAV", [L["nav1"], L["nav2"], L["nav3"], L["nav4"]], label_visibility="collapsed")

# --- 3. CONNECTION ---
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"
def get_client():
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']))

client = get_client()

# --- 4. LOGIN SYSTEM (IMAGE 1 STYLE) ---
if "auth" not in st.session_state:
    st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh;">
            <div style="background: white; padding: 40px; border-radius: 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.1); width: 450px; text-align: center; border: 1px solid #e2e8f0;">
                <h1 style="color: #0f172a; font-weight: 900; letter-spacing: -2px; font-size: 35px;">EMPIRE <span style="color: #f97316;">GATEWAY</span></h1>
                <p style="color: #64748b; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 30px;">Secured Enterprise SaaS</p>
    """, unsafe_allow_html=True)
    u_in = st.text_input(L["ident"])
    p_in = st.text_input(L["pass"], type="password")
    if st.button(L["btn_log"], use_container_width=True):
        m_sheet = client.open("Master_Admin").sheet1
        m_df = pd.DataFrame(m_sheet.get_all_records())
        match = m_df[(m_df['User'].astype(str) == str(u_in)) & (m_df['Password'].astype(str) == str(p_in))]
        if not match.empty:
            user_row = match.iloc[0]
            st.session_state.update({"auth": True, "user": u_in, "biz_name": str(user_row['Business_Name']), "sheet_name": str(user_row['Sheet_Name'])})
            st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)
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

# --- 6. BODY ---
st.markdown(f'<div class="biz-banner">👤 {st.session_state["biz_name"]} 🚀</div>', unsafe_allow_html=True)

# NAV 1: ANALYTICS
if menu == L["nav2"]:
    c1, c2, c3 = st.columns(3)
    c1.metric(L["rev"], f"{df['Prix'].sum()} DH")
    c2.metric(L["act"], len(df[df['Status'] == 'Actif']))
    c3.metric(L["alrt"], len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
    st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="simple_white"), use_container_width=True)

# NAV 2: GESTION (IMAGE 2 STYLE)
elif menu == L["nav1"]:
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

# NAV 3: RAPPELS
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

# NAV 4: REÇUS (THE EXACT REACT STYLE)
elif menu == L["nav4"]:
    st.markdown(f"<h2 style='color: #800000; font-weight: 900;'>📄 Générateur de Reçus</h2>", unsafe_allow_html=True)
    if not df.empty:
        sel = st.selectbox("Sélectionner le client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        
        # 💡 THE NAVY CARD BOX
        receipt_content = f"""✅ *REÇU - {st.session_state['biz_name'].upper()}*
👤 Client: *{c['Nom']}*
💰 Prix: *{c['Prix']} DH*
🛠️ Service: *{c['Service']}*
⌛ Expire: *{c['Date_Display']}*
🙏 Merci pour votre confiance!"""

        st.markdown(f"""<div class="receipt-card"><pre class="receipt-text">{receipt_content}</pre></div>""", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        # WhatsApp Button
        wa_url = f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(receipt_content)}"
        st.link_button("📲 ENVOYER VIA WHATSAPP", wa_url)

with st.sidebar:
    st.markdown("---")
    if st.button(L["logout"]): st.session_state.clear(); st.rerun()
