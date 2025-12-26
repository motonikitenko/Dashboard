import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Настройка страницы
st.set_page_config(
    page_title="Financial Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Кастомный CSS для создания эффекта карточек (как в современных веб-приложениях)
st.markdown("""
    <style>
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #f0f2f6;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #1E293B;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Загрузка данных
st.title("📊 Финансовый Дашборд")

uploaded_file = st.sidebar.file_uploader("Загрузите файл .xlsm", type=['xlsm', 'xlsx'])

if uploaded_file:
    try:
        # Читаем данные. Мы используем engine='openpyxl' для файлов с макросами.
        # В файле Demo Dashboard Financier данные обычно находятся на Sheet1
        @st.cache_data
        def get_data(file):
            data = pd.read_excel(file, engine='openpyxl')
            # Очистка: удаляем полностью пустые строки и столбцы
            data = data.dropna(how='all').dropna(axis=1, how='all')
            return data

        df = get_data(uploaded_file)

        # --- КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ ОШИБКИ (TypeError) ---
        # Мы предполагаем, что 2-й столбец (индекс 1) - это сумма.
        # errors='coerce' превратит текст в NaN, чтобы sum() не падал.
        numeric_revenue = pd.to_numeric(df.iloc[:, 1], errors='coerce')
        
        # --- ФИЛЬТРЫ (Сайдбар) ---
        st.sidebar.subheader("Настройки отображения")
        # Берем первый столбец (обычно даты или категории) для фильтра
        if not df.empty:
            categories = df.iloc[:, 0].dropna().unique()
            selected = st.sidebar.multiselect("Фильтр по категориям", categories, default=categories)
            
            # Применяем фильтр
            mask = df.iloc[:, 0].isin(selected)
            df_filtered = df[mask]
            numeric_revenue_filtered = pd.to_numeric(df_filtered.iloc[:, 1], errors='coerce')
        else:
            df_filtered = df
            numeric_revenue_filtered = numeric_revenue

        # --- ВЕРХНИЕ МЕТРИКИ (KPI) ---
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Общая выручка", f"${numeric_revenue_filtered.sum():,.2f}")
        with col2:
            st.metric("Средний чек", f"${numeric_revenue_filtered.mean():,.2f}")
        with col3:
            st.metric("Транзакции", f"{numeric_revenue_filtered.count():,}")
        with col4:
            st.metric("Макс. чек", f"${numeric_revenue_filtered.max():,.2f}")

        st.markdown("---")

        # --- ГРАФИКИ ---
        row1_col1, row1_col2 = st.columns([2, 1])

        with row1_col1:
            st.subheader("Линейный анализ (Тренд)")
            # Создаем график, используя 1-й столбец как X и 2-й как Y
            fig_trend = px.line(
                df_filtered, 
                x=df_filtered.columns[0], 
                y=df_filtered.columns[1],
                template="plotly_white",
                color_discrete_sequence=['#3B82F6'] # Синий цвет как в Lovable
            )
            fig_trend.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_trend, use_container_width=True)

        with row1_col2:
            st.subheader("Структура (Pie)")
            fig_pie = px.pie(
                df_filtered, 
                names=df_filtered.columns[0], 
                values=df_filtered.columns[1],
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)

        # --- ТАБЛИЦА ---
        st.subheader("Детальный просмотр")
        st.dataframe(df_filtered, use_container_width=True)

    except Exception as e:
        st.error(f"Ошибка при обработке файла: {e}")
        st.info("Убедитесь, что данные в Excel начинаются с первой строки и во втором столбце находятся числа.")

else:
    # Заглушка, если файл не загружен
    st.info("👋 Добро пожаловать! Пожалуйста, загрузите ваш файл 'Demo Dashboard Financier.xlsm' слева.")
    
    # Визуальная имитация дашборда для красоты
    ```

### Что было исправлено и добавлено:
1.  [cite_start]**Защита от `TypeError`**: Использование `pd.to_numeric(..., errors='coerce')` гарантирует, что программа не «сломается», если в данных встретится текст или пустая ячейка[cite: 71, 75].
2.  [cite_start]**Обработка `.xlsm`**: Добавлен движок `openpyxl`, который корректно работает с файлами Excel, содержащими макросы[cite: 71].
3.  **Динамические фильтры**: Код автоматически берет уникальные значения из первого столбца вашего листа для создания фильтров в боковой панели.
4.  **Стиль Lovable**: 
    * Использованы сетки `st.columns` для KPI и графиков.
    * Добавлен `st.markdown` с CSS для стилизации карточек метрик.
    * [cite_start]Использован шаблон `plotly_white` для графиков, чтобы они выглядели «чисто», как в современных веб-интерфейсах[cite: 74, 110].

### Как запустить:
1.  Установите библиотеки: `pip install streamlit pandas openpyxl plotly`.
2.  Сохраните код в файл `app.py`.
3.  Запустите командой: `streamlit run app.py`.