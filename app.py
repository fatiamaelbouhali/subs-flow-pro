import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V61 - SUPREME EMPIRE OVERLORD (ULTIMATE UI)
st.set_page_config(page_title="EMPIRE_PRO_V61", layout="wide", page_icon="💎")

# ⚡ THE NUCLEAR CSS - LUXURY, CONTRAST & SOUL
st.markdown("""
    <style>
    /* Background & Main Colors */
    .stApp { background-color: #fff8f9 !important; }
    
    /* 1. Sidebar Form (Always Open & Sharp) */
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 3px solid #db2777; }
    [data-testid="stSidebar"] label p { color: #1e293b !important; font-weight: 900 !important; font-size: 1.1rem !important; }
    
    /* Force Input Borders to be DARKER & Pro */
    input, select, .stSelectbox div, div[data-baseweb="input"], .stNumberInput div { 
        border: 2px solid #1e293b !important; 
        border-radius: 12px !important; 
        color: #000000 !important;
        font-weight: 600 !important;
    }

    /* 2. Banner Pro */
    .biz-banner {
        background: linear-gradient(135deg, #f59e0b 0%, #ec4899 100%);
        padding: 25px; border-radius: 20px; color: white !important;
        text-align: center; font-size: 35px; font-weight: 900;
        margin-bottom: 30px; border: 4px solid #ffffff;
        box-shadow: 0 12px 35px rgba(236, 72, 153, 0.4);
    }

    /* 3. Metrics Pro Cards */
    div[data-testid="stMetric"] {
        background: white !important;
        border: 2px solid #f59e0b !important;
        border-radius: 20px !important;
        padding: 20px !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06) !important;
    }
    div[data-testid="stMetricValue"] > div { color: #db2777 !important; font-size: 35px !important; font-weight: 900; }
    div[data-testid="stMetricLabel"] p { color: #1e3a8a !important; font-size: 16px !important; font-weight: 800; text-transform: uppercase; }

    /* 4. LUXURY SUMMARY TABLE (Mustard, Blue, Pink) */
    .luxury-table {
        width: 100%; border-collapse: collapse; border-radius: 15px; overflow: hidden;
        margin-top: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .luxury-table thead tr { background-color: #f59e0b !important; color: white !important; font-weight: 900; }
    .luxury-table th, .luxury-table td { padding: 18px; text-align: center; font-size: 18px; }
    .luxury-table td { background-color: #ffffff; color: #1e3a8a; font-weight: 800; border-bottom: 1px solid #f1f5f9; }
    .luxury-table tr:nth-child(even) td { background-color: #fff5f7; color: #db2777; }

    /* 5. Alert Pro Gradient */
    .pro-alert-clean {
        background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%) !important;
        color: white !important; padding: 20px; border-radius: 15px;
        text-align: center; font-weight: 900; font-size: 20px;
        border-left: 10px solid #1e3a8a !important;
        box-shadow: 0 5px 15px rgba(245, 158, 11, 0.3);
    }

    /* 6. Tabs & Buttons */
    .stTabs [data-baseweb="tab"] { font-weight: 900 !important; font-size: 19px !important; color: #1e3a8a !important; }
    .stTabs [aria-selected="true"] { background-color: #ec4899 !important; color: white !important; border-radius: 12px 12px 0 0; }
    
    .stButton button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: white !important; border-radius: 12px !important; border: none !important;
        font-weight: 900 !important; padding: 12px 30px !important;
    }
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
    st.markdown('<div class="biz-banner">🛡️ EMPIRE ACCESS PORTAL</div>', unsafe_allow_html=True)
    u_in = st.text_input("Username:")
    p_in = st.text_input("Password:", type="password")
    if st.button("Unleash"):
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
    st.markdown(f"👑 **{st.session_state['user'].upper()}**")
    if st.button("S'éclipser (Log out)"):
        st.session_state.clear()
        st.rerun()
    st.markdown("---")
    st.header("➕ Nouveau Client")
    n_nom = st.text_input("Nom Complet")
    n_phone = st.text_input("WhatsApp (ex: 212...)")
    n_email = st.text_input("Email")
    s_choice = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
    final_s = st.text_input("Préciser Service") if s_choice == "Autre" else s_choice
    n_prix = st.number_input("Prix (DH)", min_value=0)
    n_deb = st.date_input("Date de Début", today)
    n_dur = st.number_input("Durée (Mois)", min_value=1, value=1)
    
    if st.button("🚀 Enregistrer au Cloud"):
        if n_nom and n_phone:
            n_fin = n_deb + relativedelta(months=int(n_dur))
            new_r = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"]
            df_clean = df.drop(columns=['Days', 'Date_Display'], errors='ignore') if not df.empty else df
            df_new = pd.concat([df_clean, pd.DataFrame([dict(zip(df_clean.columns, new_r))])], ignore_index=True)
            c_sheet_obj.clear()
            c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
            st.success("✅ Synchro réussie!")
            st.rerun()

# --- 4. MAIN BODY ---
st.markdown(f'<div class="biz-banner">🛡️ {st.session_state["biz_name"]} 🚀</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS PRO", "👥 BASE DE DONNÉES", "🔔 RAPPELS WHATSAPP", "📄 GÉNÉRATEUR REÇUS"])

with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("✅ CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("🚨 ALERTES (3j)", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
        
        st.markdown("### 📋 Résumé des Performances par Service")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'CA Total (DH)']
        
        # LUXURY HTML TABLE
        html_table = f"""<table class="luxury-table"><thead><tr>{"".join([f"<th>{col}</th>" for col in summary.columns])}</tr></thead>
        <tbody>{"".join([f"<tr>{''.join([f'<td>{val}</td>' for val in row])}</tr>" for row in summary.values])}</tbody></table>"""
        st.markdown(html_table, unsafe_allow_html=True)
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="simple_white"), use_container_width=True)

with t2:
    st.markdown("### 🛠️ Gestion Centralisée des Données")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Days"]
        edited = st.data_editor(df[cols], use_container_width=True, num_rows="dynamic", disabled=["Days", "Date Fin"])
        if st.button("💾 Sauvegarder les modifications"):
            final_df = edited.drop(columns=['Days'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Database Cloud Updated!")
            st.rerun()

with t3:
    st.subheader("🔔 Alertes de Renouvellement")
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')] if not df.empty else pd.DataFrame()
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 **{r['Nom']}** | 📺 {r['Service']} | ⏳ **{r['Days']} j**")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire bientot. On renouvelle?"
            cr.link_button("📲 Rappeler", f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}")
    else: 
        st.markdown('<div class="pro-alert-clean">🛡️ SYSTEM STATUS : Tout est parfait. Aucun retard aujourd\'hui !</div>', unsafe_allow_html=True)

with t4:
    st.subheader("📄 Générateur de Facture Client")
    if not df.empty:
        sel = st.selectbox("Sélectionner le client:", df['Nom'].unique())
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
