import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# OMEGA STATUS: SAAS GOD MODE ACTIVATED
st.set_page_config(page_title="SUBS_FLOW_ULTIMATE_V4", layout="wide")

# Link dial Google Sheet dialek a Fatima
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iBxqfL4nwhdJCZYd9GZa22MS69knWR9qc1aDTAFLinQ/edit?usp=sharing"

# Connection l Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(spreadsheet=SHEET_URL, ttl=0)

# --- LOGIN SYSTEM ---
if "password_correct" not in st.session_state:
    st.title("🔒 Private Management System")
    pwd = st.text_input("Dakhl lcode dialek a Hnaya:", type="password")
    if st.button("Unlock Power"):
        if pwd == "fatima2025":
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("❌ Code ghalat! Zyr m3aya.")
    st.stop()

# --- DATA PROCESSING ---
df = load_data()
if not df.empty:
    df['Date Fin'] = pd.to_datetime(df['Date Fin']).dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début']).dt.date
    today = datetime.now().date()
    df['Jours Restants'] = (df['Date Fin'] - today).apply(lambda x: x.days)
    df['Mois'] = pd.to_datetime(df['Date Début']).dt.strftime('%B %Y')

# --- UI TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 DASHBOARD", "👥 CLIENTS", "🔔 RAPPELS", "👑 ADMIN"])

# ==========================================
# TAB 1: DASHBOARD (Flooos Visualization)
# ==========================================
with tab1:
    st.header("💰 Analyse Financière")
    if not df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Revenue Global", f"{df['Prix'].sum()} DH")
        c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        c3.metric("Emails Collectés", len(df[df['Email'].notna()]))
        c4.metric("Revenue ce Mois", f"{df[df['Mois'] == today.strftime('%B %Y')]['Prix'].sum()} DH")

        st.markdown("---")
        g1, g2 = st.columns(2)
        with g1:
            fig_service = px.bar(df, x='Service', y='Prix', color='Service', title="Revenue par Service", text_auto=True)
            st.plotly_chart(fig_service, use_container_width=True)
        with g2:
            fig_pie = px.pie(df, names='Status', title="Répartition des Clients", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

# ==========================================
# TAB 2: CLIENTS (With Email)
# ==========================================
with tab2:
    st.header("👥 Gestion des Abonnements")
    with st.expander("➕ Ajouter un nouveau client"):
        ca, cb, cc = st.columns(3)
        with ca:
            nom = st.text_input("Nom Complet")
            phone = st.text_input("WhatsApp (ex: 2126...)")
            email = st.text_input("Email") # ZDNA EMAIL HNA
        with cb:
            service = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
            final_s = st.text_input("Préciser Service") if service == "Autre" else service
            prix = st.number_input("Prix (DH)", min_value=0, step=5)
        with cc:
            date_d = st.date_input("Date Début", today)
            duree = st.number_input("Durée (Mois)", min_value=1, value=1)
            status = st.selectbox("Status", ["Actif", "En Attente", "Payé", "Annulé", "Renouveler"])

        if st.button("🚀 Sauvegarder"):
            if nom and phone:
                date_f = date_d + relativedelta(months=int(duree))
                new_row = pd.DataFrame([{
                    "Nom": nom, "Phone": str(phone), "Email": email, "Service": final_s, 
                    "Prix": prix, "Date Début": str(date_d), 
                    "Durée (Mois)": duree, "Date Fin": str(date_f), "Status": status
                }])
                new_df = pd.concat([df.drop(columns=['Jours Restants', 'Mois'], errors='ignore') if not df.empty else df, new_row], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=new_df)
                st.success("✅ Client t-zad f Google Sheets!")
                st.rerun()

    st.markdown("---")
    edited_df = st.data_editor(
        df,
        column_config={
            "Status": st.column_config.SelectboxColumn("Status", options=["Actif", "En Attente", "Payé", "Annulé", "Renouveler"]),
            "Email": st.column_config.TextColumn("Email Client"),
        },
        disabled=["Jours Restants", "Mois", "Date Fin"],
        use_container_width=True,
        num_rows="dynamic"
    )

    if st.button("💾 Enregistrer les modifications"):
        save_df = edited_df.drop(columns=['Jours Restants', 'Mois'], errors='ignore')
        conn.update(spreadsheet=SHEET_URL, data=save_df)
        st.success("✅ Synchro Nadiya!")
        st.rerun()

# ==========================================
# TAB 3: RAPPELS (The Alert System)
# ==========================================
with tab3:
    st.header("🔔 Alerts WhatsApp")
    # Alerts l ga3 n-nass li b9at lihom 3 jours ou r9el
    alerts_df = df[(df['Jours Restants'] <= 3) & (df['Status'].isin(['Actif', 'Payé']))]
    
    if not alerts_df.empty:
        st.warning(f"3ndek {len(alerts_df)} rappels khasshoum i-t-tiriw!")
        for _, row in alerts_df.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"👤 **{row['Nom']}** | 📺 {row['Service']} | ⏳ **{row['Jours Restants']} j**")
                st.caption(f"Email: {row['Email']}")
            with col2:
                msg = f"Bonjour {row['Nom']}, votre abonnement {row['Service']} expire le {row['Date Fin']}. On renouvelle?"
                url = f"https://wa.me/{row['Phone']}?text={urllib.parse.quote(msg)}"
                st.link_button("📲 Rappeler", url)
            st.markdown("---")
    else:
        st.success("✅ Kolchi khallass dabba.")

# ==========================================
# TAB 4: 👑 ADMIN (God Mode)
# ==========================================
with tab4:
    st.header("👑 Admin Control Panel")
    admin_pwd = st.text_input("Dakhli s-sarout d l-Admin a Fatima:", type="password")
    if admin_pwd == "omega2025":
        st.success("Bienvenue Master Fatima. Hna katchoufi l-moussi9a dial s-s7i7.")
        st.write("### 💎 Advanced Stats")
        st.write(f"- **Top Service:** {df['Service'].mode()[0] if not df.empty else 'N/A'}")
        st.write(f"- **Taux de Payement:** {round((len(df[df['Status'] == 'Payé']) / len(df)) * 100)}% dial l-klyan")
        
        # Backup CSV
        st.download_button("📥 Backup Database (CSV)", df.to_csv(index=False), "backup_pro.csv", "text/csv")
        
        if st.button("🧹 Nettoyer les Doublons"):
            df_clean = df.drop_duplicates(subset=['Phone', 'Service'])
            conn.update(spreadsheet=SHEET_URL, data=df_clean)
            st.success("Database Cleaned!")
    elif admin_pwd:
        st.error("Dégage! Ma-3ndekch s-sarout hna.")


