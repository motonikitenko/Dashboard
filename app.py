import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Настройка стиля страницы
st.set_page_config(page_title="Smart Finance Dashboard", layout="wide", page_icon="💰")

# Кастомный CSS для улучшения внешнего вида
"""st.markdown(
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    , unsafe_allow_html=True)
"""
st.title("💼 Финансовое приложение Smart Finance")
st.write("Загрузите файл 'Demo Dashboard Financier.xlsx' для получения аналитики")

# Загрузка файла
#uploaded_file = st.file_uploader("Выберите файл Excel", type="xlsx")
"""
if uploaded_file:
    try:
        # 1. Загружаем основные листы
        # Dashboard для KPI
        df_dash = pd.read_excel(uploaded_file, sheet_name="💰 Dashboard Financier", header=None)
        
        # Fortune для графика роста (пропускаем 1 строку заголовка)
        df_fortune = pd.read_excel(uploaded_file, sheet_name="🏦 Allocation de Fortune", skiprows=1)
        df_fortune = df_fortune[df_fortune['Fortune'] > 0] # Берем только заполненные данные
        
        # Dépenses для анализа трат
        df_exp = pd.read_excel(uploaded_file, sheet_name="🍾 Dépenses ", skiprows=1)
        df_exp = df_exp[df_exp['Dépenses Total'] > 0]

        # 2. Извлекаем KPI (координаты ячеек соответствуют вашему файлу)
        total_fortune = df_dash.iloc[1, 2] # "💰 FORTUNE"
        cash = df_dash.iloc[3, 2]          # "💸 CASH"
        dette = df_dash.iloc[7, 2]         # "🧨 DETTE"
        health_score = df_dash.iloc[18, 5] # "SANTÉ FINANCIÈRE"

        # Отображение метрик
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Общий капитал", f"€{total_fortune:,.0f}")
        col2.metric("Наличные", f"€{cash:,.0f}")
        col3.metric("Долг", f"€{dette:,.0f}", delta_color="inverse")
        col4.metric("Индекс здоровья", f"{health_score:.2f}")

        st.markdown("---")

        # 3. Визуализация
        row1_col1, row1_col2 = st.columns([2, 1])

        with row1_col1:
            st.subheader("📈 Динамика накоплений")
            fig_area = px.area(df_fortune, x='Date', y='Fortune', 
                               labels={'Fortune': 'Капитал', 'Date': 'Дата'},
                               color_discrete_sequence=['#2ecc71'])
            fig_area.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_area, use_container_width=True)

        with row1_col2:
            st.subheader("🍕 Категории трат")
            # Считаем суммы по категориям (последние данные)
            categories = ['Logement', 'Nourriture', 'Transport', 'Sorties', 'Divers', 'Services', 'Achats']
            if not df_exp.empty:
                last_month_values = df_exp[categories].iloc[-1]
                fig_pie = px.pie(values=last_month_values, names=categories, hole=0.5)
                st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        
        # График Доходы vs Расходы
        st.subheader("📊 Сравнение Доходов и Расходов")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=df_exp['Date'], y=df_exp['Revenus'], name='Доходы', marker_color='#2ecc71'))
        fig_bar.add_trace(go.Bar(x=df_exp['Date'], y=df_exp['Dépenses Total'], name='Расходы', marker_color='#e74c3c'))
        fig_bar.update_layout(barmode='group', height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

        # 4. Таблица активов
        with st.expander("📂 Посмотреть список всех активов (Машины, Часы и др.)"):
            df_assets = pd.read_excel(uploaded_file, sheet_name="🚗 Assets", skiprows=2)
            df_assets = df_assets.dropna(subset=['Item'])
            st.dataframe(df_assets[['Catégorie', 'Item', 'Prix d\'achat', 'Valeur Réel', 'P/L']], use_container_width=True)

    except Exception as e:
        st.error(f"Произошла ошибка при обработке файла. Убедитесь, что листы не переименованы. Ошибка: {e}")
else:
    st.info("👆 Пожалуйста, загрузите ваш Excel файл, чтобы увидеть дашборд.")
"""