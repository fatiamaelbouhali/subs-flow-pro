import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V57 - VIBRANT ROSE & MUSTARD EDITION
st.set_page_config(page_title="EMPIRE_PRO_V57", layout="wide", page_icon="🌸")

# ⚡ THE VIBRANT CSS ENGINE - LUXURY SOFT COLORS
st.markdown("""
    <style>
    /* 1. Background Rose Barad (Soft Pink) */
    .stApp { background-color: #fff5f7 !important; }
    
    /* 2. Business Banner - Mustard to Rose Gradient */
    .biz-banner {
        background: linear-gradient(135deg, #eab308 0%, #ec4899 100%);
        padding: 30px; border-radius: 20px; color: white !important;
        text-align: center; font-size: 42px; font-weight: 900;
        margin-bottom: 30px; border: 3px solid #ffffff;
        box-shadow: 0 10px 30px rgba(234, 179, 8, 0.3);
    }

    /* 3. Metrics Boxes - Mustard Style */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 2px solid #eab308 !important; /* Mustard Gold */
        border-radius: 18px !important;
        padding: 20px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05) !important;
    }
    div[data-testid="stMetricValue"] > div { color: #854d0e !important; font-size: 38px !important; font-weight: 900; }
    div[data-testid="stMetricLabel"] p { color: #b45309 !important; font-size: 16px !important; font-weight: 700; text-transform: uppercase; }

    /* 4. Tabs Styling - Chic Blue & Pink */
    .stTabs [data-baseweb="tab"] { font-weight: bold; font-size: 18px; color: #64748b !important; }
    .stTabs [aria-selected="true"] { 
        background-color: #ec4899 !important; 
        color: white !important; 
        border-radius: 10px 10px 0 0 !important;
        box-shadow: 0 5px 15px rgba(236, 72, 153, 0.3) !important;
    }

    /* 5. Inputs & Labels Visibility (Dark Text for Light Background) */
    label p, .stMarkdown p, h1, h2, h3 { color: #1e293b !important; font-weight: 700 !important; }
    input, select, textarea { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        border: 1px solid #e2e8f0 !important; 
        border-radius: 10px !important; 
    }

    /* 6. Styled Table (Summary) */
    .styled-table {
        width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 18px;
        text-align: left; border-radius: 15px; overflow: hidden;
    }
    .styled-table thead tr { background: #eab308; color: #ffffff; }
    .styled-table th, .styled-table td { padding: 15px 20px; }
    .styled-table tbody tr { background-color: #ffffff; color: #1e293b; border-bottom: 1px solid #f1f5f9; }
    .styled-table tbody tr:nth-of-type(even) { background-color: #fff9eb; }
    </style>
    """, unsafe_allow_html=True)

# MASTER ADMIN ID
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=scope))

client = get_gspread_client()

# --- 1. LOGIN ---
if "auth" not in st.session_state:
    st.markdown('<div class="biz-banner">🌸 EMPIRE BUSINESS LOGIN</div>', unsafe_allow_html=True)
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
        except Exception as e: st.error(f"Error: {e}")
    st.stop()

# --- 2. LOAD DATA ---
try:
    c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
    df = pd.DataFrame(c_sheet_obj.get_all_records())
except:
    st.error("Sheet introuvable.")
    st.stop()

today = datetime.now().date()

# --- 3. CLEANING ---
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.date
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = pd.to_datetime(df['Date Fin']).dt.strftime('%Y-%m-%d').fillna("N/A")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 4. INTERFACE ---
st.markdown(f'<div class="biz-banner">👑 {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS PRO", "👥 GESTION", "🔔 RAPPELS", "📄 REÇUS"])

# TAB 1: ANALYTICS
with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("✅ CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("🚨 ALERTES (3j)", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
        
        st.markdown("### 📋 Résumé des Revenus")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'CA Total (DH)']
        
        # HTML STYLED TABLE (Mustard Theme)
        html_table = f"""<table class="styled-table"><thead><tr>{"".join([f"<th>{col}</th>" for col in summary.columns])}</tr></thead>
        <tbody>{"".join([f"<tr>{''.join([f'<td>{val}</td>' for val in row])}</tr>" for row in summary.values])}</tbody></table>"""
        st.markdown(html_table, unsafe_allow_html=True)

        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="simple_white"), use_container_width=True)

# TAB 2: GESTION
with t2:
    with st.expander("➕ AJOUTER UN NOUVEAU CLIENT"):
        ca, cb, cc = st.columns(3)
        with ca:
            n_nom = st.text_input("Nom Complet")
            n_phone = st.text_input("WhatsApp")
            n_email = st.text_input("Email")
        with cb:
            s_choice = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
            final_s = st.text_input("Préciser Service") if s_choice == "Autre" else s_choice
            n_prix = st.number_input("Prix (DH)", min_value=0)
        with cc:
            n_deb = st.date_input("Date de Début", today)
            n_dur = st.number_input("Durée (Mois)", min_value=1, value=1)
        
        if st.button("🚀 Enregistrer au Cloud"):
            if n_nom and n_phone:
                n_fin = n_deb + relativedelta(months=int(n_dur))
                # Smart Insertion Logic
                cols_target = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status"]
                new_data = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"]
                df_clean = df[cols_target] if not df.empty else pd.DataFrame(columns=cols_target)
                df_final = pd.concat([df_clean, pd.DataFrame([new_data], columns=cols_target)], ignore_index=True)
                c_sheet_obj.clear()
                c_sheet_obj.update([df_final.columns.values.tolist()] + df_final.astype(str).values.tolist())
                st.success("✅ Synchronisé wa7ed-te7t-wa7ed!")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Days"]
        edited = st.data_editor(df[cols], use_container_width=True, num_rows="dynamic", disabled=["Days", "Date Fin"])
        if st.button("💾 Sauvegarder Changes"):
            final_df = edited.drop(columns=['Days'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Database Updated!")
            st.rerun()

# TAB 3: ALERTS
with t3:
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 {r['Nom']} | ⏳ {r['Days']} j (Expire le {r['Date_Display']})")
            msg = f"Bonjour {r['Nom']}, renouvellement {r['Service']}? Expire le {r['Date_Display']}"
            cr.link_button("📲 Rappeler", f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}")
    else: st.success("Tout est propre.")

# TAB 4: REÇUS
with t4:
    if not df.empty:
        sel = st.selectbox("Client pour Reçu:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"*REÇU - {st.session_state['biz_name']}*\n👤 Client: {c['Nom']}\n📺 Service: {c['Service']}\n💰 Prix: {c['Prix']} DH\n⌛ Expire le: {c['Date_Display']}\n*Merci !*"
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

st.sidebar.button("Log out", on_click=lambda: st.session_state.clear())
