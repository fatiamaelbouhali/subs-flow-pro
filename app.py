import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse

# OMEGA STATUS: DATA TYPE FIX DEPLOYED
st.set_page_config(page_title="SUBSCRIPTION MASTER PRO", layout="wide")

DB_FILE = "database_clients.xlsx"


# --- LOGIN SYSTEM ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔒 Access Restricted")
        pwd = st.text_input("Dakhli l-code a Fatima:", type="password")
        if st.button("Log In"):
            if pwd == "fatima2025":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Code ghalat!")
        return False
    return True


if check_password():
    # --- INITIALIZATION (Fixed for Phone Type) ---
    def init_excel():
        cols = ["Nom", "Phone", "Service", "Prix", "Date Début", "Durée (Mois)", "Date Fin", "Status"]
        if not os.path.exists(DB_FILE):
            pd.DataFrame(columns=cols).to_excel(DB_FILE, index=False)
        else:
            df = pd.read_excel(DB_FILE)
            for col in cols:
                if col not in df.columns: df[col] = ""
            df.to_excel(DB_FILE, index=False)


    init_excel()

    # --- SIDEBAR: ADD CLIENT ---
    st.sidebar.header("➕ Nouveau Client")
    with st.sidebar.expander("Ajouter Client", expanded=True):
        nom = st.text_input("Nom Complet")
        phone = st.text_input("WhatsApp (ex: 2126...)")

        service_list = ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Disney+", "Autre"]
        service_choice = st.selectbox("Service", service_list)
        final_service = st.text_input("Smiyat s-service") if service_choice == "Autre" else service_choice

        prix = st.number_input("Prix (DH)", min_value=0, step=5)

        date_debut = st.date_input("Date Début", datetime.now())
        duree_mois = st.number_input("Durée (en Mois)", min_value=1, max_value=24, value=1)

        date_fin_calc = date_debut + relativedelta(months=int(duree_mois))
        st.info(f"📅 Fin prévue: **{date_fin_calc}**")

        status = st.selectbox("Status", ["Actif", "En Attente", "Payé", "Annulé", "Renouveler"])

        if st.button("Sauvegarder Nouveau"):
            if nom and phone:
                df = pd.read_excel(DB_FILE, dtype={'Phone': str})  # Force Phone as String
                new_data = {
                    "Nom": nom, "Phone": str(phone), "Service": final_service,
                    "Prix": prix, "Date Début": str(date_debut),
                    "Durée (Mois)": duree_mois, "Date Fin": str(date_fin_calc), "Status": status
                }
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                df.to_excel(DB_FILE, index=False)
                st.sidebar.success(f"Nadi! {nom} t-zad.")
                st.rerun()

    # --- MAIN CONTENT ---
    st.title("⚡ SUBSCRIPTION FLOW - ULTIMATE")

    # Force read as String for Phone to avoid Type Errors
    if os.path.exists(DB_FILE):
        df = pd.read_excel(DB_FILE, dtype={'Phone': str})
    else:
        df = pd.DataFrame()

    if not df.empty:
        # Pre-processing
        df['Date Fin'] = pd.to_datetime(df['Date Fin']).dt.date
        today = datetime.now().date()
        df['Jours Restants'] = (df['Date Fin'] - today).apply(lambda x: x.days)

        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Clients", len(df))
        c2.metric("Revenue", f"{df['Prix'].sum()} DH")
        c3.metric("Actifs", len(df[df['Status'] == 'Actif']))
        c4.download_button("📥 Backup Excel", df.to_csv(index=False), "backup_subs.csv", "text/csv")

        # Alerts
        alerts = df[(df['Jours Restants'] <= 3) & (df['Status'] == 'Actif')]
        if not alerts.empty:
            with st.expander("⚠️ RAPPELS URGENTS (≤ 3 Jours)", expanded=True):
                for _, row in alerts.iterrows():
                    st.warning(f"**{row['Nom']}** ({row['Service']}) : b9a lih **{row['Jours Restants']} j**")


        # WhatsApp Link
        def wa_link(p, n, s):
            m = f"Bonjour {n}, votre abonnement {s} va expirer. Voulez-vous renouveler?"
            return f"https://wa.me/{p}?text={urllib.parse.quote(m)}"


        df['Chat'] = df.apply(lambda x: wa_link(x['Phone'], x['Nom'], x['Service']), axis=1)

        # INTERACTIVE TABLE (Fixed Configuration)
        st.subheader("📋 Liste & Modification")
        edited_df = st.data_editor(
            df,
            column_config={
                "Chat": st.column_config.LinkColumn("WhatsApp", display_text="Envoyer 📲"),
                "Status": st.column_config.SelectboxColumn("Status", options=["Actif", "En Attente", "Payé", "Annulé",
                                                                              "Renouveler"]),
                "Phone": st.column_config.TextColumn("Phone")  # Force as TextColumn
            },
            disabled=["Jours Restants", "Date Fin"],
            use_container_width=True,
            num_rows="dynamic"
        )

        if st.button("💾 Sauvegarder toutes les modifications"):
            final_df = edited_df.drop(columns=['Jours Restants', 'Chat'])
            # Ensure Phone stays String before saving
            final_df['Phone'] = final_df['Phone'].astype(str)
            final_df.to_excel(DB_FILE, index=False)
            st.success("Kolchi t-sauvegarda mzyan a Fatima!")
            st.rerun()
    else:
        st.info("App khawya. Bdai t-3mmri les clients mn l-yissar.")

st.markdown("---")
st.caption("OMEGA System - Secured & Fixed")