import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Конфигурация в стиле Lovable
st.set_page_config(page_title="Smart Finance Dashboard", layout="wide", page_icon="💰")

# Улучшенный CSS
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #E2E8F0;
        padding: 15px;
        border-radius: 12px;
    }
    .stPlotlyChart {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def safe_float(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or val == 'NaN': return 0.0
        # Убираем пробелы и символы валют, если они есть в строке
        if isinstance(val, str):
            val = val.replace('€', '').replace(' ', '').replace(',', '.')
        return float(val)
    except:
        return 0.0

# Функция для поиска значения рядом с ключевым словом (надежнее, чем статические индексы)
def get_val_by_label(df, label):
    try:
        for i in range(len(df)):
            for j in range(len(df.columns)):
                cell_val = str(df.iloc[i, j])
                if label in cell_val:
                    return safe_float(df.iloc[i, j+1])
        return 0.0
    except:
        return 0.0

st.sidebar.title("💎 Smart Finance")
uploaded_file = st.sidebar.file_uploader("Charger le fichier .xlsx", type="xlsx")

if uploaded_file:
    try:
        # 1. Загрузка данных
        # Лист Dashboard считываем целиком для поиска меток
        df_dash = pd.read_excel(uploaded_file, sheet_name="💰 Dashboard Financier", header=None)
        
        # Лист Fortune (ищем начало таблицы)
        df_fortune = pd.read_excel(uploaded_file, sheet_name="🏦 Allocation de Fortune", skiprows=1)
        df_fortune = df_fortune.dropna(subset=['Date', 'Fortune'])
        
        # Лист Dépenses
        df_exp = pd.read_excel(uploaded_file, sheet_name="🍾 Dépenses ", skiprows=1)
        df_exp = df_exp.dropna(subset=['Date'])

        # 2. Извлечение данных через поиск меток (Гарантирует точность)
        total_fortune = get_val_by_label(df_dash, "FORTUNE")
        cash = get_val_by_label(df_dash, "CASH")
        invest = get_val_by_label(df_dash, "INVESTISSEMENTS")
        assets_val = get_val_by_label(df_dash, "ASSETS")
        dette = get_val_by_label(df_dash, "DETTE")
        # Для здоровья ищем в колонке F (индекс 5)
        health_score = 0.0
        for i in range(len(df_dash)):
            if "SANTÉ FINANCIÈRE" in str(df_dash.iloc[i, 4]): # Проверка колонки E
                 health_score = safe_float(df_dash.iloc[i, 5])

        # --- ИНТЕРФЕЙС ---
        st.title("📊 Tableau de Bord")
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("FORTUNE TOTALE", f"{total_fortune:,.0f} €")
        k2.metric("CASH DISPONIBLE", f"{cash:,.0f} €")
        k3.metric("DETTE TOTALE", f"{dette:,.0f} €")
        k4.metric("SANTÉ FINANCIÈRE", f"{health_score:.2f}" if health_score > 0 else "N/A")

        st.write("") # Отступ

        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("📈 Évolution de la Fortune")
            fig = px.area(df_fortune, x='Date', y='Fortune', color_discrete_sequence=['#10B981'])
            fig.update_layout(xaxis_title="", yaxis_title="", height=350, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("🍩 Allocation")
            fig_pie = px.pie(
                values=[cash, invest, assets_val], 
                names=['Cash', 'Invest.', 'Assets'],
                hole=0.6,
                color_discrete_sequence=['#34D399', '#3B82F6', '#FBBF24']
            )
            fig_pie.update_layout(height=350, margin=dict(l=0,r=0,t=30,b=0), showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")

        # Нижний ряд: Revenus vs Dépenses
        st.subheader("💶 Flux de Trésorerie (Derniers 12 mois)")
        # Берем последние 12 месяцев с данными
        df_plot = df_exp[df_exp['Dépenses Total'] > 0].tail(12)
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=df_plot['Date'], y=df_plot['Revenus'], name='Revenus', marker_color='#10B981'))
        fig_bar.add_trace(go.Bar(x=df_plot['Date'], y=df_plot['Dépenses Total'], name='Dépenses', marker_color='#EF4444'))
        fig_bar.update_layout(barmode='group', height=350, template="plotly_white", margin=dict(t=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    except Exception as e:
        st.error(f"Erreur d'affichage : {e}")
        st.info("Vérifiez que le fichier Excel contient les feuilles : '💰 Dashboard Financier', '🏦 Allocation de Fortune', '🍾 Dépenses '")
else:
    st.info("👋 Veuillez charger le fichier Excel pour afficher les données.")