import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import plotly.express as px

# SYSTEM STATUS: V5 - THE UNBREAKABLE EDITION
st.set_page_config(page_title="SUBS_FLOW_PRO_ULTIMATE", layout="wide", page_icon="👑")

# Link dial Google Sheet dial Fatima
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iBxqfL4nwhdJCZYd9GZa22MS69knWR9qc1aDTAFLinQ/edit?usp=sharing"

# Connection l Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(spreadsheet=SHEET_URL, ttl=0)

# --- LOGIN SYSTEM ---
if "password_correct" not in st.session_state:
    st.title("🔒 Private Access Control")
    pwd = st.text_input("Dakhli s-sarout a Fatima:", type="password")
    if st.button("Unlock System"):
        if pwd == "fatima2025":
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("❌ Access Denied.")
    st.stop()

# --- DATA LOADING & HARD TYPE CASTING (Anti-Error Patch) ---
df_raw = load_data()

if not df_raw.empty:
    df = df_raw.copy()
    
    # Patch Email ila makanch f Sheet
    if 'Email' not in df.columns:
        df['Email'] = ""

    # FORCE TYPES: Hadchi bach maytra7ch l-mochkil dial data_editor
    df['Nom'] = df['Nom'].astype(str).replace('nan', '')
    df['Phone'] = df['Phone'].astype(str).replace('nan', '')
    df['Email'] = df['Email'].astype(str).replace('nan', '')
    df['Service'] = df['Service'].astype(str).replace('nan', '')
    df['Status'] = df['Status'].astype(str).replace('nan', '')
    
    # Prix khasso i-koun raqm
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    
    # Durée khasso i-koun raqm
    df['Durée (Mois)'] = pd.to_numeric(df['Durée (Mois)'], errors='coerce').fillna(1)

    # Dates Processing
    df['Date Fin'] = pd.to_datetime(df['Date Fin'], errors='coerce').dt.date
    df['Date Début'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.date
    
    today = datetime.now().date()
    
    # Calculs dial l-mains
    df['Jours Restants'] = df['Date Fin'].apply(lambda x: (x - today).days if pd.notnull(x) else 0)
    df['Mois'] = pd.to_datetime(df['Date Début'], errors='coerce').dt.strftime('%B %Y').fillna("N/A")
else:
    df = pd.DataFrame(columns=["Nom", "Phone", "Email", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status"])

# --- UI INTERFACE ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 DASHBOARD", "👥 GESTION CLIENTS", "🔔 RAPPELS WHATSAPP", "👑 ADMIN"])

# ==========================================
# TAB 1: DASHBOARD
# ==========================================
with tab1:
    st.header("💰 Business Analytics")
    if not df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Revenue Global", f"{df['Prix'].sum()} DH")
        c2.metric("Clients Actifs", len(df[df['Status'] == 'Actif']))
        c3.metric("Emails", len(df[df['Email'] != ""]))
        c4.metric("Revenue ce Mois", f"{df[df['Mois'] == today.strftime('%B %Y')]['Prix'].sum()} DH")

        st.markdown("---")
        g1, g2 = st.columns(2)
        with g1:
            fig_service = px.bar(df, x='Service', y='Prix', color='Service', title="Revenue par Service", text_auto=True)
            st.plotly_chart(fig_service, use_container_width=True)
        with g2:
            fig_status = px.pie(df, names='Status', title="Clients par Status", hole=0.5)
            st.plotly_chart(fig_status, use_container_width=True)

# ==========================================
# TAB 2: GESTION CLIENTS (The Fixed Part)
# ==========================================
with tab2:
    st.header("👥 Customer Database")
    with st.expander("➕ Ajouter un nouveau client"):
        ca, cb, cc = st.columns(3)
        with ca:
            new_nom = st.text_input("Nom Complet")
            new_phone = st.text_input("WhatsApp (ex: 2126...)")
            new_email = st.text_input("Email")
        with cb:
            new_service = st.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"])
            final_s = st.text_input("Nom Service Spécifique") if new_service == "Autre" else new_service
            new_prix = st.number_input("Prix (DH)", min_value=0, step=5)
        with cc:
            new_date_d = st.date_input("Date de Début", today)
            new_duree = st.number_input("Durée (Mois)", min_value=1, value=1)
            new_status = st.selectbox("Status", ["Actif", "En Attente", "Payé", "Annulé", "Renouveler"])

        if st.button("🚀 Enregistrer au Cloud"):
            if new_nom and new_phone:
                date_f_calc = new_date_d + relativedelta(months=int(new_duree))
                new_row = pd.DataFrame([{
                    "Nom": new_nom, "Phone": str(new_phone), "Email": new_email, 
                    "Service": final_s, "Prix": new_prix, "Date Début": str(new_date_d), 
                    "Durée (Mois)": new_duree, "Date Fin": str(date_f_calc), "Status": new_status
                }])
                # On enlève les colonnes calculées avant de sauvegarder
                df_clean = df.drop(columns=['Jours Restants', 'Mois'], errors='ignore')
                final_save = pd.concat([df_clean, new_row], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=final_save)
                st.success("✅ Client ajouté!")
                st.rerun()

    st.markdown("---")
    
    # SEARCH BAR
    search_query = st.text_input("🔍 Rechercher un nom ou un numéro...")
    df_filtered = df[df['Nom'].str.contains(search_query, case=False) | df['Phone'].str.contains(search_query)] if search_query else df

    # DATA EDITOR (THE SECURED VERSION)
    st.subheader("📋 Liste Editable")
    edited_df = st.data_editor(
        df_filtered,
        column_config={
            "Status": st.column_config.SelectboxColumn("Status", options=["Actif", "En Attente", "Payé", "Annulé", "Renouveler"]),
            "Prix": st.column_config.NumberColumn("Prix (DH)"),
            "Nom": st.column_config.TextColumn("Nom"),
            "Phone": st.column_config.TextColumn("Phone"),
            "Email": st.column_config.TextColumn("Email")
        },
        disabled=["Jours Restants", "Mois", "Date Fin"],
        use_container_width=True,
        num_rows="dynamic"
    )

    if st.button("💾 Sauvegarder les modifications"):
        # On nettoie avant de renvoyer à Google Sheets
        final_df = edited_df.drop(columns=['Jours Restants', 'Mois'], errors='ignore')
        conn.update(spreadsheet=SHEET_URL, data=final_df)
        st.success("✅ Synchro réussie!")
        st.rerun()

# ==========================================
# TAB 3: RAPPELS
# ==========================================
with tab3:
    st.header("🔔 Rappels Automatiques")
    alerts = df[(df['Jours Restants'] <= 3) & (df['Status'].isin(['Actif', 'Payé']))]
    
    if not alerts.empty:
        st.warning(f"Attention Master Fatima: {len(alerts)} rappels à faire!")
        for _, row in alerts.iterrows():
            with st.container():
                c_1, c_2 = st.columns([3, 1])
                c_1.write(f"👤 **{row['Nom']}** | 📺 {row['Service']} | ⏳ **{row['Jours Restants']} jours restants**")
                msg = f"Bonjour {row['Nom']}, votre abonnement {row['Service']} expire le {row['Date Fin']}. Voulez-vous renouveler ?"
                wa_url = f"https://wa.me/{row['Phone']}?text={urllib.parse.quote(msg)}"
                c_2.link_button("📲 WhatsApp", wa_url)
                st.markdown("---")
    else:
        st.success("✅ Aucun rappel urgent.")

# ==========================================
# TAB 4: 👑 ADMIN
# ==========================================
with tab4:
    st.header("👑 Advanced Control")
    admin_pwd = st.text_input("Admin Password:", type="password")
    if admin_pwd == "omega2025":
        st.write("### 💎 Business Insights")
        st.write(f"- **Top Service:** {df['Service'].mode()[0] if not df.empty else 'N/A'}")
        st.write(f"- **Taux de Payement:** {round((len(df[df['Status'] == 'Payé']) / len(df)) * 100)}% de conversion")
        st.download_button("📥 Backup Database (CSV)", df.to_csv(index=False), "backup.csv", "text/csv")
    elif admin_pwd:
        st.error("Accès non autorisé.")


