import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V59 - THE ULTIMATE SAAS BOSS EDITION
st.set_page_config(page_title="EMPIRE_PRO_V59", layout="wide", page_icon="💎")

# ⚡ THE SUPREME BOSS CSS (COMPACT & VIBRANT)
st.markdown("""
    <style>
    .stApp { background-color: #fff8f9 !important; }
    
    /* Compact Business Banner */
    .biz-banner {
        background: linear-gradient(135deg, #f59e0b 0%, #ec4899 100%);
        padding: 15px; border-radius: 15px; color: white !important;
        text-align: center; font-size: 28px; font-weight: 900;
        margin-bottom: 20px; border: 2px solid #ffffff;
        box-shadow: 0 8px 25px rgba(236, 72, 153, 0.2);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }
    .stSidebar [data-testid="stExpander"] { background-color: #f8fafc !important; border: 1px solid #ec4899 !important; border-radius: 10px; }

    /* Metrics Luxury */
    div[data-testid="stMetric"] {
        background: white !important;
        border: 2px solid #f59e0b !important;
        border-radius: 15px !important;
        padding: 15px !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stMetricValue"] > div { color: #db2777 !important; font-size: 32px !important; font-weight: 900; }
    div[data-testid="stMetricLabel"] p { color: #f59e0b !important; font-size: 14px !important; font-weight: bold; text-transform: uppercase; }

    /* Data Editor & Tables */
    .stDataFrame { border-radius: 10px !important; }
    label p { color: #1e293b !important; font-weight: 800; }
    
    /* Custom Table Style (Analytics Summary) */
    .summary-table { width: 100%; border-collapse: collapse; border-radius: 10px; overflow: hidden; margin-top: 10px; }
    .summary-table thead { background: #f59e0b; color: white; }
    .summary-table th, .summary-table td { padding: 12px; text-align: left; border-bottom: 1px solid #f1f5f9; }
    .summary-table td { background: white; font-weight: bold; color: #db2777; }
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
    st.markdown('<div class="biz-banner">🛡️ EMPIRE SaaS GATEWAY</div>', unsafe_allow_html=True)
    u_in = st.text_input("Username:")
    p_in = st.text_input("Password:", type="password")
    if st.button("Unlock Power"):
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

# --- 3. SIDEBAR (LOGOUT + ADD CLIENT FORM) ---
with st.sidebar:
    st.markdown(f"👤 **{st.session_state['user']}**")
    if st.button("Déconnexion"):
        st.session_state.clear()
        st.rerun()
    st.markdown("---")
    st.subheader("➕ Ajouter un Client")
    with st.expander("Ouvrir le Formulaire", expanded=False):
        n_nom = st.text_input("Nom Complet")
        n_phone = st.text_input("WhatsApp")
        n_email = st.text_input("Email")
        s_choice = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = st.text_input("Préciser Service") if s_choice == "Autre" else s_choice
        n_prix = st.number_input("Prix (DH)", min_value=0)
        n_deb = st.date_input("Date de Début", today)
        n_dur = st.number_input("Durée (Mois)", min_value=1, value=1)
        
        if st.button("🚀 Enregistrer au Cloud"):
            if n_nom and n_phone:
                n_fin = n_deb + relativedelta(months=int(n_dur))
                new_row = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"]
                # Manual sync to avoid data editor conflict
                df_clean = df.drop(columns=['Days', 'Date_Display'], errors='ignore') if not df.empty else df
                df_new = pd.concat([df_clean, pd.DataFrame([dict(zip(df_clean.columns, new_row))])], ignore_index=True)
                c_sheet_obj.clear()
                c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
                st.success("✅ Synchro OK!")
                st.rerun()

# --- 4. MAIN INTERFACE ---
st.markdown(f'<div class="biz-banner">🛡️ {st.session_state["biz_name"]} 🚀</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS PRO", "👥 BASE DE DONNÉES", "🔔 RAPPELS WHATSAPP", "📄 GÉNÉRATEUR REÇUS"])

# TAB 1: ANALYTICS
with t1:
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 REVENUE GLOBAL", f"{df['Prix'].sum() if not df.empty else 0} DH")
    c2.metric("✅ CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']) if not df.empty else 0)
    c3.metric("🚨 ALERTES (3j)", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]) if not df.empty else 0)

    st.markdown("### 📋 Résumé Business par Service")
    if not df.empty:
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'CA Total (DH)']
        # Custom HTML Table for style
        st.write(summary.to_html(classes='summary-table', index=False, border=0), unsafe_allow_html=True)
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="simple_white"), use_container_width=True)

# TAB 2: GESTION (NUMBER FORMATTING FIXED)
with t2:
    st.subheader("🛠️ Édition Rapide")
    if not df.empty:
        # Format Prix and Days in the editor to be Bold/Pro
        edited = st.data_editor(
            df[["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Days"]],
            column_config={
                "Prix": st.column_config.NumberColumn("Prix (DH)", format="%d DH", width="medium"),
                "Days": st.column_config.NumberColumn("Jours", format="%d j", width="small"),
                "Status": st.column_config.SelectboxColumn("Status", options=["Actif", "Payé", "Expiré", "Annulé"])
            },
            use_container_width=True,
            num_rows="dynamic",
            disabled=["Days", "Date Fin"]
        )
        if st.button("💾 Sauvegarder les modifications"):
            final_df = edited.drop(columns=['Days'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Database Updated!")
            st.rerun()

# TAB 3: RELANCES
with t3:
    st.subheader("🔔 Centre de Relance WhatsApp")
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')] if not df.empty else pd.DataFrame()
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 **{r['Nom']}** | ⏳ **{r['Days']} j** (Expire: {r['Date Fin']})")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire bientot. On renouvelle?"
            cr.link_button("📲 Rappeler", f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}")
    else: st.success("Aucun retard aujourd'hui.")

# TAB 4: REÇUS
with t4:
    if not df.empty:
        sel = st.selectbox("Choisir client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = (f"✅ *REÇU - {st.session_state['biz_name']}*\n"
                f"👤 Client: *{c['Nom']}*\n"
                f"📺 Service: *{c['Service']}*\n"
                f"💰 Prix: *{c['Prix']} DH*\n"
                f"⌛ Expire: *{c['Date_Display']}*\n"
                f"*Merci pour votre confiance !*")
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")
