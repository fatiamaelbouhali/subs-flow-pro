import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V32 - MAXIMUM VISIBILITY (FINAL PATCH)
st.set_page_config(page_title="SUBS_FLOW_PRO_V32", layout="wide", page_icon="💎")

# ⚡ CSS DIAL L-BOSS - NO MORE VISIBILITY ISSUES
st.markdown("""
    <style>
    /* Force ga3 l-ktaba wast l-app t-welli BIDA o bayna */
    .stApp, .stMarkdown, label, .stMetricValue, .stMetricLabel {
        color: #FFFFFF !important;
    }
    
    /* Metrics Box Contrast */
    div[data-testid="stMetric"] {
        background-color: #1f2937 !important;
        border: 2px solid #00d2ff !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }

    /* Input Labels (Nom, Phone, etc.) - FORCE VISIBILITY */
    div[data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: bold !important;
        opacity: 1 !important;
    }

    /* Input Boxes Styling */
    .stTextInput input, .stNumberInput input, .stSelectbox div {
        background-color: #262730 !important;
        color: #FFFFFF !important;
        border: 1px solid #4b5563 !important;
    }

    /* Banner Styling */
    .biz-banner {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        padding: 20px;
        border-radius: 12px;
        color: #000000 !important;
        font-size: 40px;
        font-weight: 900;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0, 210, 255, 0.4);
    }
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
    st.title("🛡️ Secure SaaS Login")
    u_in = st.text_input("Username:")
    p_in = st.text_input("Password:", type="password")
    if st.button("Unlock Empire"):
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
            else: st.error("❌ Invalid login.")
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
    df['Jours Restants'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df.loc[(df['Jours Restants'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 3. THE INTERFACE ---
st.markdown(f'<div class="biz-banner">🚀 {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS", "👥 GESTION", "🔔 ALERTES", "📄 REÇUS"])

with t1:
    st.subheader("Performance Overview")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Revenue Global", f"{df['Prix'].sum()} DH")
        c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        c3.metric("Relances Urgent", len(df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]))
        
        st.markdown("---")
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="plotly_dark"), use_container_width=True)
        with g2:
            st.plotly_chart(px.pie(df, names='Service', hole=0.5, template="plotly_dark"), use_container_width=True)

with t2:
    st.subheader("Base de Données")
    with st.expander("➕ AJOUTER UN NOUVEAU CLIENT", expanded=False):
        ca, cb, cc = st.columns(3)
        with ca:
            n_nom = st.text_input("Nom Complet Client")
            n_phone = st.text_input("WhatsApp (212...)")
            n_email = st.text_input("Email")
        with cb:
            s_choice = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
            final_s = st.text_input("Préciser") if s_choice == "Autre" else s_choice
            n_prix = st.number_input("Prix (DH)", min_value=0)
        with cc:
            n_dur = st.number_input("Durée (Mois)", min_value=1, value=1)
            if st.button("🚀 Enregistrer au Cloud"):
                if n_nom and n_phone:
                    n_fin = today + relativedelta(months=int(n_dur))
                    c_sheet_obj.append_row([n_nom, str(n_phone), n_email, final_s, n_prix, str(today), n_dur, str(n_fin), "Actif"])
                    st.success("✅ Synchro réussie!")
                    st.rerun()

    st.markdown("---")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Status", "Jours Restants", "Date Fin"]
        actual_cols = [c for c in cols if c in df.columns]
        edited = st.data_editor(df[actual_cols], use_container_width=True, num_rows="dynamic", disabled=["Jours Restants", "Date Fin"])
        if st.button("💾 Sauvegarder Changes"):
            final_df = edited.drop(columns=['Jours Restants'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Database Updated!")
            st.rerun()

with t3:
    st.subheader("Relances WhatsApp 📲")
    urgent = df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            col_l, col_r = st.columns([3, 1])
            icon = "🔴" if r['Jours Restants'] <= 0 else "🟠"
            col_l.warning(f"{icon} **{r['Nom']}** | {r['Service']} | **{r['Jours Restants']} j**")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire bientot. On renouvelle?"
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
            col_r.link_button("📲 Rappeler", wa)
    else: st.success("Tout est propre.")

with t4:
    st.subheader("Générateur de Reçu Officiel 📄")
    if not df.empty:
        sel = st.selectbox("Choisir klyan:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"*REÇU - {st.session_state['biz_name']}*\n\n👤 Client: {c['Nom']}\n📩 Email: {c['Email']}\n📺 Service: {c['Service']}\n💰 Prix: {c['Prix']} DH\n⌛ Expire le: {c['Date Fin']}\n\n*Merci pour votre confiance !*"
        st.code(reçu)
        st.link_button(f"📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

st.sidebar.button("Déconnexion", on_click=lambda: st.session_state.clear())
