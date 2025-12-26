import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Smart Finance Dashboard", layout="wide", page_icon="💰")

# Функция для безопасного извлечения чисел
def safe_float(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or val == 'NaN':
            return 0.0
        return float(val)
    except:
        return 0.0

st.title("💼 Финансовое приложение Smart Finance")

uploaded_file = st.file_uploader("Загрузите 'Demo Dashboard Financier.xlsx'", type="xlsx")

if uploaded_file:
    try:
        # 1. Загрузка данных
        df_dash = pd.read_excel(uploaded_file, sheet_name="💰 Dashboard Financier", header=None)
        df_fortune = pd.read_excel(uploaded_file, sheet_name="🏦 Allocation de Fortune", skiprows=1).dropna(subset=['Date', 'Fortune'])
        df_exp = pd.read_excel(uploaded_file, sheet_name="🍾 Dépenses ", skiprows=1).dropna(subset=['Date'])
        
        # 2. KPI блок (из первого листа)
        total_fortune = safe_float(df_dash.iloc[1, 2])
        cash = safe_float(df_dash.iloc[3, 2])
        investments = safe_float(df_dash.iloc[5, 2])
        assets_val = safe_float(df_dash.iloc[7, 2])
        dette = safe_float(df_dash.iloc[9, 2])
        health_score = safe_float(df_dash.iloc[18, 5])

        # Отображение метрик
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💰 Капитал (Total)", f"€{total_fortune:,.0f}")
        m2.metric("💸 Наличные", f"€{cash:,.0f}")
        m3.metric("🧨 Долг", f"€{dette:,.0f}", delta_color="inverse")
        m4.metric("🩺 Здоровье", f"{health_score:.2f}" if health_score > 0 else "Н/Д")

        st.markdown("---")

        # 3. Визуализация как на листе Dashboard
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("📊 Состав Капитала (Allocation)")
            # Создаем данные для круговой диаграммы на основе KPI
            labels = ['Наличные (Cash)', 'Инвестиции', 'Активы (Assets)']
            values = [cash, investments, assets_val]
            
            fig_donut = px.pie(
                values=values, 
                names=labels, 
                hole=0.5,
                color_discrete_sequence=['#2ecc71', '#3498db', '#f1c40f']
            )
            fig_donut.update_layout(showlegend=True)
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_right:
            st.subheader("📈 История роста капитала")
            fig_area = px.area(df_fortune, x='Date', y='Fortune',
                               labels={'Fortune': 'Сумма €', 'Date': 'Месяц'},
                               color_discrete_sequence=['#27ae60'])
            st.plotly_chart(fig_area, use_container_width=True)

        st.markdown("---")

        # 4. Сравнение Доходов и Расходов (нижняя часть Dashboard)
        col_bot1, col_bot2 = st.columns([2, 1])

        with col_bot1:
            st.subheader("📊 Доходы vs Расходы по месяцам")
            # Фильтруем только строки, где есть данные
            df_plot = df_exp[(df_exp['Revenus'] > 0) | (df_exp['Dépenses Total'] > 0)]
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=df_plot['Date'], y=df_plot['Revenus'], name='Доходы', marker_color='#2ecc71'))
            fig_bar.add_trace(go.Bar(x=df_plot['Date'], y=df_plot['Dépenses Total'], name='Расходы', marker_color='#e74c3c'))
            fig_bar.update_layout(barmode='group', height=400, margin=dict(t=20))
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_bot2:
            st.subheader("🍕 Категории трат")
            categories = ['Logement', 'Nourriture', 'Transport', 'Sorties', 'Divers', 'Services', 'Achats']
            available_cats = [c for c in categories if c in df_exp.columns]
            
            if not df_exp.empty:
                # Берем данные последнего заполненного месяца
                last_row = df_exp[df_exp['Dépenses Total'] > 0].iloc[-1]
                pie_vals = [safe_float(last_row[c]) for c in available_cats]
                
                fig_exp_pie = px.pie(values=pie_vals, names=available_cats, hole=0.3)
                fig_exp_pie.update_layout(showlegend=False)
                st.plotly_chart(fig_exp_pie, use_container_width=True)

    except Exception as e:
        st.error(f"Ошибка при чтении структуры листа: {e}")
        st.info("Убедитесь, что используете оригинальный шаблон файла без удаления строк.")
else:
    st.info("👆 Загрузите файл Excel для генерации всех графиков.")