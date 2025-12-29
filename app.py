import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V51 - VIBRANT EMPIRE (LIFE & ENERGY UI)
st.set_page_config(page_title="EMPIRE_PRO_V51", layout="wide", page_icon="⚡")

# ⚡ CSS DIAL "L-7AYAT" - COLORS THAT MAKE YOU WANT TO WORK
st.markdown("""
    <style>
    /* Background n9i o mri7 */
    .stApp { background-color: #f8fafc; }

    /* Business Banner Vibrant Gradient */
    .biz-banner {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        padding: 35px;
        border-radius: 20px;
        color: white !important;
        text-align: center;
        font-size: 45px;
        font-weight: 900;
        margin-bottom: 30px;
        box-shadow: 0 15px 35px rgba(99, 102, 241, 0.3);
        border: none;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
    }

    /* Metrics Cards - Glassmorphism Style */
    div[data-testid="stMetric"] {
        background: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
        transition: 0.4s ease;
    }
    div[data-testid="stMetric"]:hover { transform: scale(1.05); box-shadow: 0 15px 40px rgba(0,0,0,0.1) !important; }
    
    /* Vibrant Colors for Numbers */
    div[data-testid="stMetricValue"] > div { color: #4f46e5 !important; font-size: 40px !important; font-weight: 800 !important; }
    
    /* Professional Labels */
    div[data-testid="stMetricLabel"] p { color: #64748b !important; font-size: 16px !important; font-weight: 700 !important; text-transform: uppercase; }

    /* Tabs Styling - Modern Look */
    .stTabs [data-baseweb="tab-list"] { gap: 12px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background-color: #ffffff !important;
        color: #475569 !important;
        border-radius: 12px !important;
        padding: 10px 30px !important;
        font-weight: 600 !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
    }
    .stTabs [aria-selected="true"] { 
        background: #6366f1 !important; 
        color: white !important; 
        border: none !important;
        box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3) !important;
    }

    /* Buttons Pro */
    .stButton button {
        background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 25px !important;
        font-weight: bold !important;
    }
    
    /* Input Visibility Fix */
    label p { color: #1e293b !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=scope))

client = get_gspread_client()

# --- 1. LOGIN ---
if "auth" not in st.session_state:
    st.markdown('<div class="biz-banner">🚀 ENTERPRISE PORTAL</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        u_in = st.text_input("Identifiant Business:")
        p_in = st.text_input("Mot de passe:", type="password")
        if st.button("S'authentifier"):
            try:
                m_sheet = client.open("Master_Admin").sheet1
                m_df = pd.DataFrame(m_sheet.get_all_records())
                match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & 
                             (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
                if not match.empty:
                    if match.iloc[0]['Status'] == 'Active':
                        st.session_state["auth"] = True
                        st.session_state["user"] = u_in
                        st.session_state["biz_name"] = str(match.iloc[0]['Business_Name']).strip()
                        st.session_state["sheet_name"] = str(match.iloc[0]['Sheet_Name']).strip()
                        st.rerun()
                else: st.error("❌ Identifiants Incorrects.")
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

# --- 3. UI ---
st.markdown(f'<div class="biz-banner">⚡ {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS PRO", "👥 GESTION", "🔔 RAPPELS", "📄 REÇUS"])

with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("✅ CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("🚨 ALERTES URGENTES", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
        
        st.markdown("### 📈 Chiffre d'Affaires par Service")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Nb Clients', 'Revenue (DH)']
        st.dataframe(summary, use_container_width=True)
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', barmode='group', template="simple_white"), use_container_width=True)

with t2:
    with st.expander("➕ NOUVEAU CLIENT"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom Complet")
        n_phone = ca.text_input("WhatsApp")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Préciser Service") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix", min_value=0)
        n_deb = cc.date_input("Date de Début", today)
        n_dur = cc.number_input("Durée (Mois)", min_value=1, value=1)
        if st.button("🚀 Valider l'Abonnement"):
            if n_nom and n_phone:
                n_fin = n_deb + relativedelta(months=int(n_dur))
                c_sheet_obj.append_row([n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"])
                st.success("✅ Synchro réussie !")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Days"]
        edited = st.data_editor(df[cols], use_container_width=True, num_rows="dynamic", disabled=["Days", "Date Fin"])
        if st.button("💾 Sauvegarder modifications"):
            final_df = edited.drop(columns=['Days'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Cloud Sync OK!")
            st.rerun()

with t3:
    st.subheader("Relances WhatsApp 📲")
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            col_l, col_r = st.columns([3, 1])
            icon = "🔴" if r['Days'] <= 0 else "🟠"
            col_l.info(f"{icon} **{r['Nom']}** | {r['Service']} | **{r['Days']} jours**")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire le {r['Date_Display']}. On renouvelle?"
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
            col_r.link_button("📲 Envoyer", wa)
    else: st.success("Tout est propre.")

with t4:
    if not df.empty:
        sel = st.selectbox("Choisir client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = (f"✅ *REÇU - {st.session_state['biz_name']}*\n"
                f"👤 Client: *{c['Nom']}*\n"
                f"📺 Service: *{c['Service']}*\n"
                f"💰 Prix: *{c['Prix']} DH*\n"
                f"⌛ Expire: *{c['Date_Display']}*\n"
                f"*Merci de votre confiance !*")
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

st.sidebar.button("Déconnexion", on_click=lambda: st.session_state.clear())
