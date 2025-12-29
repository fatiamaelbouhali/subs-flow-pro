import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V29 - MAXIMUM CONTRAST & FORCE BRANDING
st.set_page_config(page_title="SUBS_FLOW_PRO_V29", layout="wide", page_icon="💎")

# ⚡ CSS DYAL L-M3ALLMIN (FORCE COLORS)
st.markdown("""
    <style>
    /* Force ga3 l-ktaba t-welli b l-بيض (Pure White) */
    html, body, [class*="st-"] {
        color: #ffffff !important;
    }
    
    /* Metrics Box - Dark & Pro */
    div[data-testid="stMetric"] {
        background-color: #1a1c24 !important;
        border-left: 5px solid #00d2ff !important;
        padding: 20px !important;
        border-radius: 10px !important;
    }
    
    /* Neon Numbers */
    div[data-testid="stMetricValue"] > div {
        color: #00ffcc !important;
        font-size: 38px !important;
        font-weight: 800 !important;
    }
    
    /* Labels (Revenu, Clients, etc) - FORCE VISIBILITY */
    div[data-testid="stMetricLabel"] > div > p {
        color: #ffffff !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        opacity: 1 !important;
    }

    /* Tabs Bold */
    .stTabs [data-baseweb="tab"] {
        font-size: 18px !important;
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
    st.title("🛡️ SaaS Login")
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
                    st.session_state["auth"] = True
                    st.session_state["user"] = u_in
                    # Force Business Name
                    b_name = str(match.iloc[0]['Business_Name']).strip()
                    st.session_state["biz_name"] = b_name if b_name != 'nan' and b_name != "" else f"EMPIRE {u_in.upper()}"
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

# --- 3. INTERFACE ---
# Title FORCE: Impossible t-ghletti fih dabba
st.title(f"🚀 {st.session_state['biz_name']}")
st.markdown("---")

t1, t2, t3, t4 = st.tabs(["📊 PERFORMANCE", "👥 GESTION", "🔔 RELANCES", "📄 REÇUS"])

with t1:
    st.subheader("Business Metrics")
    if not df.empty:
        # Metrics b l-Contrast l-kbiir
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Revenue Global", value=f"{df['Prix'].sum()} DH")
        m2.metric(label="Clients Actifs", value=len(df[df['Status'] == 'Actif']))
        m3.metric(label="Relances Urgent", value=len(df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]))
        
        st.markdown("---")
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="plotly_dark", title="Money/Service"), use_container_width=True)
        with g2:
            st.plotly_chart(px.pie(df, names='Service', hole=0.6, template="plotly_dark", title="Market Share"), use_container_width=True)

with t2:
    with st.expander("➕ Nouveau Client"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom")
        n_phone = ca.text_input("WhatsApp")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Préciser s-service") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix", min_value=0)
        n_dur = cc.number_input("Durée (Mois)", min_value=1, value=1)
        if st.button("🚀 Enregistrer"):
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
        if st.button("💾 Sauvegarder modifications"):
            final_df = edited.drop(columns=['Jours Restants'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Cloud Updated!")
            st.rerun()

with t3:
    st.subheader("Relances WhatsApp 📲")
    urgent = df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            col_l, col_r = st.columns([3, 1])
            icon = "🔴" if r['Jours Restants'] <= 0 else "🟠"
            col_l.warning(f"{icon} **{r['Nom']}** | {r['Service']} | **{r['Jours Restants']} j**")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire le {r['Date Fin']}. On renouvelle?"
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
            col_r.link_button("📲 Rappeler", wa)
    else: st.success("Aucune relance.")

with t4:
    st.subheader("Générateur de Reçu 📄")
    if not df.empty:
        sel = st.selectbox("Choisir klyan:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = (
            f"✅ *REÇU D'ABONNEMENT - {st.session_state['biz_name']}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Client:* {c['Nom']}\n"
            f"📺 *Service:* {c['Service']}\n"
            f"💰 *Prix:* {c['Prix']} DH\n"
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
