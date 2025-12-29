import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V41 - BULLETPROOF ARCHITECTURE
st.set_page_config(page_title="EMPIRE_PRO_V41", layout="wide", page_icon="📈")

# ⚡ CSS - CLEAN & ADAPTIVE
st.markdown("""
    <style>
    div[data-testid="stMetric"] { border: 1px solid #3b82f6; padding: 15px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; font-size: 18px; }
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
    st.title("🛡️ Access Pro Management")
    u_in = st.text_input("Username:")
    p_in = st.text_input("Password:", type="password")
    if st.button("Unlock System"):
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
            else: st.error("❌ Invalid Credentials.")
        except Exception as e: st.error(f"Error Login: {e}")
    st.stop()

# --- 2. LOAD DATA ---
try:
    c_sheet_obj = client.open(st.session_state["sheet_name"]).sheet1
    data_raw = c_sheet_obj.get_all_records()
    df = pd.DataFrame(data_raw)
except:
    st.error(f"Base '{st.session_state['sheet_name']}' introuvable.")
    st.stop()

# --- 3. THE BULLETPROOF COLUMN PATCH ---
required_cols = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status"]
if not df.empty:
    # Logic bach n-Mapping l-columns wakha t-koun smiya mbeddla chwiya
    for col in required_cols:
        if col not in df.columns:
            # Check if it exists with extra spaces or different case
            found = False
            for actual_col in df.columns:
                if col.strip().lower() == actual_col.strip().lower():
                    df.rename(columns={actual_col: col}, inplace=True)
                    found = True
                    break
            if not found:
                df[col] = "" # Create empty if not found at all

    # Cleaning & Types
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        df[c] = df[c].astype(str).replace('nan', '')
    
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce')
    
    today = datetime.now().date()
    df['Jours Restants'] = df['Date Fin'].apply(lambda x: (x.date() - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = df['Date Fin'].dt.strftime('%Y-%m-%d').fillna("NON DÉFINI")
    df.loc[(df['Jours Restants'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 4. THE UI ---
st.title(f"🚀 {st.session_state['biz_name']}")
st.markdown("---")

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS", "👥 CLIENTS", "🔔 RELANCES", "📄 REÇUS"])

# TAB 1: ANALYTICS
with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("✅ CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("🚨 RELANCES (3j)", len(df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]))

        g1, g2 = st.columns([2, 1])
        with g1:
            st.plotly_chart(px.bar(df.groupby('Service')['Prix'].sum().reset_index(), x='Service', y='Prix', title="Revenue per Service"), use_container_width=True)
        with g2:
            st.plotly_chart(px.pie(df, names='Status', title="Stats Distribution", hole=0.4), use_container_width=True)

        st.markdown("### 📊 Résumé Business")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Total Clients', 'Revenue (DH)']
        st.dataframe(summary, use_container_width=True)

# TAB 2: GESTION
with t2:
    with st.expander("➕ AJOUTER UN NOUVEAU CLIENT"):
        ca, cb, cc = st.columns(3)
        with ca:
            n_nom = st.text_input("Nom")
            n_phone = st.text_input("WhatsApp")
        with cb:
            n_email = st.text_input("Email")
            s_list = ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"]
            s_choice = st.selectbox("Service", s_list)
            final_s = st.text_input("Préciser") if s_choice == "Autre" else s_choice
        with cc:
            n_prix = st.number_input("Prix", min_value=0)
            n_dur = st.number_input("Durée (Mois)", min_value=1, value=1)
        
        if st.button("🚀 Enregistrer"):
            if n_nom and n_phone:
                n_fin = today + relativedelta(months=int(n_dur))
                new_row = [n_nom, str(n_phone), n_email, final_s, n_prix, str(today), n_dur, str(n_fin), "Actif"]
                c_sheet_obj.append_row(new_row)
                st.success("✅ Synchro OK!")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Status", "Jours Restants", "Date_Display"]
        # On n'affiche que ce qu'on a pour être sur
        display_cols = [c for c in cols if c in df.columns]
        edited = st.data_editor(df[display_cols], use_container_width=True, num_rows="dynamic", disabled=["Jours Restants", "Date_Display"])
        if st.button("💾 Sauvegarder modifications"):
            final_df = edited.drop(columns=['Jours Restants', 'Date_Display'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Google Sheets Synced!")
            st.rerun()

# TAB 3: RELANCES
with t3:
    st.subheader("Relances WhatsApp 📲")
    urgent = df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            col_l, col_r = st.columns([3, 1])
            icon = "🔴" if r['Jours Restants'] <= 0 else "🟠"
            col_l.warning(f"{icon} **{r['Nom']}** | {r['Service']} | **{r['Jours Restants']} j**")
            wa = f"https://wa.me/{r['Phone']}?text=Bonjour {r['Nom']}, renouvellement {r['Service']}? Expire le {r['Date_Display']}"
            col_r.link_button("📲 Rappeler", wa)
    else: st.success("Tout est à jour.")

# TAB 4: REÇUS
with t4:
    if not df.empty:
        sel = st.selectbox("Choisir client:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"*REÇU - {st.session_state['biz_name']}*\n👤 Client: {c['Nom']}\n📺 Service: {c['Service']}\n💰 Prix: {c['Prix']} DH\n⌛ Expire le: {c['Date_Display']}\n\n*Merci !*"
        st.code(reçu)
        st.link_button("📲 WhatsApp Direct", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

st.sidebar.button("Déconnexion", on_click=lambda: st.session_state.clear())
