import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse

# OMEGA STATUS: GOOGLE SHEETS PERSISTENCE ACTIVATED
st.set_page_config(page_title="SUBS_FLOW_PRO_GSHEETS", layout="wide")

# Link dial Google Sheet dialek a Fatima
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iBxqfl4nwhdJCZYd9gZa22MS69knWR9qC1aDTAFLinQ/edit?usp=sharing"

# 1. Connection l Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(spreadsheet=SHEET_URL, ttl=0)

# --- LOGIN SYSTEM ---
if "password_correct" not in st.session_state:
    st.title("🔒 Private Access")
    pwd = st.text_input("Dakhli l-code:", type="password")
    if st.button("Log In"):
        if pwd == "fatima2025":
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("❌ Code ghalat!")
    st.stop()

# --- INTERFACE ---
st.title("⚡ SUBS_FLOW - GOOGLE SHEETS EDITION")

# Sidebar: Ajout
st.sidebar.header("➕ Nouveau Client")
nom = st.sidebar.text_input("Nom Complet")
phone = st.sidebar.text_input("WhatsApp (ex: 2126...)")
service_choice = st.sidebar.selectbox("Service", ["Netflix", "ChatGPT", "Canva", "Spotify", "IPTV", "Autre"])
final_service = st.sidebar.text_input("Préciser") if service_choice == "Autre" else service_choice
prix = st.sidebar.number_input("Prix (DH)", min_value=0, step=5)
date_debut = st.sidebar.date_input("Date Début", datetime.now())
duree = st.sidebar.number_input("Durée (Mois)", min_value=1, value=1)
date_fin_calc = date_debut + relativedelta(months=int(duree))
status = st.sidebar.selectbox("Status", ["Actif", "En Attente", "Payé", "Annulé", "Renouveler"])

if st.sidebar.button("Sauvegarder dans Google Sheets"):
    if nom and phone:
        df = load_data()
        new_row = pd.DataFrame([{
            "Nom": nom, "Phone": str(phone), "Service": final_service, 
            "Prix": prix, "Date Début": str(date_debut), 
            "Durée (Mois)": duree, "Date Fin": str(date_fin_calc), "Status": status
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, data=df)
        st.sidebar.success("✅ T-khzen f Google Sheets!")
        st.rerun()

# --- DISPLAY ---
df = load_data()
if not df.empty:
    df['Date Fin'] = pd.to_datetime(df['Date Fin']).dt.date
    df['Jours Restants'] = (df['Date Fin'] - datetime.now().date()).apply(lambda x: x.days)
    
    st.metric("Total Revenue", f"{df['Prix'].sum()} DH")
    
    # WhatsApp Link
    def wa_link(p, n, s):
        m = f"Bonjour {n}, votre abonnement {s} arrive à sa fin. On renouvelle?"
        return f"https://wa.me/{p}?text={urllib.parse.quote(m)}"
    df['WhatsApp'] = df.apply(lambda x: wa_link(x['Phone'], x['Nom'], x['Service']), axis=1)

    edited_df = st.data_editor(df, column_config={"WhatsApp": st.column_config.LinkColumn("Chat", display_text="Envoyer 📲")}, use_container_width=True, num_rows="dynamic")

    if st.button("💾 Mettre à jour Google Sheets"):
        final_df = edited_df.drop(columns=['Jours Restants', 'WhatsApp'])
        conn.update(spreadsheet=SHEET_URL, data=final_df)
        st.success("✅ Google Sheets Updated!")
        st.rerun()
else:
    st.info("Sheet khawya. Bdai t-3mmri.")
