import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- НАСТРОЙКИ ИНТЕРФЕЙСА ---
st.set_page_config(page_title="Smart Finance Local", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #E2E8F0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stButton>button { border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- РАБОТА С ЛОКАЛЬНОЙ БАЗОЙ ---
DB_NAME = 'finance_local.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS fortune 
                 (Date TEXT, Fortune REAL, Cash REAL, Investissements REAL, Assets REAL, Dette REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS flux 
                 (Date TEXT, Revenus REAL, Depenses REAL)''')
    conn.commit()
    conn.close()

def load_table(table):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

def save_table(df, table):
    conn = sqlite3.connect(DB_NAME)
    df.to_sql(table, conn, if_exists='replace', index=False)
    conn.close()

init_db()

# --- SIDEBAR ---
st.sidebar.title("💎 Smart Finance")
st.sidebar.write("Gestion de Fortune")
menu = st.sidebar.radio("Navigation", ["Tableau de Bord", "Données & Import"])

if menu == "Données & Import":
    st.title("📝 Gestion des Données")
    
    # 1. Загрузка из Excel
    with st.expander("📥 Importer depuis Excel (.xlsm)"):
        uploaded_file = st.file_uploader("Choisir un fichier", type=["xlsm", "xlsx"])
        if uploaded_file and st.button("Lancer l'import"):
            try:
                # Читаем листы из вашего шаблона
                df_f_excel = pd.read_excel(uploaded_file, sheet_name="🏦 Allocation de Fortune", skiprows=1)
                df_x_excel = pd.read_excel(uploaded_file, sheet_name="🍾 Dépenses ", skiprows=1)
                
                # Чистим данные (удаляем пустые строки)
                df_f_excel = df_f_excel[['Date', 'Fortune', 'Liquide', 'Assets']].dropna(subset=['Date']).rename(columns={'Liquide': 'Cash'})
                df_x_excel = df_x_excel[['Date', 'Revenus', 'Dépenses Total']].dropna(subset=['Date']).rename(columns={'Dépenses Total': 'Depenses'})
                
                save_table(df_f_excel, "fortune")
                save_table(df_x_excel, "flux")
                st.success("Données importées avec succès !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur d'import : {e}")

    st.markdown("---")
    
    # 2. Ручной ввод (Data Editor)
    df_f = load_table("fortune")
    st.subheader("🏦 Table de Fortune")
    edited_f = st.data_editor(df_f, num_rows="dynamic", use_container_width=True, key="ed_f")
    
    if st.button("Sauvegarder les modifications"):
        save_table(edited_f, "fortune")
        st.success("Base de données mise à jour !")

else:
    # --- ТАБЛО (TABLEAU DE BORD) ---
    df_f = load_table("fortune")
    df_x = load_table("flux")

    if not df_f.empty:
        # KPI ROW
        latest = df_f.iloc[-1]
        st.title("📊 Tableau de Bord")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("FORTUNE TOTALE", f"{latest['Fortune']:,.0f} €")
        c2.metric("CASH", f"{latest.get('Cash', 0):,.0f} €")
        c3.metric("ASSETS", f"{latest.get('Assets', 0):,.0f} €")
        c4.metric("DETTE", f"{latest.get('Dette', 0):,.0f} €")

        st.markdown("<br>", unsafe_allow_html=True)

        # CHARTS ROW
        col_l, col_r = st.columns([2, 1])

        with col_l:
            st.subheader("📈 Croissance du Patrimoine")
            fig = px.area(df_f, x='Date', y='Fortune', color_discrete_sequence=['#10B981'])
            fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.subheader("🍩 Allocation")
            vals = [latest.get('Cash', 0), latest.get('Investissements', 0), latest.get('Assets', 0)]
            fig_pie = px.pie(values=vals, names=['Cash', 'Invest.', 'Assets'], hole=0.7,
                             color_discrete_sequence=['#34D399', '#3B82F6', '#FBBF24'])
            st.plotly_chart(fig_pie, use_container_width=True)

        # FLOW CHART
        st.subheader("💶 Revenus vs Dépenses")
        if not df_x.empty:
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=df_x['Date'], y=df_x['Revenus'], name='Revenus', marker_color='#10B981'))
            fig_bar.add_trace(go.Bar(x=df_x['Date'], y=df_x['Depenses'], name='Dépenses', marker_color='#EF4444'))
            fig_bar.update_layout(barmode='group', height=350)
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("👋 Bienvenue ! Allez dans 'Données & Import' pour charger votre fichier Excel.")