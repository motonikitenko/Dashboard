import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(
    page_title="Financial Dashboard | Dark Mode",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- DARK UI CSS (Стиль Lovable Dark) ---
st.markdown("""
    <style>
    /* Фон всего приложения */
    .stApp {
        background-color: #020617;
        color: #F8FAFC;
    }
    
    /* Сайдбар */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    
    /* Карточки KPI */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    }
    
    /* Текст внутри метрик */
    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-weight: 500;
    }
    
    div[data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-weight: 700;
    }

    /* Заголовки */
    h1, h2, h3 {
        color: #F1F5F9 !important;
    }

    /* Таблица данных */
    .stDataFrame {
        background-color: #0F172A;
        border-radius: 8px;
    }

    /* Настройка инпутов и кнопок */
    .stMultiSelect div[role="listbox"] {
        background-color: #1E293B;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ОСНОВНОЙ КОНТЕНТ ---
st.title("🌙 Финансовая Аналитика (Dark Mode)")
st.markdown("<p style='color: #94A3B8;'>Интеллектуальный анализ ваших данных из Excel</p>", unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader("Загрузить файл .xlsm", type=['xlsm', 'xlsx'])

if uploaded_file:
    try:
        @st.cache_data
        def load_data(file):
            df = pd.read_excel(file, engine='openpyxl')
            df = df.dropna(how='all').dropna(axis=1, how='all')
            return df

        df = load_data(uploaded_file)

        if not df.empty:
            cat_col = df.columns[0]
            val_col = df.columns[1]
            
            # Приведение типов
            df[val_col] = pd.to_numeric(df[val_col], errors='coerce')
            df = df.dropna(subset=[val_col])

            # Сайдбар фильтры
            st.sidebar.divider()
            selected_cats = st.sidebar.multiselect(
                f"Выбор {cat_col}", 
                options=df[cat_col].unique(),
                default=df[cat_col].unique()[:5] # По умолчанию берем первые 5 для наглядности
            )
            
            display_df = df[df[cat_col].isin(selected_cats)]

            # --- МЕТРИКИ ---
            m1, m2, m3, m4 = st.columns(4)
            
            total_val = display_df[val_col].sum()
            avg_val = display_df[val_col].mean()
            
            m1.metric("Баланс", f"${total_val:,.0f}", "+8%")
            m2.metric("Ср. доход", f"${avg_val:,.2f}", "+2.5%")
            m3.metric("Записей", len(display_df))
            m4.metric("Статус", "Active", delta_color="normal")

            st.write("##")

            # --- ГРАФИКИ (Адаптированные под темную тему) ---
            col_chart1, col_chart2 = st.columns([2, 1])

            with col_chart1:
                st.subheader("Тренд доходности")
                # Используем темный шаблон plotly_dark
                fig_area = px.area(
                    display_df, x=cat_col, y=val_col,
                    color_discrete_sequence=['#38BDF8'], # Голубой акцент
                    template="plotly_dark"
                )
                fig_area.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, color="#94A3B8"),
                    yaxis=dict(showgrid=True, gridcolor='#1E293B', color="#94A3B8"),
                    margin=dict(l=0, r=0, t=10, b=0)
                )
                st.plotly_chart(fig_area, use_container_width=True)

            with col_chart2:
                st.subheader("Распределение")
                fig_donut = px.pie(
                    display_df, names=cat_col, values=val_col,
                    hole=0.6,
                    color_discrete_sequence=px.colors.qualitative.T10,
                    template="plotly_dark"
                )
                fig_donut.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=10, b=0),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3)
                )
                st.plotly_chart(fig_donut, use_container_width=True)

            # --- ТАБЛИЦА ---
            st.write("##")
            st.subheader("Детальный реестр")
            st.dataframe(display_df, use_container_width=True)

    except Exception as e:
        st.error(f"Ошибка: {e}")
else:
    st.info("🌑 Режим ожидания. Пожалуйста, загрузите .xlsm файл для активации дашборда.")
    # Заглушка (Empty state)
    st.image("https://images.unsplash.com/photo-1551288049-bbbda546697a?q=80&w=2070&auto=format&fit=crop", caption="Data visualization engine")