import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Настройка страницы в стиле Dashboard
st.set_page_config(page_title="Financial Dashboard", layout="wide", initial_sidebar_state="expanded")

# Кастомный CSS для стилизации карточек как в современном UI
st.markdown("""
    <style>
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💹 Финансовый аналитик: Дашборд")

# Загрузка файла
uploaded_file = st.sidebar.file_uploader("Загрузите ваш .xlsm файл", type=['xlsm', 'xlsx'])

if uploaded_file:
    # Загружаем данные (автоматически читаем первый лист с данными)
    @st.cache_data
    def load_data(file):
        return pd.read_excel(file, engine='openpyxl')

    df = load_data(uploaded_file)

    # --- САЙДБАР (Фильтры как на Lovable) ---
    st.sidebar.header("Фильтры")
    # Предположим, в файле есть столбцы 'Дата' и 'Категория'
    if 'Категория' in df.columns:
        categories = st.sidebar.multiselect("Выберите категории", options=df['Категория'].unique(), default=df['Категория'].unique())
        df = df[df['Категория'].isin(categories)]

    # --- ВЕРХНИЕ КАРТОЧКИ (KPI) ---
    col1, col2, col3, col4 = st.columns(4)
    
    # Пример расчета метрик (замените на ваши столбцы)
    total_revenue = df.iloc[:, 1].sum() # Сумма второго столбца
    avg_check = df.iloc[:, 1].mean()
    
    col1.metric("Общая выручка", f"${total_revenue:,.2f}", "+5.2%")
    col2.metric("Средний чек", f"${avg_check:,.2f}", "-1.1%")
    col3.metric("Сделки", len(df), "+12")
    col4.metric("Маржа", "32%", "+2%")

    # --- ГРАФИКИ (Визуализация как в Excel/Lovable) ---
    st.markdown("---")
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("Динамика доходов")
        # Создаем линейный график Plotly (Style 17 из вашего Excel)
        fig_line = px.line(df, x=df.columns[0], y=df.columns[1], template="plotly_white", 
                           color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig_line, use_container_width=True)

    with row1_col2:
        st.subheader("Распределение по сегментам")
        # Кольцевая диаграмма (Donut chart)
        fig_pie = px.pie(df, names=df.columns[0], values=df.columns[1], hole=0.5)
        fig_pie.update_layout(showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- НИЖНЯЯ СЕКЦИЯ (Детальная таблица) ---
    st.subheader("Детальный анализ данных")
    st.dataframe(df, use_container_width=True)

else:
    st.info("👆 Пожалуйста, загрузите файл Demo Dashboard Financier.xlsm в боковую панель.")