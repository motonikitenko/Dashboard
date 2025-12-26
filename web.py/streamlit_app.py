import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Financial Dashboard", layout="wide")

st.title("📊 Финансовый Дашборд из Excel")

# Загрузка файла
uploaded_file = st.file_uploader("Выберите файл .xlsm или .xlsx", type=['xlsm', 'xlsx'])

if uploaded_file:
    # Чтение данных (аналог листов sheet1, sheet2 в вашем файле)
    # Используем engine='openpyxl' для поддержки .xlsm
    df = pd.read_excel(uploaded_file, sheet_name=0) 

    # Боковая панель с фильтрами (аналог Slicers в Excel)
    st.sidebar.header("Фильтры")
    selected_category = st.sidebar.multiselect(
        "Выберите категорию:",
        options=df.iloc[:, 0].unique(), # Предположим, категории в 1-м столбце
        default=df.iloc[:, 0].unique()
    )

    # Фильтрация данных
    filtered_df = df[df.iloc[:, 0].isin(selected_category)]

    # Основные показатели (KPI)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Общий доход", f"{filtered_df.iloc[:, 1].sum():,.0f} ₽")
    with col2:
        st.metric("Количество операций", len(filtered_df))
    
    # Визуализация (аналог графиков chart1, chart2 из вашего файла [cite: 74, 111])
    st.subheader("Анализ данных")
    
    c1, c2 = st.columns(2)
    with c1:
        # Линейный график
        fig_line = px.line(filtered_df, title="Динамика показателей")
        st.plotly_chart(fig_line, use_container_width=True)
        
    with c2:
        # Круговая диаграмма
        fig_pie = px.pie(filtered_df, names=df.columns[0], values=df.columns[1], title="Распределение")
        st.plotly_chart(fig_pie, use_container_width=True)

    # Таблица данных
    with st.expander("Посмотреть исходные данные"):
        st.dataframe(filtered_df)
else:
    st.info("Пожалуйста, загрузите Excel-файл для начала работы.")