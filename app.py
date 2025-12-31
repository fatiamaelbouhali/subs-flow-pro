import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V58 - VIBRANT SOUL EDITION (MAXIMUM ENERGY)
st.set_page_config(page_title="EMPIRE_PRO_V58", layout="wide", page_icon="⚡")

# ⚡ THE SUPREME VIBRANT CSS - GIVING SOUL TO EVERY PIXEL
st.markdown("""
    <style>
    /* 1. Background Soft Pink Luxury */
    .stApp { background-color: #fff8f9 !important; }
    
    /* 2. Business Banner Pro (Shield Icon) */
    .biz-banner {
        background: linear-gradient(135deg, #f59e0b 0%, #ec4899 100%);
        padding: 30px; border-radius: 20px; color: white !important;
        text-align: center; font-size: 45px; font-weight: 900;
        margin-bottom: 30px; border: 3px solid #ffffff;
        box-shadow: 0 15px 40px rgba(236, 72, 153, 0.3);
    }

    /* 3. Metrics Cards (The Analytics Pro) */
    div[data-testid="stMetric"] {
        background: white !important;
        border: 2px solid #f59e0b !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 10px 25px rgba(245, 158, 11, 0.1) !important;
    }
    div[data-testid="stMetricValue"] > div { color: #db2777 !important; font-size: 42px !important; font-weight: 900; }
    div[data-testid="stMetricLabel"] p { color: #f59e0b !important; font-size: 17px !important; font-weight: bold !important; text-transform: uppercase; }

    /* 4. Gestion Tab - Adding Soul to Inputs */
    .stExpander {
        background-color: white !important;
        border: 2px solid #ec4899 !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 20px rgba(236, 72, 153, 0.1) !important;
    }
    label p { color: #475569 !important; font-weight: 800 !important; font-size: 1.1rem !important; }
    input, select, .stSelectbox div { 
        border-radius: 12px !important; 
        border: 1px solid #e2e8f0 !important; 
        font-weight: 600 !important; 
    }

    /* 5. Alert System - Pro Gradient for Clean State */
    .stAlert {
        border-radius: 15px !important;
        border: none !important;
        background: linear-gradient(90deg, #f0fdf4 0%, #dcfce7 100%) !important;
        border-left: 8px solid #22c55e !important;
    }

    /* 6. Reçus Tab - Card Style */
    .stCode {
        background-color: #1e293b !important;
        color: #00ffcc !important;
        border-radius: 15px !important;
        padding: 20px !important;
        border: 2px solid #ec4899 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
    }

    /* 7. Tabs Pro */
    .stTabs [data-baseweb="tab"] { font-weight: bold; font-size: 18px; color: #64748b !important; }
    .stTabs [aria-selected="true"] { 
        background-color: #f59e0b !important; 
        color: white !important; 
        border-radius: 10px 10px 0 0 !important; 
    }
    
    /* 8. Styled Table (Summary) */
    .styled-table {
        width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 18px;
        border-radius: 15px; overflow: hidden;
    }
    .styled-table thead tr { background: #f59e0b; color: white; }
    .styled-table td { padding: 15px; background: white; color: #1e293b; border-bottom: 1px solid #f1f5f9; }
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
    st.markdown('<div class="biz-banner">🛡️ EMPIRE DIGITAL PORTAL</div>', unsafe_allow_html=True)
    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
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
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.date
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = pd.to_datetime(df['Date Fin']).dt.strftime('%Y-%m-%d').fillna("N/A")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 3. THE UI ---
st.markdown(f'<div class="biz-banner">🛡️ {st.session_state["biz_name"]} 🚀</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS PRO", "👥 GESTION", "🔔 RAPPELS", "📄 REÇUS"])

with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("✅ CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("🚨 ALERTES URGENTES", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
        
        st.markdown("### 📋 Résumé Exécutif")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'CA Total (DH)']
        html_table = f"""<table class="styled-table"><thead><tr>{"".join([f"<th>{col}</th>" for col in summary.columns])}</tr></thead>
        <tbody>{"".join([f"<tr>{''.join([f'<td>{val}</td>' for val in row])}</tr>" for row in summary.values])}</tbody></table>"""
        st.markdown(html_table, unsafe_allow_html=True)
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="simple_white"), use_container_width=True)

with t2:
    st.markdown("### 👥 Gestion des Abonnements")
    with st.expander("➕ AJOUTER UN NOUVEAU CLIENT"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom")
        n_phone = ca.text_input("WhatsApp")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Nom service") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix (DH)", min_value=0)
        n_deb = cc.date_input("Date de Début", today)
        n_dur = cc.number_input("Durée (Mois)", min_value=1, value=1)
        if st.button("🚀 Enregistrer au Cloud"):
            if n_nom and n_phone:
                n_fin = n_deb + relativedelta(months=int(n_dur))
                new_row = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"]
                df_clean = df.drop(columns=['Days', 'Date_Display'], errors='ignore') if not df.empty else df
                df_new = pd.concat([df_clean, pd.DataFrame([dict(zip(df_clean.columns, new_row))])], ignore_index=True)
                c_sheet_obj.clear()
                c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
                st.success("✅ Synchro OK!")
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

with t3:
    st.markdown("### 🔔 Alertes de Relance")
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 {r['Nom']} | 📺 {r['Service']} | ⏳ **{r['Days']} j**")
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(f'Bonjour {r[0]}, renouvellement?')}"
            cr.link_button("📲 Rappeler", wa)
    else: st.success("🚀 Tout est parfait. Aucun retard aujourd'hui !")

with t4:
    st.markdown("### 📄 Générateur de Reçu Pro")
    if not df.empty:
        sel = st.selectbox("Choisir client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = (f"✅ *REÇU - {st.session_state['biz_name']}*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👤 Client: *{c['Nom']}*\n"
                f"📺 Service: *{c['Service']}*\n"
                f"💰 Prix: *{c['Prix']} DH*\n"
                f"⌛ Expire: *{c['Date_Display']}*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🤝 *Merci pour votre confiance !*")
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

st.sidebar.button("Déconnexion", on_click=lambda: st.session_state.clear())
