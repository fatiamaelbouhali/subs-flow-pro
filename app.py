import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px
import webbrowser # Bach n-7ello les onglets dial WhatsApp

# SYSTEM STATUS: OMEGA V43 - BULK WHATSAPP AUTOMATION
st.set_page_config(page_title="SUBS_FLOW_EMPIRE_V43", layout="wide", page_icon="🤖")

# ⚡ CSS LUXURY
st.markdown("""
    <style>
    .stMetric { border: 1px solid #00ffcc; padding: 15px; border-radius: 15px; background: #111; }
    .auto-btn { background-color: #25d366 !important; color: white !important; font-weight: bold; }
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
    st.title("🏦 Enterprise SaaS Gateway")
    u_in = st.text_input("Business ID:")
    p_in = st.text_input("Access Key:", type="password")
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
                    st.session_state["biz_name"] = str(match.iloc[0]['Business_Name']).strip()
                    st.session_state["sheet_name"] = str(match.iloc[0]['Sheet_Name']).strip()
                    st.rerun()
            else: st.error("Access Denied.")
        except Exception as e: st.error(f"Error: {e}")
    st.stop()

# --- 2. LOAD DATA ---
try:
    c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
    df = pd.DataFrame(c_sheet_obj.get_all_records())
except:
    st.error("Database connection lost.")
    st.stop()

today = datetime.now().date()

# --- 3. LOGIC ---
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce')
    df['Days'] = df['Date Fin'].apply(lambda x: (x.date() - today).days if pd.notnull(x) else 100)
    df['Date_Display'] = df['Date Fin'].dt.strftime('%Y-%m-%d').fillna("NON DÉFINI")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 4. INTERFACE ---
st.header(f"🚀 {st.session_state['biz_name']}")

t1, t2, t3, t4 = st.tabs(["📊 DASHBOARD", "👥 GESTION", "🤖 AUTO-RAPPELS", "📄 REÇUS"])

with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("ALERTES", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="plotly_dark"), use_container_width=True)

with t2:
    with st.expander("➕ AJOUTER CLIENT"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom")
        n_phone = ca.text_input("WhatsApp")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Détails") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix", min_value=0)
        n_dur = cc.number_input("Mois", min_value=1, value=1)
        if st.button("💾 Sauvegarder"):
            if n_nom and n_phone:
                n_fin = today + relativedelta(months=int(n_dur))
                c_sheet_obj.append_row([n_nom, str(n_phone), n_email, final_s, n_prix, str(today), n_dur, str(n_fin), "Actif"])
                st.success("Synced!")
                st.rerun()

    st.markdown("---")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder modifications"):
        final_df = edited.drop(columns=['Days', 'Date_Display'], errors='ignore')
        c_sheet_obj.clear()
        c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
        st.success("Cloud Updated!")
        st.rerun()

# ==========================================
# TAB 3: AUTO-RAPPELS (THE MAGIC)
# ==========================================
with t3:
    st.subheader("🤖 WhatsApp Automation Center")
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    
    if not urgent.empty:
        st.info(f"3ndek {len(urgent)} rappel(s) dabba.")
        
        # 💡 BULK SEND BUTTON
        if st.button("🚀 TIRER TOUS LES RAPPELS (Bulk Send)"):
            st.warning("Préparez-vous: Had l-bouton ghadi i-7el lik les onglets dial WhatsApp wa7ed b wa7ed.")
            for _, r in urgent.iterrows():
                msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire le {r['Date_Display']}. On renouvelle?"
                wa_url = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
                # Hna l-mou3ijiza: kat-7el ga3 l-links f de9a wa7da
                st.write(f"S-tiri dial: {r['Nom']}...")
                st.markdown(f'<meta http-equiv="refresh" content="0;URL={wa_url}">', unsafe_allow_html=True)
        
        st.markdown("---")
        # Individual list
        for _, r in urgent.iterrows():
            c_l, c_r = st.columns([3, 1])
            c_l.warning(f"👤 {r['Nom']} | {r['Service']} | **{r['Days']} jours**")
            wa_link = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(f'Bonjour {r[0]}, renouvellement?')}"
            c_r.link_button("📲 Tirer", wa_link)
    else:
        st.success("Ga3 l-klyane m-rglin!")

with t4:
    if not df.empty:
        sel = st.selectbox("Client pour reçu:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"*REÇU - {st.session_state['biz_name']}*\n👤 Client: {c['Nom']}\n📺 Service: {c['Service']}\n💰 Prix: {c['Prix']} DH\n⌛ Expire: {c['Date_Display']}\n*Merci !*"
        st.code(reçu)
        st.link_button("📲 Envoyer Reçu", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

if st.sidebar.button("Déconnexion"):
    st.session_state.clear()
    st.rerun()
