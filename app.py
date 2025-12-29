import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V40 - THE ADAPTIVE EMPIRE (CLEAN & PRO)
st.set_page_config(page_title="EMPIRE_V40", layout="wide", page_icon="📈")

# ⚡ CSS SGHIR GHIR BACH N-ZIDU L-HIBA (MA-KAY-KHROWEDCH L-ALWAN)
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        border: 1px solid #3b82f6;
        padding: 15px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: bold;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# MASTER ADMIN ID
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=scope))

client = get_gspread_client()

# --- 1. LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.title("🛡️ Accès Management Pro")
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
                    b_name = str(match.iloc[0]['Business_Name']).strip()
                    st.session_state["biz_name"] = b_name if b_name != 'nan' and b_name != "" else f"{u_in.upper()} PRO"
                    st.session_state["sheet_name"] = str(match.iloc[0]['Sheet_Name']).strip()
                    st.rerun()
                else: st.error("🚫 Accès Bloqué.")
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

# --- 3. CLEANING & LOGIC ---
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce')
    df['Jours Restants'] = df['Date Fin'].apply(lambda x: (x.date() - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = df['Date Fin'].dt.strftime('%Y-%m-%d').fillna("NON DÉFINI")
    df.loc[(df['Jours Restants'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 4. THE UI ---
st.title(f"🚀 {st.session_state['biz_name']}")
st.markdown("---")

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS", "👥 GESTION", "🔔 RELANCES", "📄 REÇUS"])

# TAB 1: ANALYTICS (NADI)
with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("✅ CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("🚨 RELANCES (3j)", len(df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]))

        st.markdown("### 📈 Performance par Service")
        g1, g2 = st.columns([2, 1])
        with g1:
            fig1 = px.bar(df.groupby('Service')['Prix'].sum().reset_index(), x='Service', y='Prix', title="Revenue per Service")
            st.plotly_chart(fig1, use_container_width=True)
        with g2:
            fig2 = px.pie(df, names='Status', title="Stats Status", hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)

        # 💡 LE RÉSUMÉ PAR SERVICE (THE BIG FEATURE)
        st.markdown("### 📊 Résumé du Business")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Total Clients', 'Chiffre d\'Affaires (DH)']
        st.dataframe(summary, use_container_width=True)
    else:
        st.info("Aucune donnée.")

# TAB 2: GESTION
with t2:
    with st.expander("➕ AJOUTER UN NOUVEAU CLIENT"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom")
        n_phone = ca.text_input("WhatsApp")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Préciser") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix", min_value=0)
        n_dur = cc.number_input("Mois", min_value=1, value=1)
        if st.button("💾 Enregistrer"):
            if n_nom and n_phone:
                n_fin = today + relativedelta(months=int(n_dur))
                c_sheet_obj.append_row([n_nom, str(n_phone), n_email, final_s, n_prix, str(today), n_dur, str(n_fin), "Actif"])
                st.success("✅ Synced!")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Status", "Jours Restants", "Date_Display"]
        edited = st.data_editor(df[cols], use_container_width=True, num_rows="dynamic", disabled=["Jours Restants", "Date_Display"])
        if st.button("💾 Valider modifications"):
            final_df = edited.drop(columns=['Jours Restants', 'Date_Display'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Database Updated!")
            st.rerun()

# TAB 3: ALERTS
with t3:
    st.subheader("Relances WhatsApp 📲")
    urgent = df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            col_l, col_r = st.columns([3, 1])
            icon = "🔴" if r['Jours Restants'] <= 0 else "🟠"
            col_l.warning(f"{icon} **{r['Nom']}** | {r['Service']} | **{r['Jours Restants']} j** (Expire: {r['Date_Display']})")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire bientot. On renouvelle?"
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
            col_r.link_button("📲 Rappeler", wa)
    else: st.success("Aucune relance.")

# TAB 4: REÇUS
with t4:
    if not df.empty:
        sel = st.selectbox("Choisir klyan:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"*REÇU - {st.session_state['biz_name']}*\n👤 Client: {c['Nom']}\n📺 Service: {c['Service']}\n💰 Prix: {c['Prix']} DH\n⌛ Expire: {c['Date_Display']}\n*Merci !*"
        st.code(reçu)
        st.link_button("📲 WhatsApp Direct", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

st.sidebar.button("Déconnexion", on_click=lambda: st.session_state.clear())
