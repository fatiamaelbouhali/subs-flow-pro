import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# OMEGA STATUS: TOTAL DOMINATION - PERFECTION EDITION
st.set_page_config(page_title="SUBS_FLOW_ULTIMATE", layout="wide")

# Link dial Google Sheet dialek
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iBxqfL4nwhdJCZYd9GZa22MS69knWR9qc1aDTAFLinQ/edit?usp=sharing"

# Connection l Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(spreadsheet=SHEET_URL, ttl=0)

# --- LOGIN SYSTEM ---
if "password_correct" not in st.session_state:
    st.title("🔒 OMEGA SECURED ACCESS")
    pwd = st.text_input("Dakhli s-sarout a Fatima:", type="password")
    if st.button("Unleash Power"):
        if pwd == "fatima2025":
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("❌ Ghalat! Mat-l3bi m3a OMEGA.")
    st.stop()

# --- DATA PRE-PROCESSING ---
df = load_data()
if not df.empty:
    df['Date Fin'] = pd.to_datetime(df['Date Fin']).dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début']).dt.date
    today = datetime.now().date()
    df['Jours Restants'] = (df['Date Fin'] - today).apply(lambda x: x.days)
    df['Mois'] = pd.to_datetime(df['Date Début']).dt.strftime('%B %Y')

# --- UI TABS ---
tab1, tab2, tab3 = st.tabs(["📊 DASHBOARD FINANCIER", "👥 GESTION DES CLIENTS", "🔔 RAPPELS WHATSAPP"])

# ==========================================
# TAB 1: DASHBOARD (FLOOOS)
# ==========================================
with tab1:
    st.header("💰 Analyse des Revenus")
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Revenue Total", f"{df['Prix'].sum()} DH", delta="Nadiya")
        col2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        col3.metric("Abonnements Payés", len(df[df['Status'] == 'Payé']))
        col4.metric("Revenue ce Mois", f"{df[df['Mois'] == today.strftime('%B %Y')]['Prix'].sum()} DH")

        st.markdown("---")
        g1, g2 = st.columns(2)
        
        with g1:
            # Revenue par Service
            fig_service = px.bar(df, x='Service', y='Prix', color='Service', title="Revenue par Service (DH)", text_auto=True)
            st.plotly_chart(fig_service, use_container_width=True)
            
        with g2:
            # Répartition des Status
            fig_status = px.pie(df, names='Status', title="Répartition par Status", hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_status, use_container_width=True)
            
        # Revenue Mensuel
        fig_month = px.line(df.groupby('Mois')['Prix'].sum().reset_index(), x='Mois', y='Prix', title="Évolution du Revenue Mensuel", markers=True)
        st.plotly_chart(fig_month, use_container_width=True)
    else:
        st.info("Makayna data bach n-7sbo l-flooos.")

# ==========================================
# TAB 2: GESTION (MODIF/ADD)
# ==========================================
with tab2:
    st.header("👥 Base de Données Live")
    
    # Sidebar l-Ajout (Inside Tab 2)
    with st.expander("➕ Ajouter un nouveau client"):
        c_a, c_b, c_c = st.columns(3)
        with c_a:
            nom = st.text_input("Nom Complet")
            phone = st.text_input("WhatsApp (ex: 2126...)")
        with c_b:
            service_choice = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
            final_service = st.text_input("Préciser") if service_choice == "Autre" else service_choice
        with c_c:
            prix = st.number_input("Prix (DH)", min_value=0, step=5)
            duree = st.number_input("Durée (Mois)", min_value=1, value=1)
            date_debut = st.date_input("Date Début", today)

        status = st.selectbox("Status Initial", ["Actif", "En Attente", "Payé", "Annulé", "Renouveler"])
        
        if st.button("🚀 Enregistrer dans Google Sheets"):
            if nom and phone:
                date_fin_calc = date_debut + relativedelta(months=int(duree))
                new_row = pd.DataFrame([{
                    "Nom": nom, "Phone": str(phone), "Service": final_service, 
                    "Prix": prix, "Date Début": str(date_debut), 
                    "Durée (Mois)": duree, "Date Fin": str(date_fin_calc), "Status": status
                }])
                new_df = pd.concat([df.drop(columns=['Jours Restants', 'Mois']) if not df.empty else df, new_row], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=new_df)
                st.success("✅ Nadi! T-zad f s-Sheet.")
                st.rerun()

    st.markdown("---")
    
    # Barre de recherche
    search = st.text_input("🔍 Rechercher un client...")
    if search:
        df_view = df[df['Nom'].str.contains(search, case=False, na=False) | df['Phone'].astype(str).str.contains(search)]
    else:
        df_view = df

    # Data Editor
    edited_df = st.data_editor(
        df_view,
        column_config={
            "Status": st.column_config.SelectboxColumn("Status", options=["Actif", "En Attente", "Payé", "Annulé", "Renouveler"]),
            "Prix": st.column_config.NumberColumn("Prix (DH)", format="%d DH"),
        },
        disabled=["Jours Restants", "Mois", "Date Fin"],
        use_container_width=True,
        num_rows="dynamic"
    )

    if st.button("💾 Sauvegarder les Changements"):
        final_df = edited_df.drop(columns=['Jours Restants', 'Mois', 'WhatsApp'], errors='ignore')
        conn.update(spreadsheet=SHEET_URL, data=final_df)
        st.success("✅ Google Sheets Synced!")
        st.rerun()

# ==========================================
# TAB 3: WHATSAPP (ALERTS)
# ==========================================
with tab3:
    st.header("🔔 Rappels de Renouvellement")
    
    # N-jebdou ghi n-nass li b9at lihom 3 jours ou r9el
    alerts_df = df[(df['Jours Restants'] <= 3) & (df['Status'] == 'Actif')]
    
    if not alerts_df.empty:
        st.warning(f"3ndek {len(alerts_df)} klyane khasshoum i-khlsso dabba!")
        for _, row in alerts_df.iterrows():
            col_1, col_2, col_3 = st.columns([2, 1, 1])
            with col_1:
                st.write(f"👤 **{row['Nom']}** | 📺 {row['Service']} | ⏳ **{row['Jours Restants']} jours**")
            with col_2:
                # Link WhatsApp
                msg = f"Bonjour {row['Nom']}, votre abonnement {row['Service']} va expirer bientôt ({row['Date Fin']}). Voulez-vous renouveler ?"
                wa_url = f"https://wa.me/{row['Phone']}?text={urllib.parse.quote(msg)}"
                st.link_button("📲 Envoyer Rappel", wa_url)
            with col_3:
                st.write(f"💰 {row['Prix']} DH")
            st.markdown("---")
    else:
        st.success("✅ Kolchi khallass! Ma-3ndek 7ta rappel dabba.")

st.sidebar.caption("OMEGA ULTIMATE V3 - THE GOD MODE")
