import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V33 - THE FINAL PERFECTION (ZERO BUGS)
st.set_page_config(page_title="SUBS_FLOW_EMPIRE", layout="wide", page_icon="👑")

# ⚡ THE NUCLEAR UI FIX (FORCE VISIBILITY)
st.markdown("""
    <style>
    /* Force ga3 l-ktaba t-welli BIDA 100% */
    .stApp, .stMarkdown, label, div, span, p { color: #FFFFFF !important; }
    
    /* Metrics High Visibility */
    div[data-testid="stMetricValue"] > div { color: #00FFCC !important; font-size: 40px !important; font-weight: 900 !important; }
    div[data-testid="stMetricLabel"] p { color: #FFFFFF !important; font-size: 18px !important; font-weight: bold !important; opacity: 1 !important; }

    /* Input Fields Fix - White Text on Dark Background */
    input, select, textarea { color: #FFFFFF !important; background-color: #262730 !important; }
    
    /* Expander Fix */
    .streamlit-expanderHeader { background-color: #1f2937 !important; border: 1px solid #3b82f6 !important; }

    /* Banner dial l-Boss */
    .boss-banner {
        background: #00d2ff;
        background: -webkit-linear-gradient(to right, #3a7bd5, #00d2ff);
        background: linear-gradient(to right, #3a7bd5, #00d2ff);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: #000000 !important;
        font-size: 45px;
        font-weight: 900;
        margin-bottom: 25px;
        border: 2px solid #ffffff;
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
    st.title("🛡️ SaaS Login Portal")
    u_in = st.text_input("Username:")
    p_in = st.text_input("Password:", type="password")
    if st.button("Access"):
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
                else: st.error("🚫 Access Blocked.")
            else: st.error("❌ Credentials Error.")
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
# BANNER MHAYBA
st.markdown(f'<div class="boss-banner">🚀 {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 DASHBOARD", "👥 GESTION", "🔔 ALERTES", "📄 REÇUS"])

with t1:
    st.subheader("Performance Live")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Revenue Global", f"{df['Prix'].sum()} DH")
        c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        c3.metric("Relances (≤3j)", len(df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]))
        
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="plotly_dark", title="Sales/Service"), use_container_width=True)
        with g2:
            st.plotly_chart(px.pie(df, names='Service', hole=0.6, template="plotly_dark", title="Market Distribution"), use_container_width=True)

with t2:
    st.subheader("Database")
    with st.expander("➕ AJOUTER UN NOUVEAU CLIENT", expanded=False):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom Complet")
        n_phone = ca.text_input("WhatsApp (212...)")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Préciser le service") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix (DH)", min_value=0)
        n_dur = cc.number_input("Durée (Mois)", min_value=1, value=1)
        if st.button("💾 Enregistrer"):
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
            col_l.write(f"{icon} **{r['Nom']}** | {r['Service']} | **{r['Jours Restants']} j**")
            wa = f"https://wa.me/{r['Phone']}?text=Bonjour {r['Nom']}, renouvellement {r['Service']}? Expire le {r['Date Fin']}"
            col_r.link_button("📲 Rappeler", wa)
    else: st.success("Aucun retard.")

with t4:
    st.subheader("Générateur de Reçu 📄")
    if not df.empty:
        sel = st.selectbox("Choisir klyan:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"*REÇU - {st.session_state['biz_name']}*\n\n👤 Client: {c['Nom']}\n📩 Email: {c['Email']}\n📺 Service: {c['Service']}\n💰 Prix: {c['Prix']} DH\n⌛ Expire le: {c['Date Fin']}\n\n*Merci de votre confiance !*"
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

if st.sidebar.button("Déconnexion"):
    st.session_state.clear()
    st.rerun()
