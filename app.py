import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V56 - EXECUTIVE DIAMOND EDITION
st.set_page_config(page_title="EMPIRE_V56_EXECUTIVE", layout="wide", page_icon="💎")

# ⚡ THE SUPREME CSS - LUXURY & READABILITY
st.markdown("""
    <style>
    /* Background Pro - Soft Dark */
    .stApp { background-color: #0b0e14; }
    
    /* Metrics Box - Ultra Clean Glass */
    div[data-testid="stMetric"] {
        background: rgba(31, 41, 55, 0.4);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stMetricValue"] > div { color: #00ffcc !important; font-size: 35px !important; font-weight: 800; }
    div[data-testid="stMetricLabel"] p { color: #94a3b8 !important; font-size: 14px !important; font-weight: 600; text-transform: uppercase; }

    /* Business Banner - Modern Gradient */
    .biz-banner {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        padding: 20px; border-radius: 15px; color: white !important;
        text-align: center; font-size: 38px; font-weight: 900;
        margin-bottom: 25px; border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.3);
    }

    /* THE DATA EDITOR FIX - PREMIUM STYLE */
    [data-testid="stDataEditor"] {
        background-color: #161b22 !important;
        border-radius: 12px !important;
        border: 1px solid #30363d !important;
        padding: 5px !important;
    }
    
    /* Expander Styling */
    .stExpander {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
    }

    /* Tabs Decoration */
    .stTabs [data-baseweb="tab"] { font-weight: bold; font-size: 16px; color: #94a3b8 !important; }
    .stTabs [aria-selected="true"] { color: #ffffff !important; border-bottom: 3px solid #6366f1 !important; }

    /* Styled Table (Summary) */
    .styled-table {
        width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 16px;
        text-align: left; border-radius: 12px; overflow: hidden;
    }
    .styled-table thead tr { background: #6366f1; color: #ffffff; }
    .styled-table th, .styled-table td { padding: 12px 15px; }
    .styled-table tbody tr { background-color: #ffffff; color: #1e293b; border-bottom: 1px solid #e2e8f0; }
    .styled-table tbody tr:nth-of-type(even) { background-color: #f1f5f9; }
    </style>
    """, unsafe_allow_html=True)

# ID DIAL MASTER ADMIN
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=scope))

client = get_gspread_client()

# --- 1. LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.markdown('<div class="biz-banner">🏦 SaaS Empire Portal</div>', unsafe_allow_html=True)
    u_in = st.text_input("Business Username:")
    p_in = st.text_input("Access Password:", type="password")
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

# --- 3. DATA CLEANING & LOGIC ---
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.date
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = pd.to_datetime(df['Date Fin']).dt.strftime('%Y-%m-%d').fillna("N/A")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 4. THE INTERFACE ---
st.markdown(f'<div class="biz-banner">💎 {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS PRO", "👥 GESTION", "🔔 RELANCES", "📄 REÇUS"])

# TAB 1: ANALYTICS
with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("✅ CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("🚨 ALERTES (3j)", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))

        st.markdown("### 📊 Résumé Exécutif")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'Chiffre d\'Affaires (DH)']
        
        html_table = f"""<table class="styled-table"><thead><tr>{"".join([f"<th>{col}</th>" for col in summary.columns])}</tr></thead>
        <tbody>{"".join([f"<tr>{''.join([f'<td>{val}</td>' for val in row])}</tr>" for row in summary.values])}</tbody></table>"""
        st.markdown(html_table, unsafe_allow_html=True)

        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="plotly_dark", barmode='group'), use_container_width=True)

# TAB 2: GESTION (THE STYLED EDITOR)
with t2:
    with st.expander("➕ AJOUTER UN NOUVEAU CLIENT"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom Complet")
        n_phone = ca.text_input("WhatsApp (ex: 212...)")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Préciser Service") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix (DH)", min_value=0)
        n_deb = cc.date_input("Date de Début", today)
        n_dur = cc.number_input("Durée (Mois)", min_value=1, value=1)
        
        if st.button("🚀 Enregistrer au Cloud"):
            if n_nom and n_phone and final_s:
                n_fin = n_deb + relativedelta(months=int(n_dur))
                # New row sync
                cols_target = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status"]
                new_data = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"]
                df_clean = df[cols_target] if not df.empty else pd.DataFrame(columns=cols_target)
                df_final = pd.concat([df_clean, pd.DataFrame([new_data], columns=cols_target)], ignore_index=True)
                c_sheet_obj.clear()
                c_sheet_obj.update([df_final.columns.values.tolist()] + df_final.astype(str).values.tolist())
                st.success("✅ Client synchronisé !")
                st.rerun()

    st.markdown("---")
    st.subheader("🛠️ Édition Rapide de la Base")
    if not df.empty:
        # Table cleaner and more readable
        cols_to_show = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Days"]
        edited = st.data_editor(df[cols_to_show], use_container_width=True, num_rows="dynamic", disabled=["Days", "Date Fin"])
        
        if st.button("💾 Sauvegarder les modifications"):
            final_df = edited.drop(columns=['Days'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Google Sheets Synchro!")
            st.rerun()

# TAB 3: RELANCES
with t3:
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 **{r['Nom']}** | ⏳ **{r['Days']} jours** (Expire: {r['Date_Display']})")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire le {r['Date_Display']}. On renouvelle?"
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
            cr.link_button("📲 Rappeler", wa)
    else: st.success("Aucune relance.")

# TAB 4: REÇUS
with t4:
    if not df.empty:
        sel = st.selectbox("Sélectionner Client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = (f"✅ *REÇU - {st.session_state['biz_name']}*\n━━━━━━━━━━━━━━━━━━\n"
                f"👤 Client: *{c['Nom']}*\n📺 Service: *{c['Service']}*\n💰 Prix: *{c['Prix']} DH*\n⌛ Expire: *{c['Date_Display']}*\n"
                f"━━━━━━━━━━━━━━━━━━\n🤝 *Merci !*")
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

if st.sidebar.button("Log out"):
    st.session_state.clear()
    st.rerun()
