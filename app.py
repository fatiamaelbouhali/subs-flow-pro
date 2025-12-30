import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: OMEGA V53 - THE TOTAL EMPIRE (ALL FEATURES RESTORED)
st.set_page_config(page_title="EMPIRE_V53_PRO", layout="wide", page_icon="🏦")

# ⚡ CSS VIBRANT & PRO - NO VISIBILITY ISSUES
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        border: 1px solid #6366f1;
        padding: 15px;
        border-radius: 15px;
        background: rgba(99, 102, 241, 0.05);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] > div { color: #4f46e5 !important; font-weight: 900 !important; }
    label p { color: #1e293b !important; font-weight: 700 !important; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; font-size: 18px; }
    .biz-banner {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        padding: 25px; border-radius: 15px; color: white !important;
        text-align: center; font-size: 40px; font-weight: 900;
        margin-bottom: 25px; box-shadow: 0 10px 25px rgba(99, 102, 241, 0.3);
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
    st.markdown('<div class="biz-banner">🚀 EMPIRE SaaS LOGIN</div>', unsafe_allow_html=True)
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
                    st.session_state.update({"auth": True, "user": u_in, "biz_name": str(match.iloc[0]['Business_Name']), "sheet_name": str(match.iloc[0]['Sheet_Name'])})
                    st.rerun()
                else: st.error("🚫 Access Blocked.")
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

# --- 3. DATA CLEANING & LOGIC ---
if not df.empty:
    for c in ['Nom', 'Phone', 'Email', 'Service', 'Status']:
        if c in df.columns: df[c] = df[c].astype(str).replace('nan', '')
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.date
    df['Days'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Date_Display'] = pd.to_datetime(df['Date Fin']).dt.strftime('%Y-%m-%d').fillna("N/A")
    df.loc[(df['Days'] <= 0) & (df['Status'] == 'Actif'), 'Status'] = 'Expiré'

# --- 4. THE UI ---
st.markdown(f'<div class="biz-banner">⚡ {st.session_state["biz_name"]}</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["📊 ANALYTICS", "👥 GESTION", "🔔 RAPPELS", "📄 REÇUS"])

# TAB 1: ANALYTICS (SUMMARY RESTORED)
with t1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 REVENUE TOTAL", f"{df['Prix'].sum()} DH")
        c2.metric("✅ CLIENTS ACTIFS", len(df[df['Status'] == 'Actif']))
        c3.metric("🚨 ALERTES (3j)", len(df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]))
        
        st.markdown("### 📋 Résumé Business par Service")
        summary = df.groupby('Service').agg({'Nom': 'count', 'Prix': 'sum'}).reset_index()
        summary.columns = ['Service', 'Clients', 'Chiffre d\'Affaires (DH)']
        st.table(summary) # 💡 RESTORED SUMMARY TABLE

        st.plotly_chart(px.bar(df, x='Service', y='Prix', color='Status', template="simple_white"), use_container_width=True)

# TAB 2: GESTION (DATE DEBUT RESTORED)
with t2:
    with st.expander("➕ AJOUTER UN NOUVEAU CLIENT"):
        ca, cb, cc = st.columns(3)
        n_nom = ca.text_input("Nom")
        n_phone = ca.text_input("WhatsApp")
        n_email = ca.text_input("Email")
        s_choice = cb.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
        final_s = cb.text_input("Nom service") if s_choice == "Autre" else s_choice
        n_prix = cc.number_input("Prix (DH)", min_value=0)
        n_deb = cc.date_input("Date de Début", today) # 💡 RESTORED FIELD
        n_dur = cc.number_input("Durée (Mois)", min_value=1, value=1)
        
        if st.button("🚀 Enregistrer au Cloud"):
            if n_nom and n_phone:
                n_fin = n_deb + relativedelta(months=int(n_dur))
                new_r = [n_nom, str(n_phone), n_email, final_s, n_prix, str(n_deb), n_dur, str(n_fin), "Actif"]
                
                # Smart Inserter Logic
                df_clean = df.drop(columns=['Days', 'Date_Display'], errors='ignore')
                df_new = pd.concat([df_clean, pd.DataFrame([dict(zip(df_clean.columns, new_row)) for new_row in [new_r]])], ignore_index=True)
                c_sheet_obj.clear()
                c_sheet_obj.update([df_new.columns.values.tolist()] + df_new.astype(str).values.tolist())
                st.success("✅ Synchro réussie!")
                st.rerun()

    st.markdown("---")
    if not df.empty:
        cols = ["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status", "Days"]
        edited = st.data_editor(df[cols], use_container_width=True, num_rows="dynamic", disabled=["Days", "Date Fin"])
        if st.button("💾 Sauvegarder les modifications"):
            final_df = edited.drop(columns=['Days'], errors='ignore')
            c_sheet_obj.clear()
            c_sheet_obj.update([final_df.columns.values.tolist()] + final_df.astype(str).values.tolist())
            st.success("✅ Database Updated!")
            st.rerun()

# TAB 3: ALERTS
with t3:
    st.subheader("Relances WhatsApp 📲")
    urgent = df[(df['Days'] <= 3) & (df['Status'] == 'Actif')]
    if not urgent.empty:
        for _, r in urgent.iterrows():
            cl, cr = st.columns([3, 1])
            cl.warning(f"👤 {r['Nom']} | 📺 {r['Service']} | ⏳ **{r['Days']} jours**")
            msg = f"Bonjour {r['Nom']}, votre abonnement {r['Service']} expire le {r['Date_Display']}. On renouvelle?"
            wa = f"https://wa.me/{r['Phone']}?text={urllib.parse.quote(msg)}"
            cr.link_button("📲 Envoyer Rappel", wa)
    else: st.success("Tout est à jour.")

# TAB 4: REÇUS
with t4:
    if not df.empty:
        sel = st.selectbox("Client pour Reçu:", df['Nom'].unique())
        c = df[df['Nom'] == sel].iloc[0]
        reçu = (f"✅ *REÇU DE PAIEMENT - {st.session_state['biz_name']}*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👤 Client: *{c['Nom']}*\n"
                f"📺 Service: *{c['Service']}*\n"
                f"💰 Prix: *{c['Prix']} DH*\n"
                f"⌛ Expire: *{c['Date_Display']}*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🤝 *Merci pour votre confiance !*")
        st.code(reçu)
        st.link_button("📲 Envoyer via WhatsApp", f"https://wa.me/{c['Phone']}?text={urllib.parse.quote(reçu)}")

if st.sidebar.button("Log out"):
    st.session_state.clear()
    st.rerun()
