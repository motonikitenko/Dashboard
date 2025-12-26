import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Smart Finance Dashboard", layout="wide", page_icon="💰")

# Кастомный CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("💼 Финансовое приложение Smart Finance")
st.write("Загрузите файл 'Demo Dashboard Financier.xlsx' для получения аналитики")

uploaded_file = st.file_uploader("Выберите файл Excel", type="xlsx")

# Функция для безопасной конвертации в число (исправляет вашу ошибку)
def safe_float(val):
    try:
        if pd.isna(val) or val == 'NaN':
            return 0.0
        return float(val)
    except:
        return 0.0

if uploaded_file:
    try:
        # 1. Загружаем основные листы
        df_dash = pd.read_excel(uploaded_file, sheet_name="💰 Dashboard Financier", header=None)
        
        df_fortune = pd.read_excel(uploaded_file, sheet_name="🏦 Allocation de Fortune", skiprows=1)
        # Очистка данных от пустых строк
        df_fortune = df_fortune.dropna(subset=['Date', 'Fortune'])
        df_fortune = df_fortune[df_fortune['Fortune'] > 0]

        df_exp = pd.read_excel(uploaded_file, sheet_name="🍾 Dépenses ", skiprows=1)
        df_exp = df_exp.dropna(subset=['Date'])

        # 2. Извлекаем KPI с использованием безопасной функции
        total_fortune = safe_float(df_dash.iloc[1, 2])
        cash = safe_float(df_dash.iloc[3, 2])
        dette = safe_float(df_dash.iloc[7, 2])
        
        # Здесь была главная ошибка: f"{health_score:.2f}" не работал из-за NaN
        health_score = safe_float(df_dash.iloc[18, 5])

        # Отображение метрик
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Общий капитал", f"€{total_fortune:,.0f}")
        col2.metric("Наличные", f"€{cash:,.0f}")
        col3.metric("Долг", f"€{dette:,.0f}", delta_color="inverse")
        
        # Условное отображение индекса здоровья
        if health_score == 0:
            col4.metric("Индекс здоровья", "Нет данных")
        else:
            col4.metric("Индекс здоровья", f"{health_score:.2f}")

        st.markdown("---")

        # 3. Визуализация
        row1_col1, row1_col2 = st.columns([2, 1])

        with row1_col1:
            st.subheader("📈 Динамика накоплений")
            if not df_fortune.empty:
                fig_area = px.area(df_fortune, x='Date', y='Fortune',
                                   labels={'Fortune': 'Капитал', 'Date': 'Дата'},
                                   color_discrete_sequence=['#2ecc71'])
                st.plotly_chart(fig_area, use_container_width=True)
            else:
                st.info("Недостаточно данных для графика динамики.")

        with row1_col2:
            st.subheader("🍕 Категории трат")
            categories = ['Logement', 'Nourriture', 'Transport', 'Sorties', 'Divers', 'Services', 'Achats']
            # Проверяем наличие колонок и данных
            available_cats = [c for c in categories if c in df_exp.columns]
            if not df_exp.empty and available_cats:
                last_month_values = df_exp[available_cats].iloc[-1].apply(safe_float)
                if last_month_values.sum() > 0:
                    fig_pie = px.pie(values=last_month_values, names=available_cats, hole=0.5)
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("В последнем месяце нет расходов.")

        st.markdown("---")

        # График Доходы vs Расходы
        st.subheader("📊 Сравнение Доходов и Расходов")
        if 'Revenus' in df_exp.columns and 'Dépenses Total' in df_exp.columns:
            # Очищаем данные от нулей для красоты графика
            df_plot = df_exp[(df_exp['Revenus'] > 0) | (df_exp['Dépenses Total'] > 0)]
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=df_plot['Date'], y=df_plot['Revenus'], name='Доходы', marker_color='#2ecc71'))
            fig_bar.add_trace(go.Bar(x=df_plot['Date'], y=df_plot['Dépenses Total'], name='Расходы', marker_color='#e74c3c'))
            fig_bar.update_layout(barmode='group', height=400)
            st.plotly_chart(fig_bar, use_container_width=True)

        # 4. Таблица активов
        with st.expander("📂 Посмотреть список всех активов"):
            df_assets = pd.read_excel(uploaded_file, sheet_name="🚗 Assets", skiprows=2)
            df_assets = df_assets.dropna(subset=['Item'])
            display_cols = ['Catégorie', 'Item', 'Prix d\'achat', 'Valeur Réel', 'P/L']
            # Берем только те колонки, которые есть в наличии
            existing_cols = [c for c in display_cols if c in df_assets.columns]
            st.dataframe(df_assets[existing_cols], use_container_width=True)

    except Exception as e:
        st.error(f"Ошибка при обработке: {e}")
        st.info("Подсказка: Проверьте, что в ячейках Dashboard нет ошибок типа #ДЕЛ/0!")
else:
    st.info("👆 Пожалуйста, загрузите ваш Excel файл.")