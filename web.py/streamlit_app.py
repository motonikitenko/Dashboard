import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Настройка страницы в стиле современного дашборда
st.set_page_config(
    page_title="Financial Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Стилизация (CSS)
st.markdown("""
    <style>
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #f0f2f6;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #1E293B;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Финансовый Дашборд")

# 3. Загрузка файла в сайдбаре
uploaded_file = st.sidebar.file_uploader("Загрузите файл .xlsm или .xlsx", type=['xlsm', 'xlsx'])

if uploaded_file:
    try:
        # Чтение данных
        @st.cache_data
        def load_data(file):
            # Читаем данные, движок openpyxl обязателен для .xlsm
            df = pd.read_excel(file, engine='openpyxl')
            # Очистка от полностью пустых строк
            df = df.dropna(how='all')
            return df

        raw_df = load_data(uploaded_file)

        if not raw_df.empty:
            # Определяем колонки (первая - текст/дата, вторая - сумма)
            label_col = raw_df.columns[0]
            value_col = raw_df.columns[1]

            # Преобразование данных (защита от TypeError)
            raw_df[value_col] = pd.to_numeric(raw_df[value_col], errors='coerce')
            df_final = raw_df.dropna(subset=[value_col])

            # --- БОКОВАЯ ПАНЕЛЬ С ФИЛЬТРАМИ ---
            st.sidebar.header("Настройки")
            unique_vals = df_final[label_col].unique()
            selected = st.sidebar.multiselect(f"Фильтр по {label_col}:", unique_vals, default=unique_vals)
            
            # Применение фильтра
            filtered_df = df_final[df_final[label_col].isin(selected)]

            # --- ВЕРХНИЕ МЕТРИКИ (KPI) ---
            kpi1, kpi2, kpi3 = st.columns(3)
            with kpi1:
                st.metric("Итоговая сумма", f"{filtered_df[value_col].sum():,.2f}")
            with kpi2:
                st.metric("Средний показатель", f"{filtered_df[value_col].mean():,.2f}")
            with kpi3:
                st.metric("Всего записей", f"{len(filtered_df)}")

            st.markdown("---")

            # --- ГРАФИКИ (Визуализация) ---
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader("Временная зависимость / Тренды")
                fig_line = px.line(filtered_df, x=label_col, y=value_col, 
                                   template="plotly_white", markers=True)
                st.plotly_chart(fig_line, use_container_width=True)
                
            with col_right:
                st.subheader("Структура данных")
                fig_pie = px.pie(filtered_df, names=label_col, values=value_col, 
                                 hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
                st.plotly_chart(fig_pie, use_container_width=True)

            # --- ТАБЛИЦА С ДАННЫМИ ---
            with st.expander("Просмотреть детализированную таблицу"):
                st.dataframe(filtered_df, use_container_width=True)
        else:
            st.warning("Загруженный файл не содержит данных.")

    except Exception as e:
        st.error(f"Произошла ошибка при обработке: {e}")
else:
    st.info("Пожалуйста, загрузите Excel-файл (например, Demo Dashboard Financier.xlsm) через меню слева.")