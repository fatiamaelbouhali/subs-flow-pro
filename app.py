import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V72 - THE ABSOLUTE PROTOCOL (360° BORDER FIX)
st.set_page_config(page_title="EMPIRE_PRO_V72", layout="wide", page_icon="🛡️")

# ⚡ THE NUCLEAR CSS - FORCING FULL BORDERS & TOTAL VISIBILITY
st.markdown("""
    <style>
    /* 1. Background Luxury */
    .stApp { background-color: #fff5f7 !important; }
    
    /* 2. INPUT CASES - THE ULTIMATE FIX (NO MORE CUTTING) */
    /* On cible le conteneur exact de l'input */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="base-input"] {
        border: 3px solid #800000 !important; /* Bordo Bold */
        border-radius: 12px !important;
        background-color: #ffffff !important;
        padding: 2px !important;
    }
    
    /* On force l'input interne à être transparent pour voir le bord du conteneur */
    input, select, textarea {
        border: none !important;
        box-shadow: none !important;
        color: #1e3a8a !important; /* Royal Blue Text */
        font-weight: 800 !important;
        background-color: transparent !important;
    }

    /* Fix pour Number Input et Date Input */
    div.stNumberInput, div.stTextInput, div.stDateInput, div.stSelectbox {
        margin-bottom: 15px !important;
    }

    /* 3. Business Banner */
    .biz-banner {
        background: linear-gradient(135deg, #f59e0b 0%, #ec4899 100%);
        padding: 25px; border-radius: 20px; color: white !important;
        text-align: center; font-size: 32px; font-weight: 900;
        margin-bottom: 25px; border: 4px solid #ffffff;
        box-shadow: 0 10px 30px rgba(236, 72, 153, 0.3);
    }

    /* 4. Labels Bordo Bold */
    label[data-testid="stWidgetLabel"] p {
        color: #800000 !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        margin-bottom: 8px !important;
    }

    /* 5. Metrics & Tables */
    div[data-testid="stMetric"] { background: white !important; border: 2px solid #1e3a8a !important; border-radius: 18px !important; padding: 20px !important; }
    div[data-testid="stMetricValue"] > div { color: #db2777 !important; font-size: 32px !important; font-weight: 900; }
    
    .luxury-table { width: 100%; border-collapse: collapse; border-radius: 15px; overflow: hidden; margin-top: 20px; }
    .luxury-table thead tr { background-color: #f59e0b !important; color: white !important; font-weight: 900; }
    .luxury-table td { padding: 15px; background-color: #ffffff; color: #1e3a8a; font-weight: 800; border-bottom: 1px solid #f1f5f9; text-align: center; }

    /* Sidebar & Tabs */
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 5px solid #800000; }
    .stTabs [data-baseweb="tab"] { font-weight: 900 !important; font-size: 18px !important; color: #1e3a8a !important; }
    .stTabs [aria-selected="true"] { background-color: #ec4899 !important; color: white !important; border-radius: 10px 10px 0 0; }
    </style>
    """, unsafe_allow_html=True)

MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=scope))

client = get_gspread_client()

# --- 1. LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.markdown('<div class="biz-banner">👤 EMPIRE ACCESS GATEWAY</div>', unsafe_allow_html=True)
    u_in = st.text_input("Username:")
    p_in = st.text_input("Password:", type="password")
    if st.button("Unlock"):
        try:
            m_sheet = client.open("Master_Admin").sheet1
            m_df = pd.DataFrame(m_sheet.get_all_records())
            match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & 
                         (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
            if not match.empty:
                user_row = match.iloc[0]
                if str(user_row['Status']).strip() == 'Active':
                    st.session_state.update({"auth": True, "user": u_in, "biz_name": str(user_row['Business_Name']), "sheet_name": str(user_row['Sheet_Name'])})
                    st.rerun()
                else: st.error("🚫 Accès suspendu.")
            else: st.error("❌ Identifiants incorrects.")
        except Exception as e: st.error(f"Error: {e}")
    st.stop()

# --- 2. LOAD DATA ---
try:
    c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
    df = pd.DataFrame(c_sheet_obj.get_all_records())
except:
    st.error("Base introuvable.")
    st.stop()

today = datetime.now().date()
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.date
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = pd.to_datetime(df['Date Fin']).dt.strftime('%Y-%m-%d').fillna("N/A")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 3. SIDEBAR FORM (360° FIXED) ---
with st.sidebar:
    st.markdown(f"👑 **{st.session_state['user'].upper()}**")
    if st.button("Log out"):
        st.session_state.clear()
        st.rerun()
    st.markdown("---")
    st.header("➕ Nouveau Client")
    n_nom = st.text_input("Nom Complet Client")
    n_phone = st.text_input("WhatsApp (ex: 212...)")
    n_email = st.text_input("Email")
    s_choice = st.selectbox("Service Principal", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
    final_s = st.text_input("Préciser Service") if s_choice == "Autre" else s_choice
    n_prix = st.number_input("Prix (DH)", min_value=0)
    n_deb = st.date_input("Date de Début", today)
    n_dur = st.number_input("Nombre de Mois", min_value=1, value=1)
    
    if st.button("🚀 Enregistrer au Cloud"):
        if n_nom and n_phone:
            n_fin = n_deb + relativedelta(months=int(n_dur))
            new_r = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"]
            df_clean = df.drop(columns=['Days', 'Date_Display'], errors='ignore') if not df.empty else pd.DataFrame(columns=["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status"])
            df_new = pd.concat([df_clean, pd.DataFrame([dict(zip(df_clean.columns, new_r))])], ignore_index=True)
            c_sheet_obj.clear()
            c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
            st.success("✅ Synchro OK!")
            st.rerun()

# --- 4. MAIN BODY ---
st.markdown(f'<div class="biz-banner">🛡️ {st.session_state["biz_name"]} 🚀</div>', unsafe_allow_html=True)
t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS PRO", "👥 BASE DE DONNÉES", "🔔 RAPPELS", "📄 REÇUS"])

with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("ALERTES", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'CA Total (DH)']
        st.write(summary.to_html(classes='luxury-table', index=False, border=0), unsafe_allow_html=True)
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="simple_white"), use_container_width=True)

with t2:
    if not df.empty:
        cols_edit = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Days"]
        edited = st.data_editor(df[cols_edit], use_container_width=True, num_rows="dynamic", disabled=["Days", "Date Fin"])
        if st.button("💾 Sauvegarder modifications"):
            final_df = edited.drop(columns=['Days'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Database Updated!")
            st.rerun()

with t3:
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')] if not df.empty else pd.DataFrame()
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 **{r['Nom']}** | ⏳ **{r['Days']} j**")
            msg = f"Bonjour {r['Nom']}, renouvellement {r['Service']}? Expire le {r['Date_Display']}"
            cr.link_button("📲 Rappeler", f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}")
    else: st.info("🛡️ Tout est parfait.")

with t4:
    if not df.empty:
        sel = st.selectbox("Sélectionner Client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = (f"✅ *REÇU DE PAIEMENT - {st.session_state['biz_name']}*\n━━━━━━━━━━━━━━━━━━\n"
                f"👤 Client: *{c['Nom']}*\n📺 Service: *{c['Service']}*\n💰 Prix: *{c['Prix']} DH*\n⌛ Expire le: *{c['Date_Display']}*\n"
                f"━━━━━━━━━━━━━━━━━━\n🤝 *Merci !*")
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")
