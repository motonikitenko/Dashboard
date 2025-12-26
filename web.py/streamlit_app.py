import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Настройка страницы
st.set_page_config(
    page_title="Financial Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Стилизация карточек
st.markdown("""
    <style>
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Финансовый Дашборд")

# 3. Загрузка файла
uploaded_file = st.sidebar.file_uploader("Загрузите файл .xlsm", type=['xlsm', 'xlsx'])

if uploaded_file:
    try:
        # Чтение данных с первого листа
        @st.cache_data
        def get_data(file):
            data = pd.read_excel(file, engine='openpyxl')
            # Удаляем полностью пустые строки
            data = data.dropna(how='all')
            return data

        df = get_data(uploaded_file)

        if not df.empty:
            # Безопасное преобразование 2-го столбца в числа
            # (индекс 1 - это второй столбец, где обычно суммы)
            numeric_col_name = df.columns[1]
            df[numeric_col_name] = pd.to_numeric(df[numeric_col_name], errors='coerce')
            
            # Очистка от строк, где сумма не определилась (NaN)
            df_clean = df.dropna(subset=[numeric_col_name])

            # --- ФИЛЬТРЫ ---
            st.sidebar.subheader("Настройки")
            first_col_name = df_clean.columns[0]
            categories = df_clean[first_col_name].unique()
            selected = st.sidebar.multiselect("Фильтр:", categories, default=categories)
            
            df_filtered = df_clean[df_clean[first_col_name].isin(selected)]

            # --- KPI МЕТРИКИ ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Общая сумма", f"{df_filtered[numeric_col_name].sum():,.2f}")
            with col2:
                st.metric("Средний чек", f"{df_filtered[numeric_col_name].mean():,.2f}")
            with col3:
                st.metric("Кол-во записей", f"{len(df_filtered)}")

            st.markdown("---")

            # --- ГРАФИКИ ---
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Линейный график")
                fig_line = px.line(df_filtered, x=first_col_name, y=numeric_col_name, template="plotly_white")
                st.plotly_chart(fig_line, use_container_width=True)
            
            with c2:
                st.subheader("Распределение")
                fig_pie = px.pie(df_filtered, names=first_col_name, values=numeric_col_name, hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)

            # --- ТАБЛИЦА ---
            with st.expander("Открыть таблицу данных"):
                st.dataframe(df_filtered, use_container_width=True)
        else:
            st.warning("Файл пуст.")

    except Exception as e:
        st.error(f"Произошла ошибка: {e}")
else:
    st.info("Пожалуйста, загрузите Excel файл в боковой панели.")