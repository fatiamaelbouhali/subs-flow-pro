import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V38 - THE CEO DASHBOARD (PREMIUM UI)
st.set_page_config(page_title="EMPIRE_PRO_V38", layout="wide", page_icon="📈")

# ⚡ CSS DIAL L-M3ALLMIN - HIGH CONTRAST & LUXURY
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    [data-testid="stMetric"] {
        background: #1a1c24;
        border: 1px solid #3b82f6;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    div[data-testid="stMetricValue"] > div { color: #00ffcc !important; font-size: 36px !important; font-weight: 800; }
    div[data-testid="stMetricLabel"] p { color: #ffffff !important; font-size: 16px !important; font-weight: bold; text-transform: uppercase; }
    .biz-banner {
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        padding: 30px; border-radius: 15px; color: white !important;
        text-align: center; font-size: 45px; font-weight: 900;
        margin-bottom: 30px; border: 2px solid #ffffff;
    }
    .section-title { color: #00d2ff; font-size: 24px; font-weight: bold; margin-top: 20px; }
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
    st.title("🛡️ Secure Partner Access")
    u_in = st.text_input("Username:")
    p_in = st.text_input("Password:", type="password")
    if st.button("Unleash the Empire"):
        try:
            m_sheet = client.open("Master_Admin").sheet1
            m_df = pd.DataFrame(m_sheet.get_all_records())
            match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & 
                         (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
            if not match.empty:
                if match.iloc[0]['Status'] == 'Active':
                    st.session_state["auth"] = True
                    st.session_state["user"] = u_in
                    b_name = str(match.iloc[0]['Business_Name']).strip()
                    st.session_state["biz_name"] = b_name if b_name != 'nan' and b_name != "" else f"{u_in.upper()} PRO"
                    st.session_state["sheet_name"] = str(match.iloc[0]['Sheet_Name']).strip()
                    st.rerun()
                else: st.error("🚫 Bloqué.")
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

# --- 3. DATA CLEANING & LOGIC ---
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce')
    df['Jours Restants'] = df['Date Fin'].apply(lambda x: (x.date() - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = df['Date Fin'].dt.strftime('%Y-%m-%d').fillna("NON DÉFINI")
    df.loc[(df['Jours Restants'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 4. THE INTERFACE ---
st.markdown(f'<div class="biz-banner">🚀 {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS PRO", "👥 CLIENTS", "🔔 RAPPELS", "📄 REÇUS"])

# ==========================================
# TAB 1: ANALYTICS (REBORN)
# ==========================================
with t1:
    if not df.empty:
        # TOP METRICS
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("✅ CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("🚨 RELANCES (3j)", len(df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]))

        st.markdown('<div class="section-title">📈 Analyse du Business</div>', unsafe_allow_html=True)
        
        g1, g2 = st.columns([2, 1])
        with g1:
            # Simple Bar Chart for Revenue
            fig_rev = px.bar(df.groupby('Service')['Prix'].sum().reset_index(), 
                             x='Service', y='Prix', text_auto='.2s',
                             title="Revenue par Service (DH)", template="plotly_dark",
                             color_discrete_sequence=['#00d2ff'])
            st.plotly_chart(fig_rev, use_container_width=True)
        
        with g2:
            # Status Distribution
            fig_pie = px.pie(df, names='Status', title="Répartition des Status", 
                             hole=0.6, template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)

        # 💡 SUMMARY TABLE FOR THE BOSS
        st.markdown('<div class="section-title">📊 Résumé par Service</div>', unsafe_allow_html=True)
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Nombre de Clients', 'Revenue Total (DH)']
        st.table(summary)
    else:
        st.info("Aucune donnée pour l'analyse.")

# ==========================================
# TAB 2: GESTION (STAYS CLEAN)
# ==========================================
with t2:
    with st.expander("➕ AJOUTER UN NOUVEAU CLIENT"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom")
        n_phone = ca.text_input("WhatsApp")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Nom service") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix", min_value=0)
        n_dur = cc.number_input("Durée (Mois)", min_value=1, value=1)
        if st.button("💾 Sauvegarder"):
            if n_nom and n_phone:
                n_fin = today + relativedelta(months=int(n_dur))
                c_sheet_obj.append_row([n_nom, str(n_phone), n_email, final_s, n_prix, str(today), n_dur, str(n_fin), "Actif"])
                st.success("✅ Synced!")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Status", "Jours Restants", "Date_Display"]
        edited = st.data_editor(df[cols], use_container_width=True, num_rows="dynamic", disabled=["Jours Restants", "Date_Display"])
        if st.button("💾 Valider les modifications"):
            final_df = edited.drop(columns=['Jours Restants', 'Date_Display'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Database Updated!")
            st.rerun()

# ==========================================
# TAB 3: ALERTS
# ==========================================
with t3:
    st.subheader("Relances WhatsApp 📲")
    urgent = df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            col_l, col_r = st.columns([3, 1])
            icon = "🔴" if r['Jours Restants'] <= 0 else "🟠"
            col_l.warning(f"{icon} **{r['Nom']}** | **{r['Jours Restants']} j** (Expire: {r['Date_Display']})")
            wa = f"https://wa.me/{r['Phone']}?text=Bonjour {r['Nom']}, renouvellement {r['Service']}? Fin le {r['Date_Display']}"
            col_r.link_button("📲 Rappeler", wa)
    else: st.success("Aucun retard.")

# ==========================================
# TAB 4: REÇUS
# ==========================================
with t4:
    st.subheader("Générateur de Reçu 📄")
    if not df.empty:
        sel = st.selectbox("Choisir klyan:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"*REÇU - {st.session_state['biz_name']}*\n👤 Client: {c['Nom']}\n📺 Service: {c['Service']}\n💰 Prix: {c['Prix']} DH\n⌛ Expire le: {c['Date_Display']}\n*Merci !*"
        st.code(reçu)
        st.link_button("📲 WhatsApp Direct", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

st.sidebar.button("Déconnexion", on_click=lambda: st.session_state.clear())
