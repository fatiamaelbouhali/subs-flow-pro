import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V30 - FINAL VISIBILITY OVERLOAD
st.set_page_config(page_title="SUBS_FLOW_PRO_V30", layout="wide", page_icon="🏦")

# ⚡ CSS DIAL S-SAYTARA - CLEAN & HIGH CONTRAST
st.markdown("""
    <style>
    /* Reset ga3 l-ktaba l-asasiya */
    .stApp { color: #ffffff !important; }
    h1, h2, h3, h4, h5, h6, p, span, label { color: #ffffff !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Metrics Box - Professional Neon Style */
    div[data-testid="stMetric"] {
        background-color: #1a1c24 !important;
        border: 2px solid #00d2ff !important;
        padding: 20px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 210, 255, 0.2);
    }
    
    /* Neon Green dial l-Ar9am */
    div[data-testid="stMetricValue"] > div {
        color: #00ff9d !important;
        font-size: 42px !important;
        font-weight: 900 !important;
    }
    
    /* White Labels (Revenu, etc) - NADIYIN */
    div[data-testid="stMetricLabel"] p {
        color: #ffffff !important;
        font-size: 18px !important;
        font-weight: bold !important;
        letter-spacing: 1px !important;
    }

    /* Tabs Visibility */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #262730 !important;
        color: #ffffff !important;
        border-radius: 5px !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00d2ff !important;
        color: #000000 !important;
    }

    /* Business Title Banner */
    .biz-banner {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        padding: 20px;
        border-radius: 10px;
        color: #000000 !important;
        font-size: 40px;
        font-weight: 900;
        text-align: center;
        margin-bottom: 30px;
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
    st.title("🛡️ SaaS Management Login")
    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
    if st.button("Unleash the Power"):
        try:
            m_sheet = client.open("Master_Admin").sheet1
            m_df = pd.DataFrame(m_sheet.get_all_records())
            match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & 
                         (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
            if not match.empty:
                if match.iloc[0]['Status'] == 'Active':
                    st.session_state["auth"] = True
                    st.session_state["user"] = u_in
                    # Fallback Business Name
                    b_name = str(match.iloc[0]['Business_Name']).strip()
                    st.session_state["biz_name"] = b_name if b_name != 'nan' and b_name != "" else f"{u_in.upper()} DIGITAL"
                    st.session_state["sheet_name"] = str(match.iloc[0]['Sheet_Name']).strip()
                    st.rerun()
                else: st.error("🚫 Access Suspended.")
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
    df['Jours Restants'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df.loc[(df['Jours Restants'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 3. THE INTERFACE ---
# FORCE BRANDING WITH BANNER
st.markdown(f'<div class="biz-banner">🚀 {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS", "👥 GESTION", "🔔 ALERTES", "📄 REÇUS"])

with t1:
    st.subheader("Business Metrics Overview")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Revenue Global", f"{df['Prix'].sum()} DH")
        c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        c3.metric("Relances (≤3j)", len(df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]))
        
        st.markdown("---")
        g1, g2 = st.columns(2)
        with g1:
            fig1 = px.bar(df, x='Service', y='Prix', color='Status', template="plotly_dark", title="Revenue / Service")
            fig1.update_layout(font=dict(color="white"))
            st.plotly_chart(fig1, use_container_width=True)
        with g2:
            fig2 = px.pie(df, names='Service', hole=0.6, template="plotly_dark", title="Répartition Services")
            fig2.update_layout(font=dict(color="white"))
            st.plotly_chart(fig2, use_container_width=True)

with t2:
    st.subheader("Database Management")
    with st.expander("➕ Ajouter un nouveau client"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom Complet")
        n_phone = ca.text_input("WhatsApp")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Détails Service") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix", min_value=0)
        n_dur = cc.number_input("Mois", min_value=1, value=1)
        if st.button("🚀 Enregistrer au Cloud"):
            if n_nom and n_phone:
                n_fin = today + relativedelta(months=int(n_dur))
                c_sheet_obj.append_row([n_nom, str(n_phone), n_email, final_s, n_prix, str(today), n_dur, str(n_fin), "Actif"])
                st.success("✅ Synced!")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Status", "Jours Restants", "Date Fin"]
        actual_cols = [c for c in cols if c in df.columns]
        edited = st.data_editor(df[actual_cols], use_container_width=True, num_rows="dynamic", disabled=["Jours Restants", "Date Fin"])
        if st.button("💾 Sauvegarder modifications"):
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
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire bientôt ({r['Date Fin']}). On renouvelle?"
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
            col_r.link_button("📲 Rappeler", wa)
    else: st.success("Aucune relance urgente.")

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
            f"📅 *Fin:* {c['Date Fin']}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🤝 *Merci pour votre confiance !*"
        )
        st.code(reçu)
        wa_reçu = f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}"
        st.link_button(f"📲 Envoyer Reçu via WhatsApp", wa_reçu)

st.sidebar.button("Déconnexion", on_click=lambda: st.session_state.clear())
