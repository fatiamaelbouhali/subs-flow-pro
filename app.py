import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V63 - DIAMOND COMMANDER EDITION
st.set_page_config(page_title="EMPIRE_PRO_V63", layout="wide", page_icon="👤")

# ⚡ THE SUPREME LUXURY CSS (BORDO, ROSE, MUSTARD, BLUE)
st.markdown("""
    <style>
    .stApp { background-color: #fff8f9 !important; }
    
    /* 1. INPUT CASES - BORDO & ROSE CONTOURS */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        border: 2px solid #800000 !important; /* Bordo */
        border-radius: 12px !important;
        background-color: #ffffff !important;
        color: #1e3a8a !important; /* Royal Blue Text */
        font-weight: 700 !important;
        box-shadow: 3px 3px 0px #ec4899 !important; /* Rose Barad Shadow */
    }

    /* 2. BUSINESS BANNER - LUXURY GRADIENT WITH HUMAN ICON */
    .biz-banner {
        background: linear-gradient(135deg, #f59e0b 0%, #1e3a8a 100%); /* Mustard to Blue */
        padding: 25px; border-radius: 20px; color: white !important;
        text-align: center; font-size: 35px; font-weight: 900;
        margin-bottom: 30px; border: 3px solid #ffffff;
        box-shadow: 0 10px 30px rgba(30, 58, 138, 0.3);
    }

    /* 3. METRICS - CLEAN & BOLD */
    div[data-testid="stMetric"] {
        background: white !important;
        border: 2px solid #ec4899 !important; /* Rose Barad */
        border-radius: 18px !important;
        padding: 15px !important;
    }
    div[data-testid="stMetricValue"] > div { color: #800000 !important; font-size: 32px !important; font-weight: 900; }
    div[data-testid="stMetricLabel"] p { color: #1e3a8a !important; font-weight: 800; text-transform: uppercase; }

    /* 4. BUTTONS - MUSTARD & BLUE GRADIENT */
    .stButton button {
        background: linear-gradient(90deg, #f59e0b 0%, #1e3a8a 100%) !important;
        color: white !important; border-radius: 12px !important; border: 2px solid #ffffff !important;
        font-weight: 900 !important; padding: 12px 35px !important;
        text-transform: uppercase; letter-spacing: 1px;
    }

    /* 5. TABS & EDITOR */
    .stTabs [data-baseweb="tab"] { font-weight: 900 !important; font-size: 18px !important; color: #800000 !important; }
    .stTabs [aria-selected="true"] { background-color: #ec4899 !important; color: white !important; border-radius: 10px 10px 0 0; }
    [data-testid="stDataFrame"] td { text-align: center !important; font-weight: 700 !important; color: #1e3a8a !important; }

    /* 6. REÇU BOX STYLE */
    .stCode {
        background-color: #fff9eb !important; /* Soft Mustard */
        border: 2px solid #1e3a8a !important;
        border-radius: 15px !important;
        color: #800000 !important;
        font-weight: bold !important;
    }
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
                if match.iloc[0]['Status'] == 'Active':
                    st.session_state.update({"auth": True, "user": u_in, "biz_name": str(match.iloc[0]['Business_Name']), "sheet_name": str(match.iloc[0]['Sheet_Name'])})
                    st.rerun()
        except Exception as e: st.error(f"Error Master: {e}")
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

# --- 3. SIDEBAR (ALWAYS OPEN FORM) ---
with st.sidebar:
    st.markdown(f"👤 Admin: **{st.session_state['user'].upper()}**")
    if st.button("Déconnexion"):
        st.session_state.clear()
        st.rerun()
    st.markdown("---")
    st.header("➕ Nouveau Client")
    n_nom = st.text_input("Nom Complet")
    n_phone = st.text_input("WhatsApp (ex: 212...)")
    n_email = st.text_input("Email")
    s_choice = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
    final_s = st.text_input("Nom Service Spécifique") if s_choice == "Autre" else s_choice
    n_prix = st.number_input("Prix (DH)", min_value=0)
    n_deb = st.date_input("Date de Début", today)
    n_dur = st.number_input("Durée (Mois)", min_value=1, value=1)
    
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
st.markdown(f'<div class="biz-banner">👤 {st.session_state["biz_name"]} 🚀</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS PRO", "👥 BASE DE DONNÉES", "🔔 RAPPELS WHATSAPP", "📄 GÉNÉRATEUR REÇUS"])

with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("ALERTES (3j)", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
        
        st.markdown("### 📋 Résumé Exécutif par Service")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'Total (DH)']
        st.write(summary.to_html(classes='luxury-table', index=False, border=0), unsafe_allow_html=True)
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="simple_white"), use_container_width=True)

with t2:
    st.markdown("### 🛠️ Gestion Centralisée")
    if not df.empty:
        cols_edit = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Days"]
        edited = st.data_editor(df[cols_edit], use_container_width=True, num_rows="dynamic", disabled=["Days", "Date Fin"])
        if st.button("💾 Sauvegarder les modifications"):
            final_df = edited.drop(columns=['Days'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Base Cloud Synchronisée!")
            st.rerun()

with t3:
    st.subheader("🔔 Alertes de Relance")
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')] if not df.empty else pd.DataFrame()
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 **{r['Nom']}** | ⏳ **{r['Days']} j** (Fin: {r['Date Fin']})")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire le {r['Date_Display']}. On renouvelle?"
            cr.link_button("📲 Rappeler", f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}")
    else: st.info("🛡️ Tout est propre. Aucun retard aujourd'hui !")

with t4:
    if not df.empty:
        sel = st.selectbox("Sélectionner Client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = (f"✅ *REÇU DE PAIEMENT - {st.session_state['biz_name']}*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👤 Client: *{c['Nom']}*\n"
                f"📺 Service: *{c['Service']}*\n"
                f"💰 Prix: *{c['Prix']} DH*\n"
                f"⌛ Expire le: *{c['Date_Display']}*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🤝 *Merci pour votre confiance !*")
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")
