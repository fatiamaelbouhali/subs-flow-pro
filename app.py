import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# OMEGA STATUS: SAAS PLATFORM V6 - MULTI-TENANT
st.set_page_config(page_title="SUBS_FLOW_PRO_PLATFORM", layout="wide", page_icon="🏦")

# --- 1. CONFIGURATION MASTER (S-SAROUT DIAL FATIMA) ---
# 7etti hna l-ID dial MASTER_ADMIN s-sheet jdid
MASTER_ID = "https://docs.google.com/spreadsheets/d/1j8FOrpIcWFbF9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE/edit?gid=0" # <--- BEDDLI HADA B L-ID DIAL MASTER SHEET

conn = st.connection("gsheets", type=GSheetsConnection)

def load_master():
    return conn.read(spreadsheets=MASTER_ID, ttl=0)

# --- 2. LOGIN SYSTEM SAAS ---
if "auth" not in st.session_state:
    st.title("🏦 Plateforme de Gestion Digital")
    st.subheader("Accès Partenaires")
    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
    
    if st.button("Se Connecter"):
        m_df = load_master()
        user_row = m_df[(m_df['User'] == u_in) & (m_df['Password'] == p_in)]
        
        if not user_row.empty:
            if user_row.iloc[0]['Status'] == 'Active':
                st.session_state["auth"] = True
                st.session_state["user"] = u_in
                st.session_state["sheet_id"] = user_row.iloc[0]['Sheet_ID']
                st.rerun()
            else:
                st.error("🚫 Compte suspendu. Contactez le support.")
        else:
            st.error("❌ Identifiants incorrects.")
    st.stop()

# --- 3. LOAD DATA DIAL L-KLYAN (The Tenant) ---
CLIENT_URL = f"https://docs.google.com/spreadsheets/d/{st.session_state['sheet_id']}/edit?usp=sharing"

def load_data():
    raw = conn.read(spreadsheet=CLIENT_URL, ttl=0)
    # Anti-Error Patch (Type Force)
    if 'Email' not in raw.columns: raw['Email'] = ""
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in raw.columns: raw[c] = raw[c].astype(str).replace('nan', '')
    if 'Prix' in raw.columns: raw['Prix'] = pd.to_numeric(raw['Prix'], errors='coerce').fillna(0)
    if 'Date Fin' in raw.columns: raw['Date Fin'] = pd.to_datetime(raw['Date Fin'], errors='coerce').dt.date
    if 'Date Début' in raw.columns: raw['Date Début'] = pd.to_datetime(raw['Date Début'], errors='coerce').dt.date
    return raw

df = load_data()
today = datetime.now().date()

# --- 4. INTERFACE ---
st.sidebar.title(f"👤 {st.session_state['user']}")
if st.sidebar.button("Se déconnecter"):
    del st.session_state["auth"]
    st.rerun()

t1, t2, t3 = st.tabs(["📊 DASHBOARD", "👥 CLIENTS", "🔔 ALERTES"])

with t1:
    st.header("Financial Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"{df['Prix'].sum()} DH")
    c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
    c3.metric("Emails", len(df[df['Email'] != ""]))
    
    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Service', title="Revenue/Service"), use_container_width=True)
    with g2:
        st.plotly_chart(px.pie(df, names='Status', title="Stats Status", hole=0.5), use_container_width=True)

with t2:
    with st.expander("➕ Nouveau Client"):
        ca, cb, cc = st.columns(3)
        with ca:
            n_nom = st.text_input("Nom")
            n_phone = st.text_input("WhatsApp")
        with cb:
            n_email = st.text_input("Email")
            n_serv = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "IPTV", "Disney+", "Autre"])
        with cc:
            n_prix = st.number_input("Prix", min_value=0)
            n_dur = st.number_input("Mois", min_value=1, value=1)
        
        if st.button("🚀 Ajouter"):
            if n_nom and n_phone:
                n_fin = today + relativedelta(months=int(n_dur))
                new_r = pd.DataFrame([{"Nom": n_nom, "Phone": n_phone, "Email": n_email, "Service": n_serv, "Prix": n_prix, "Date Début": str(today), "Durée (Mois)": n_dur, "Date Fin": str(n_fin), "Status": "Actif"}])
                # Clean columns before update
                df_to_save = pd.concat([df, new_r], ignore_index=True)
                conn.update(spreadsheet=CLIENT_URL, data=df_to_save)
                st.success("Client ajouté!")
                st.rerun()

    st.markdown("---")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic", disabled=["Date Fin"])
    if st.button("💾 Sauvegarder Changes"):
        conn.update(spreadsheet=CLIENT_URL, data=edited)
        st.success("Synced!")
        st.rerun()

with t3:
    st.header("WhatsApp Rappels")
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 100)
    alerts = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not alerts.empty:
        for _, r in alerts.iterrows():
            col1, col2 = st.columns([3, 1])
            col1.write(f"👤 **{r['Nom']}** | 📺 {r['Service']} | ⏳ **{r['Days']} jours**")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire le {r['Date Fin']}. On renouvelle?"
            url = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
            col2.link_button("📲 Rappeler", url)
    else:
        st.success("Tout est clean.")




