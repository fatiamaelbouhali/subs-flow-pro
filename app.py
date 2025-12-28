import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# OMEGA STATUS: V20 - THE EMPIRE STRIKES BACK (FULL SaaS)
st.set_page_config(page_title="SUBS_FLOW_PRO_EMPIRE", layout="wide", page_icon="👑")

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

client = get_gspread_client()

# --- 1. LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.title("🏦 Plateforme Management Pro")
    u_in = st.text_input("Identifiant Business:")
    p_in = st.text_input("Mot de passe:", type="password")
    
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
                    # Get Sheet Name from Master Admin
                    st.session_state["target_sheet"] = str(match.iloc[0]['Sheet_Name']).strip()
                    st.rerun()
                else: st.error("🚫 Accès Suspendu.")
            else: st.error("❌ Identifiants incorrects.")
        except Exception as e:
            st.error(f"❌ Error Connection: {e}")
    st.stop()

# --- 2. LOAD DATA CLIENT ---
try:
    c_sheet_obj = client.open(st.session_state["target_sheet"]).sheet1
    df = pd.DataFrame(c_sheet_obj.get_all_records())
except Exception as e:
    st.error(f"❌ Impossible d'ouvrir la base: {st.session_state['target_sheet']}")
    st.code(f"Reason: {e}")
    st.stop()

# --- 3. DATA CLEANING ---
if not df.empty:
    if 'Email' not in df.columns: df['Email'] = ""
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    if 'Prix' in df.columns: df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.date

today = datetime.now().date()
st.sidebar.title(f"👤 {st.session_state['user']}")
if st.sidebar.button("Déconnexion"):
    del st.session_state["auth"]
    st.rerun()

# --- 4. UI TABS ---
t1, t2, t3, t4 = st.tabs(["📊 DASHBOARD", "👥 GESTION CLIENTS", "🔔 RAPPELS WHATSAPP", "👑 ADMIN"])

with t1:
    st.header("Financial Dashboard")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Revenue Total", f"{df['Prix'].sum()} DH")
        c2.metric("Abonnements Actifs", len(df[df['Status'] == 'Actif']))
        c3.metric("Emails Collectés", len(df[df['Email'] != ""]))
        
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Service', title="Revenue par Service"), use_container_width=True)
        with g2:
            st.plotly_chart(px.pie(df, names='Status', title="Stats Status", hole=0.5), use_container_width=True)

with t2:
    st.header("Gestion de la Base")
    with st.expander("➕ Ajouter un nouveau client"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom Complet")
        n_phone = ca.text_input("WhatsApp (ex: 2126...)")
        n_email = ca.text_input("Email")
        n_serv = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        n_prix = cb.number_input("Prix (DH)", min_value=0)
        n_dur = cc.number_input("Durée (Mois)", min_value=1, value=1)
        n_stat = cc.selectbox("Status Initial", ["Actif", "En Attente", "Payé"])
        
        if st.button("🚀 Enregistrer au Cloud"):
            if n_nom and n_phone:
                n_fin = today + relativedelta(months=int(n_dur))
                new_r = [n_nom, str(n_phone), n_email, n_serv, n_prix, str(today), n_dur, str(n_fin), n_stat]
                c_sheet_obj.append_row(new_row=new_r)
                st.success("✅ Client ajouté !")
                st.rerun()

    st.markdown("---")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder les modifications"):
        c_sheet_obj.clear()
        c_sheet_obj.update([df.columns.values.tolist()] + edited.values.tolist())
        st.success("✅ Cloud Updated!")
        st.rerun()

with t3:
    st.header("WhatsApp Smart Alerts")
    if not df.empty:
        df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 100)
        alerts = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
        if not alerts.empty:
            for _, r in alerts.iterrows():
                col1, col2 = st.columns([3, 1])
                col1.warning(f"👤 **{r['Nom']}** | 📺 {r['Service']} | ⏳ **{r['Days']} jours**")
                msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire bientôt. On renouvelle?"
                url = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
                col2.link_button("📲 Rappeler", url)
        else: st.success("Tout est à jour.")

with t4:
    st.header("👑 Advanced Control")
    admin_pwd = st.text_input("Code Admin Fatima:", type="password")
    if admin_pwd == "omega2025":
        st.write("### 💎 SaaS Insights")
        st.write(f"Kheddama dabba m3a s-Sheet: **{st.session_state['target_sheet']}**")
        st.download_button("📥 Backup Database (CSV)", df.to_csv(index=False), "backup.csv", "text/csv")
    elif admin_pwd:
        st.error("Accès refusé.")
