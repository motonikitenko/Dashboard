import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Настройки стиля
st.set_page_config(page_title="Smart Finance Dashboard", layout="wide", page_icon="💰")

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    div[data-testid="stMetric"] { background-color: #ffffff; border: 1px solid #E2E8F0; padding: 15px; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

def safe_float(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or val == 'NaN': return 0.0
        if isinstance(val, str):
            val = val.replace('€', '').replace(' ', '').replace(',', '.')
        return float(val)
    except: return 0.0

def get_val_by_label(df, label):
    try:
        for i in range(len(df)):
            for j in range(len(df.columns)):
                if label in str(df.iloc[i, j]): return safe_float(df.iloc[i, j+1])
        return 0.0
    except: return 0.0

# --- SIDEBAR ---
st.sidebar.title("💎 Smart Finance")
uploaded_file = st.sidebar.file_uploader("Charger le fichier .xlsx", type="xlsx")

if uploaded_file:
    try:
        # 1. Загрузка данных
        df_dash = pd.read_excel(uploaded_file, sheet_name="💰 Dashboard Financier", header=None)
        
        df_fortune = pd.read_excel(uploaded_file, sheet_name="🏦 Allocation de Fortune", skiprows=1)
        df_fortune['Date'] = pd.to_datetime(df_fortune['Date'])
        df_fortune = df_fortune.dropna(subset=['Date', 'Fortune']).sort_values('Date')

        df_exp = pd.read_excel(uploaded_file, sheet_name="🍾 Dépenses ", skiprows=1)
        df_exp['Date'] = pd.to_datetime(df_exp['Date'])
        df_exp = df_exp.dropna(subset=['Date']).sort_values('Date')

        # --- ФИЛЬТР ПЕРИОДА В SIDEBAR ---
        st.sidebar.markdown("---")
        st.sidebar.subheader("📅 Période d'analyse")
        
        min_date = df_fortune['Date'].min().to_pydatetime()
        max_date = df_fortune['Date'].max().to_pydatetime()
        
        # Выбор диапазона дат
        selected_dates = st.sidebar.date_input(
            "Sélectionnez la période",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        # Проверка, что выбраны обе даты (начало и конец)
        if len(selected_dates) == 2:
            start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
            
            # Фильтрация датафреймов
            mask_fortune = (df_fortune['Date'] >= start_date) & (df_fortune['Date'] <= end_date)
            df_fortune_filtered = df_fortune.loc[mask_fortune]
            
            mask_exp = (df_exp['Date'] >= start_date) & (df_exp['Date'] <= end_date)
            df_exp_filtered = df_exp.loc[mask_exp]

            # 2. Извлечение KPI
            total_fortune = get_val_by_label(df_dash, "FORTUNE")
            cash = get_val_by_label(df_dash, "CASH")
            invest = get_val_by_label(df_dash, "INVESTISSEMENTS")
            assets_val = get_val_by_label(df_dash, "ASSETS")
            dette = get_val_by_label(df_dash, "DETTE")
            
            health_score = 0.0
            for i in range(len(df_dash)):
                if "SANTÉ FINANCIÈRE" in str(df_dash.iloc[i, 4]):
                     health_score = safe_float(df_dash.iloc[i, 5])

            # --- ИНТЕРФЕЙС ---
            st.title("📊 Tableau de Bord")
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("FORTUNE TOTALE", f"{total_fortune:,.0f} €")
            k2.metric("CASH DISPONIBLE", f"{cash:,.0f} €")
            k3.metric("DETTE TOTALE", f"{dette:,.0f} €")
            k4.metric("SANTÉ FINANCIÈRE", f"{health_score:.2f}" if health_score > 0 else "N/A")

            st.write("") 

            c1, c2 = st.columns([2, 1])
            
            with c1:
                st.subheader("📈 Évolution de la Fortune")
                fig = px.area(df_fortune_filtered, x='Date', y='Fortune', color_discrete_sequence=['#10B981'])
                fig.update_layout(xaxis_title="", yaxis_title="", height=350, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.subheader("🍩 Allocation actuelle")
                # Аллокация обычно показывается на текущий момент, но мы можем использовать данные на конец периода
                fig_pie = px.pie(
                    values=[cash, invest, assets_val], 
                    names=['Cash', 'Invest.', 'Assets'],
                    hole=0.6,
                    color_discrete_sequence=['#34D399', '#3B82F6', '#FBBF24']
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            st.markdown("---")

            st.subheader("💶 Revenus vs Dépenses sur la période")
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=df_exp_filtered['Date'], y=df_exp_filtered['Revenus'], name='Revenus', marker_color='#10B981'))
            fig_bar.add_trace(go.Bar(x=df_exp_filtered['Date'], y=df_exp_filtered['Dépenses Total'], name='Dépenses', marker_color='#EF4444'))
            fig_bar.update_layout(barmode='group', height=350, template="plotly_white")
            st.plotly_chart(fig_bar, use_container_width=True)

    except Exception as e:
        st.error(f"Erreur d'affichage : {e}")
else:
    st.info("👋 Veuillez charger le fichier Excel dans la barre latérale.")