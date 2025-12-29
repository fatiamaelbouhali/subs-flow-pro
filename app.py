import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V35 - THE COMPLETE EMPIRE (ALL FIELDS RESTORED)
st.set_page_config(page_title="SUBS_FLOW_PRO_V35", layout="wide", page_icon="🏦")

# ID DIAL MASTER ADMIN
MASTER_ID = "1j8FOrpIcWfBf9UJcBRP1BpY4JJiCx0cUTEJ53qHuuWE"

def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["connections"]["gsheets"]
    return gspread.authorize(Credentials.from_service_account_info(creds_dict, scopes=scope))

client = get_gspread_client()

# --- 1. LOGIN SYSTEM ---
if "auth" not in st.session_state:
    st.title("🛡️ SaaS Empire Login")
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
                    b_name = str(match.iloc[0]['Business_Name']).strip()
                    st.session_state["biz_name"] = b_name if b_name != 'nan' and b_name != "" else f"{u_in.upper()} PRO"
                    st.session_state["sheet_name"] = str(match.iloc[0]['Sheet_Name']).strip()
                    st.rerun()
                else: st.error("🚫 Accès suspendu.")
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

# --- 3. LOGIC & CLEANING ---
if not df.empty:
    if 'Email' not in df.columns: df['Email'] = ""
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Durée (Mois)'] = pd.to_numeric(df['Durée (Mois)'], errors='coerce').fillna(1)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.date
    
    # 💡 CALC: Jours Restants
    df['Jours Restants'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df.loc[(df['Jours Restants'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 4. INTERFACE ---
st.header(f"🚀 {st.session_state['biz_name']}")
st.markdown("---")

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS", "👥 CLIENTS", "🔔 ALERTES", "📄 REÇUS"])

with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Revenue Global", f"{df['Prix'].sum()} DH")
        c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        c3.metric("Relances Urgent", len(df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]))
        
        g1, g2 = st.columns(2)
        with g1: st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="plotly_dark", title="Revenue/Service"), use_container_width=True)
        with g2: st.plotly_chart(px.pie(df, names='Service', hole=0.4, template="plotly_dark", title="Market Share"), use_container_width=True)

with t2:
    with st.expander("➕ AJOUTER UN NOUVEAU CLIENT"):
        ca, cb, cc = st.columns(3)
        with ca:
            n_nom = st.text_input("Nom Complet")
            n_phone = st.text_input("WhatsApp (212...)")
            n_email = st.text_input("Email")
        with cb:
            s_list = ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"]
            s_choice = st.selectbox("Service", s_list)
            final_s = st.text_input("Préciser le service") if s_choice == "Autre" else s_choice
            n_prix = st.number_input("Prix (DH)", min_value=0)
        with cc:
            n_deb = st.date_input("Date de Début", today) # 💡 RESTORED
            n_dur = st.number_input("Durée (Mois)", min_value=1, value=1)
            n_stat = st.selectbox("Status Initial", ["Actif", "Payé", "En Attente"])
        
        if st.button("💾 Enregistrer dans le Cloud"):
            if n_nom and n_phone:
                n_fin = n_deb + relativedelta(months=int(n_dur))
                # Structure: Nom, Phone, Email, Service, Prix, Début, Durée, Fin, Status
                new_row = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), n_stat]
                c_sheet_obj.append_row(new_row)
                st.success("✅ Synchro réussie !")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        # Ordre dial les colonnes bach i-ban kolchi
        cols_order = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Jours Restants", "Status"]
        actual_cols = [c for c in cols_order if c in df.columns]
        
        edited = st.data_editor(df[actual_cols], use_container_width=True, num_rows="dynamic", 
                                disabled=["Jours Restants", "Date Fin"])
        
        if st.button("💾 Sauvegarder les modifications"):
            final_df = edited.drop(columns=['Jours Restants'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Google Sheets Updated!")
            st.rerun()

with t3:
    st.subheader("Relances WhatsApp 📲")
    urgent = df[(df['Jours Restants'] <= 3) & (df['Status'] != 'Payé')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            col_l, col_r = st.columns([3, 1])
            icon = "🔴" if r['Jours Restants'] <= 0 else "🟠"
            col_l.warning(f"{icon} **{r['Nom']}** | {r['Service']} | **{r['Jours Restants']} j** (Expire: {r['Date Fin']})")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire le {r['Date Fin']}. On renouvelle?"
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
            col_r.link_button("📲 Rappeler", wa)
    else: st.success("Aucun retard.")

with t4:
    st.subheader("Générateur de Reçu 📄")
    if not df.empty:
        sel = st.selectbox("Choisir klyan:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = f"*REÇU D'ABONNEMENT - {st.session_state['biz_name']}*\n\n👤 Client: {c['Nom']}\n📺 Service: {c['Service']}\n💰 Prix: {c['Prix']} DH\n📅 Fin: {c['Date Fin']}\n\n*Merci pour votre confiance !*"
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

if st.sidebar.button("Déconnexion"):
    st.session_state.clear()
    st.rerun()
