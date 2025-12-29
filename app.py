import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: V27 - MAXIMUM VISIBILITY 
st.set_page_config(page_title="SUBS_FLOW_PRO_V27", layout="wide", page_icon="💎")

# ⚡ CSS DIAL S-SAYTARA (FORCE WHITE LABELS & NEON NUMBERS)
st.markdown("""
    <style>
    /* Headers & Text */
    h1, h2, h3, p, span, label { color: #FFFFFF !important; }
    
    /* Metrics Box */
    div[data-testid="stMetric"] {
        background-color: #1f2937 !important;
        border: 2px solid #3b82f6 !important;
        padding: 20px !important;
        border-radius: 15px !important;
    }
    
    /* Neon Green for Numbers */
    div[data-testid="stMetricValue"] > div {
        color: #00ff9d !important;
        font-size: 40px !important;
        font-weight: 900 !important;
    }
    
    /* Forced White for Labels (Revenue Global, etc) */
    div[data-testid="stMetricLabel"] p {
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF !important;
        font-weight: bold !important;
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
    st.title("🏦 SaaS Login")
    u_in = st.text_input("Username:")
    p_in = st.text_input("Password:", type="password")
    if st.button("Se Connecter"):
        try:
            m_sheet = client.open("Master_Admin").sheet1
            m_df = pd.DataFrame(m_sheet.get_all_records())
            match = m_df[(m_df['User'].astype(str).str.strip() == str(u_in).strip()) & 
                         (m_df['Password'].astype(str).str.strip() == str(p_in).strip())]
            if not match.empty:
                if match.iloc[0]['Status'] == 'Active':
                    st.session_state["auth"] = True
                    st.session_state["user"] = u_in
                    # Fallback ila kant smiya khawya f master
                    st.session_state["biz_name"] = str(match.iloc[0]['Business_Name']).strip() if match.iloc[0]['Business_Name'] else f"EMPIRE {u_in.upper()}"
                    st.session_state["sheet_name"] = str(match.iloc[0]['Sheet_Name']).strip()
                    st.rerun()
                else: st.error("🚫 Bloqué.")
            else: st.error("❌ Erreur Login.")
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
st.markdown(f"# 🚀 {st.session_state['biz_name']}")
st.sidebar.write(f"Admin: **{st.session_state['user']}**")

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS", "👥 GESTION", "🔔 ALERTES", "📄 REÇUS"])

with t1:
    st.header("📈 Financial Performance")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Revenue Global", f"{df['Prix'].sum()} DH")
        c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        c3.metric("Alertes (≤3j)", len(df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]))
        
        st.markdown("---")
        g1, g2 = st.columns(2)
        with g1:
            fig1 = px.bar(df, x='Service', y='Prix', color='Status', title="Revenue/Service", template="plotly_dark")
            fig1.update_layout(font=dict(color="white"))
            st.plotly_chart(fig1, use_container_width=True)
        with g2:
            fig2 = px.pie(df, names='Service', title="Market Share", hole=0.5, template="plotly_dark")
            fig2.update_layout(font=dict(color="white"))
            st.plotly_chart(fig2, use_container_width=True)

with t2:
    with st.expander("➕ Ajouter un Client"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom Complet")
        n_phone = ca.text_input("WhatsApp")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Autre"])
        final_s = cb.text_input("Préciser") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix", min_value=0)
        n_dur = cc.number_input("Durée (Mois)", min_value=1, value=1)
        if st.button("🚀 Valider l'Abonnement"):
            if n_nom and n_phone:
                n_fin = today + relativedelta(months=int(n_dur))
                c_sheet_obj.append_row([n_nom, str(n_phone), n_email, final_s, n_prix, str(today), n_dur, str(n_fin), "Actif"])
                st.success("✅ Synced!")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Jours Restants"]
        actual_cols = [c for c in cols if c in df.columns]
        edited = st.data_editor(df[actual_cols], use_container_width=True, num_rows="dynamic", disabled=["Jours Restants", "Date Fin"])
        if st.button("💾 Sauvegarder Changes"):
            final_df = edited.drop(columns=['Jours Restants'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Database Updated!")
            st.rerun()

with t3:
    st.header("Relances WhatsApp 📲")
    urgent = df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            col1, col2 = st.columns([3, 1])
            icon = "🔴" if r['Jours Restants'] <= 0 else "🟠"
            col1.warning(f"{icon} **{r['Nom']}** | {r['Service']} | **{r['Jours Restants']} j**")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire bientôt. On renouvelle?"
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
            col2.link_button("📲 Rappeler", wa)
    else: st.success("Aucune relance.")

with t4:
    st.header("Générateur de Reçu Officiel 📄")
    if not df.empty:
        sel = st.selectbox("Choisir klyan:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"*REÇU - {st.session_state['biz_name']}*\n\n👤 Client: {c['Nom']}\n📩 Email: {c['Email']}\n📺 Service: {c['Service']}\n💰 Prix: {c['Prix']} DH\n⌛ Expire: {c['Date Fin']}\n\n*Merci de votre confiance !*"
        st.code(reçu)
        wa_reçu = f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}"
        st.link_button(f"📲 Envoyer Reçu à {c['Nom']}", wa_reçu)

if st.sidebar.button("Se déconnecter"):
    del st.session_state["auth"]
    st.rerun()
