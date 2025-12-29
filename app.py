import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V47 - COMMANDER EDITION (CRASH FIXED)
st.set_page_config(page_title="SUBS_FLOW_EMPIRE_V47", layout="wide", page_icon="🏦")

# ⚡ CSS LUXURY
st.markdown("""
    <style>
    div[data-testid="stMetric"] { border: 1px solid #3b82f6; padding: 15px; border-radius: 12px; background: rgba(0,0,0,0.2); }
    .stTabs [data-baseweb="tab"] { font-weight: bold; font-size: 18px; }
    .boss-banner {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        padding: 25px; border-radius: 12px; color: white !important;
        text-align: center; font-size: 38px; font-weight: 900;
        margin-bottom: 25px; border: 2px solid #ffffff;
    }
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
    st.title("🛡️ Secure SaaS Login")
    u_in = st.text_input("Username:")
    p_in = st.text_input("Password:", type="password")
    if st.button("Unlock"):
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
            else: st.error("Identifiants incorrects.")
        except Exception as e: st.error(f"Error Master: {e}")
    st.stop()

# --- 2. LOAD DATA ---
try:
    c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
    df = pd.DataFrame(c_sheet_obj.get_all_records())
except:
    st.error("Sheet introuvable.")
    st.stop()

today = datetime.now().date()
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = pd.to_datetime(df['Date Fin']).dt.strftime('%Y-%m-%d').fillna("N/A")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 3. UI ---
st.markdown(f'<div class="boss-banner">🚀 {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 DASHBOARD", "👥 GESTION", "🔔 RAPPELS PRO", "📄 REÇUS"])

with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("RAPPELS URGENTS", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
        
        st.markdown("### 📋 Résumé par Service")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'Total (DH)']
        st.dataframe(summary, use_container_width=True)
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="plotly_dark"), use_container_width=True)

with t2:
    with st.expander("➕ AJOUTER CLIENT"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom")
        n_phone = ca.text_input("WhatsApp (ex: 212...)")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Détails") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix", min_value=0)
        n_dur = cc.number_input("Mois", min_value=1, value=1)
        if st.button("🚀 Valider"):
            if n_nom and n_phone:
                n_fin = today + relativedelta(months=int(n_dur))
                c_sheet_obj.append_row([n_nom, str(n_phone), n_email, final_s, n_prix, str(today), n_dur, str(n_fin), "Actif"])
                st.success("✅ Synced!")
                st.rerun()

    st.markdown("---")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder les changements"):
        final_df = edited.drop(columns=['Days', 'Date_Display'], errors='ignore')
        c_sheet_obj.clear()
        c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
        st.success("✅ Cloud Updated!")
        st.rerun()

# ==========================================
# TAB 3: RAPPELS PRO (CRASH FIXED)
# ==========================================
with t3:
    st.subheader("🔔 Centre de Relance WhatsApp")
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    
    if not urgent.empty:
        st.info(f"💡 **Action Immédiate :** {len(urgent)} client(s) arrivent à expiration.")
        
        for _, r in urgent.iterrows():
            with st.container():
                c_l, c_r = st.columns([3, 1])
                icon = "🔴" if r['Days'] <= 0 else "🟠"
                c_l.warning(f"{icon} **{r['Nom']}** | 📺 {r['Service']} | ⏳ **{r['Days']} jours restants**")
                
                # 💡 NEW PROFESSIONAL MESSAGE LOGIC
                biz_name = st.session_state['biz_name']
                pro_msg = (
                    f"⚠️ *RAPPEL D'EXPIRATION - {biz_name}*\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"Bonjour *{r['Nom']}*,\n\n"
                    f"Nous vous informons que votre abonnement *{r['Service']}* arrive à échéance le *{r['Date_Display']}*.\n\n"
                    f"👉 Pour éviter toute coupure de service, merci de procéder au renouvellement.\n\n"
                    f"Nous restons à votre disposition pour toute question.\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"🤝 *Merci pour votre confiance !*"
                )
                
                wa_url = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(pro_msg)}"
                c_r.link_button("📲 Envoyer Rappel", wa_url)
                st.markdown("---")
    else:
        st.success("Ga3 l-klyane m-rglin 100%. Nadi!")

with t4:
    if not df.empty:
        sel = st.selectbox("Client pour reçu:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = (
            f"✅ *REÇU DE PAIEMENT - {st.session_state['biz_name']}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 Client: *{c['Nom']}*\n"
            f"📺 Service: *{c['Service']}*\n"
            f"💰 Prix: *{c['Prix']} DH*\n"
            f"⌛ Date d'Expiration: *{c['Date_Display']}*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🤝 *Merci pour votre confiance !*"
        )
        st.code(reçu)
        st.link_button("📲 Envoyer Reçu via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

st.sidebar.button("Déconnexion", on_click=lambda: st.session_state.clear())
