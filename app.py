import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V26 - CRYSTAL CLEAR UI
st.set_page_config(page_title="SUBS_FLOW_PRO_V26", layout="wide", page_icon="💎")

# ⚡ CSS DYAL S-SAYTARA (FORCE COLORS)
st.markdown("""
    <style>
    /* Background Metrics */
    div[data-testid="stMetric"] {
        background-color: #111827 !important;
        border: 2px solid #374151 !important;
        padding: 20px !important;
        border-radius: 15px !important;
    }
    /* Alwan dial l-ar9am */
    div[data-testid="stMetricValue"] > div {
        color: #00ff9d !important; /* Neon Green bach i-banu l-flooos */
        font-size: 35px !important;
        font-weight: bold !important;
    }
    /* Alwan dial l-ktaba sghira */
    div[data-testid="stMetricLabel"] > div > p {
        color: #ffffff !important;
        font-size: 16px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    /* Title Style */
    .main-title {
        color: #ffffff;
        font-size: 50px;
        font-weight: 900;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px #000000;
    }
    </style>
    """, unsafe_allow_html=True)

# ID DIAL MASTER ADMIN
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

client = get_gspread_client()

# --- 1. LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.title("🏦 Plateforme SaaS Management")
    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
    if st.button("Se Connecter & Dominer"):
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
                else: st.error("🚫 Accès suspendu.")
            else: st.error("❌ Identifiants incorrects.")
        except Exception as e: st.error(f"Error: {e}")
    st.stop()

# --- 2. LOAD DATA ---
try:
    c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
    df = pd.DataFrame(c_sheet_obj.get_all_records())
except:
    st.error("Base de données introuvable.")
    st.stop()

today = datetime.now().date()
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.date
    df['Jours Restants'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df.loc[(df['Jours Restants'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 3. THE INTERFACE ---
# FORCE BIZ NAME DISPLAY
st.markdown(f'<p class="main-title">🚀 {st.session_state["biz_name"]}</p>', unsafe_allow_html=True)
st.sidebar.markdown(f"👤 Admin: **{st.session_state['user']}**")

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS", "👥 GESTION", "🔔 ALERTES", "📄 REÇUS"])

with t1:
    st.subheader("Performance Live")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Revenue Global", f"{df['Prix'].sum()} DH")
        c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        c3.metric("Relances Urgent", len(df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]))
        
        st.markdown("---")
        g1, g2 = st.columns(2)
        with g1:
            fig1 = px.bar(df, x='Service', y='Prix', color='Status', title="Revenue/Service", template="plotly_dark")
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig1, use_container_width=True)
        with g2:
            fig2 = px.pie(df, names='Service', title="Market Share", hole=0.5, template="plotly_dark")
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig2, use_container_width=True)

with t2:
    with st.expander("➕ Ajouter un Client"):
        ca, cb, cc = st.columns(3)
        with ca:
            n_nom = st.text_input("Nom Complet")
            n_phone = st.text_input("WhatsApp")
            n_email = st.text_input("Email Client")
        with cb:
            s_choice = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
            final_s = st.text_input("Préciser s-service") if s_choice == "Autre" else s_choice
            n_prix = st.number_input("Prix (DH)", min_value=0, step=5)
        with cc:
            n_deb = st.date_input("Date de Début", today)
            n_dur = st.number_input("Durée (Mois)", min_value=1, value=1)
            n_stat = st.selectbox("Status", ["Actif", "Payé", "En Attente"])
        
        if st.button("🚀 Valider l'Abonnement"):
            if n_nom and n_phone:
                n_fin = n_deb + relativedelta(months=int(n_dur))
                new_row = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), n_stat]
                c_sheet_obj.append_row(new_row)
                st.success("✅ Synchro réussie!")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Jours Restants"]
        actual_cols = [c for c in cols if c in df.columns]
        edited = st.data_editor(df[actual_cols], use_container_width=True, num_rows="dynamic", disabled=["Jours Restants", "Date Fin"])
        if st.button("💾 Sauvegarder Changes"):
            final_df = edited.drop(columns=['Jours Restants', 'Mois'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Cloud Updated!")
            st.rerun()

with t3:
    st.subheader("Relances WhatsApp 📲")
    urgent = df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            col1, col2 = st.columns([3, 1])
            icon = "🔴" if r['Jours Restants'] <= 0 else "🟠"
            col1.warning(f"{icon} **{r['Nom']}** | {r['Service']} | **{r['Jours Restants']} j**")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire le {r['Date Fin']}. On renouvelle?"
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
            col2.link_button("📲 Rappeler", wa)
    else: st.success("Tout est propre!")

with t4:
    st.subheader("Générateur de Reçu Officiel 📄")
    if not df.empty:
        sel = st.selectbox("Choisir klyan:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = (
            f"✅ *REÇU D'ABONNEMENT - {st.session_state['biz_name']}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Client:* {c['Nom']}\n"
            f"📩 *Email:* {c['Email']}\n"
            f"📺 *Service:* {c['Service']}\n"
            f"💰 *Prix:* {c['Prix']} DH\n"
            f"📅 *Début:* {c['Date Début']}\n"
            f"⌛ *Expire le:* {c['Date Fin']}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🤝 *Merci pour votre confiance !*"
        )
        st.code(reçu)
        wa_reçu = f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}"
        st.link_button(f"📲 Envoyer Reçu à {c['Nom']}", wa_reçu)

if st.sidebar.button("Se déconnecter"):
    del st.session_state["auth"]
    st.rerun()
