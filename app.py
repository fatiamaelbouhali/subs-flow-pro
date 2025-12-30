import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V55 - GALAXY PREMIUM EDITION
st.set_page_config(page_title="EMPIRE_GALAXY_V55", layout="wide", page_icon="💎")

# ⚡ THE SUPREME CSS - VISUAL PERFECTION
st.markdown("""
    <style>
    /* Background & Main App */
    .stApp { background-color: #0e1117; }
    
    /* Metrics Styling */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.7);
        border: 2px solid #6366f1;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
    }
    div[data-testid="stMetricValue"] > div { color: #00ffcc !important; font-size: 40px !important; font-weight: 900; }
    div[data-testid="stMetricLabel"] p { color: #ffffff !important; font-weight: bold; text-transform: uppercase; }

    /* Custom Business Banner */
    .biz-banner {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        padding: 30px; border-radius: 20px; color: white !important;
        text-align: center; font-size: 45px; font-weight: 900;
        margin-bottom: 30px; border: 2px solid #ffffff;
        box-shadow: 0 10px 40px rgba(168, 85, 247, 0.4);
    }

    /* Styled Expander (Add Client) - Premium Glass Look */
    .stExpander {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid #6366f1 !important;
        border-radius: 15px !important;
    }
    .streamlit-expanderHeader { color: #ffffff !important; font-size: 20px !important; font-weight: 800 !important; }

    /* Input Fields - White Theme for Maximum Readability */
    input, select, .stSelectbox div, .stNumberInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab"] { font-weight: bold; font-size: 18px; color: #94a3b8 !important; }
    .stTabs [aria-selected="true"] { color: #ffffff !important; border-bottom: 4px solid #00ffcc !important; }

    /* Styled Table (Summary) */
    .styled-table {
        width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 18px;
        text-align: left; border-radius: 15px; overflow: hidden;
    }
    .styled-table thead tr { background: linear-gradient(90deg, #6366f1, #a855f7); color: #ffffff; }
    .styled-table th, .styled-table td { padding: 15px 20px; }
    .styled-table tbody tr { background-color: #ffffff; color: #1e293b; border-bottom: 1px solid #e2e8f0; }
    .styled-table tbody tr:nth-of-type(even) { background-color: #f8fafc; }
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
    st.markdown('<div class="biz-banner">🏦 SaaS Empire Login</div>', unsafe_allow_html=True)
    col_l, col_r = st.columns([1, 1])
    with col_l:
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
st.markdown(f'<div class="biz-banner">🚀 {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS PRO", "👥 GESTION", "🔔 RAPPELS", "📄 REÇUS"])

# TAB 1: ANALYTICS (GALAXY THEME)
with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("✅ CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("🚨 ALERTES (3j)", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))

        st.markdown("### 📋 Résumé par Service")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'CA Total (DH)']
        
        # HTML STYLED TABLE
        html_table = f"""<table class="styled-table"><thead><tr>{"".join([f"<th>{col}</th>" for col in summary.columns])}</tr></thead>
        <tbody>{"".join([f"<tr>{''.join([f'<td>{val}</td>' for val in row])}</tr>" for row in summary.values])}</tbody></table>"""
        st.markdown(html_table, unsafe_allow_html=True)

        # GALAXY CHART (Fixed Axes)
        fig = px.bar(df, x='Service', y='Prix', color='Status', barmode='group', template="plotly_dark",
                     color_discrete_map={'Actif':'#00ffcc', 'Payé':'#6366f1', 'Expiré':'#ff4b4b'})
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          font=dict(color="white", size=14),
                          xaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color="#00d2ff", size=14)),
                          yaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color="#00d2ff", size=14)))
        st.plotly_chart(fig, use_container_width=True)

# TAB 2: GESTION (RESTORED ALL FIELDS)
with t2:
    with st.expander("➕ AJOUTER UN NOUVEAU CLIENT (VIBRANT)"):
        ca, cb, cc = st.columns(3)
        with ca:
            n_nom = st.text_input("Nom Complet Client")
            n_phone = st.text_input("WhatsApp (ex: 212...)")
            n_email = st.text_input("Email")
        with cb:
            s_choice = st.selectbox("Service Principal", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
            final_s = st.text_input("Préciser le service") if s_choice == "Autre" else s_choice
            n_prix = st.number_input("Prix (DH)", min_value=0)
        with cc:
            n_deb = st.date_input("Date de Début", today)
            n_dur = st.number_input("Durée (en Mois)", min_value=1, value=1)
            n_stat = st.selectbox("Status Initial", ["Actif", "Payé", "En Attente"])
        
        if st.button("🚀 Enregistrer au Cloud"):
            if n_nom and n_phone and final_s:
                n_fin = n_deb + relativedelta(months=int(n_dur))
                new_data = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), n_stat]
                # Smart Data Insert
                cols_target = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status"]
                df_clean = df[cols_target] if not df.empty else pd.DataFrame(columns=cols_target)
                df_final = pd.concat([df_clean, pd.DataFrame([new_data], columns=cols_target)], ignore_index=True)
                c_sheet_obj.clear()
                c_sheet_obj.update([df_final.columns.values.tolist()] + df_final.astype(str).values.tolist())
                st.success("✅ Synchronisation réussie !")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        cols_edit = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Days"]
        edited = st.data_editor(df[cols_edit], use_container_width=True, num_rows="dynamic", disabled=["Days", "Date Fin"])
        if st.button("💾 Sauvegarder les modifications"):
            final_df = edited.drop(columns=['Days'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Database Pro Updated!")
            st.rerun()

# TAB 3: ALERTES
with t3:
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 {r['Nom']} | 📺 {r['Service']} | ⏳ **{r['Days']} jours restants**")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire le {r['Date_Display']}. On renouvelle?"
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
            cr.link_button("📲 Rappeler", wa)
    else: st.success("Tout est propre.")

# TAB 4: REÇUS
with t4:
    if not df.empty:
        sel = st.selectbox("Sélectionner pour Reçu:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = (f"✅ *REÇU DE PAIEMENT - {st.session_state['biz_name']}*\n━━━━━━━━━━━━━━━━━━\n"
                f"👤 Client: *{c['Nom']}*\n📺 Service: *{c['Service']}*\n💰 Prix: *{c['Prix']} DH*\n⌛ Expire: *{c['Date_Display']}*\n"
                f"━━━━━━━━━━━━━━━━━━\n🤝 *Merci !*")
        st.code(reçu)
        st.link_button("📲 WhatsApp Direct", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

if st.sidebar.button("Log out"):
    st.session_state.clear()
    st.rerun()
