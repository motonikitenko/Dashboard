import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Настройка страницы в стиле веб-приложения
st.set_page_config(page_title="Smart Finance Dashboard", layout="wide", page_icon="💰")

# Кастомный CSS для создания эффекта карточек и чистого фона
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #1E293B; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; }
    .main { background-color: #F8FAFC; }
    </style>
    """, unsafe_allow_html=True)

def safe_float(val):
    try:
        if pd.isna(val) or str(val).strip() == "" or val == 'NaN':
            return 0.0
        return float(val)
    except:
        return 0.0

# --- SIDEBAR (Боковая панель) ---
st.sidebar.title("💎 Smart Finance")
st.sidebar.write("Gestion de Fortune")
uploaded_file = st.sidebar.file_uploader("Charger le fichier Excel", type="xlsx")

if uploaded_file:
    try:
        # Чтение данных
        df_dash = pd.read_excel(uploaded_file, sheet_name="💰 Dashboard Financier", header=None)
        df_fortune = pd.read_excel(uploaded_file, sheet_name="🏦 Allocation de Fortune", skiprows=1).dropna(subset=['Date', 'Fortune'])
        df_exp = pd.read_excel(uploaded_file, sheet_name="🍾 Dépenses ", skiprows=1).dropna(subset=['Date'])
        
        # Данные для KPI (Французские названия)
        total_fortune = safe_float(df_dash.iloc[1, 2])
        cash = safe_float(df_dash.iloc[3, 2])
        investments = safe_float(df_dash.iloc[5, 2])
        assets_val = safe_float(df_dash.iloc[7, 2])
        dette = safe_float(df_dash.iloc[9, 2])
        health_score = safe_float(df_dash.iloc[18, 5])
        
        # --- ВЕРХНЯЯ ПАНЕЛЬ KPI ---
        st.title("💰 Tableau de Bord Financier")
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric("FORTUNE TOTALE", f"{total_fortune:,.0f} €")
        with kpi2:
            st.metric("CASH DISPONIBLE", f"{cash:,.0f} €")
        with kpi3:
            st.metric("DETTE TOTALE", f"{dette:,.0f} €", delta_color="inverse")
        with kpi4:
            st.metric("SANTÉ FINANCIÈRE", f"{health_score:.2f}" if health_score > 0 else "N/A")

        st.markdown("---")

        # --- ОСНОВНОЙ КОНТЕНТ ---
        col_main_1, col_main_2 = st.columns([2, 1])

        with col_main_1:
            st.subheader("📈 Croissance de la Fortune")
            # График роста как в приложении
            fig_growth = px.area(df_fortune, x='Date', y='Fortune',
                                 color_discrete_sequence=['#10B981'])
            fig_growth.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                     xaxis_title="", yaxis_title="Fortune (€)")
            st.plotly_chart(fig_growth, use_container_width=True)

        with col_main_2:
            st.subheader("📊 Allocation d'Actifs")
            # Круговая диаграмма распределения
            labels = ['Cash', 'Investissements', 'Assets']
            values = [cash, investments, assets_val]
            fig_donut = px.pie(values=values, names=labels, hole=0.6,
                               color_discrete_sequence=['#34D399', '#3B82F6', '#FBBF24'])
            fig_donut.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2))
            st.plotly_chart(fig_donut, use_container_width=True)

        st.markdown("---")

        # --- НИЖНЯЯ ПАНЕЛЬ (Доходы и Расходы) ---
        col_bot_1, col_bot_2 = st.columns(2)

        with col_bot_1:
            st.subheader("💵 Revenus vs Dépenses")
            df_plot = df_exp[(df_exp['Revenus'] > 0) | (df_exp['Dépenses Total'] > 0)].tail(12)
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=df_plot['Date'], y=df_plot['Revenus'], name='Revenus', marker_color='#10B981'))
            fig_bar.add_trace(go.Bar(x=df_plot['Date'], y=df_plot['Dépenses Total'], name='Dépenses', marker_color='#EF4444'))
            fig_bar.update_layout(barmode='group', height=350, plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_bot_2:
            st.subheader("🍕 Répartition des Dépenses")
            categories = ['Logement', 'Nourriture', 'Transport', 'Sorties', 'Divers', 'Services', 'Achats']
            if not df_exp.empty:
                last_month = df_exp[df_exp['Dépenses Total'] > 0].iloc[-1]
                cat_vals = [safe_float(last_month[c]) for c in categories if c in df_exp.columns]
                cat_names = [c for c in categories if c in df_exp.columns]
                
                fig_exp = px.bar(x=cat_vals, y=cat_names, orientation='h', 
                                 color=cat_vals, color_continuous_scale='Greens')
                fig_exp.update_layout(showlegend=False, xaxis_title="Montant (€)", yaxis_title="")
                st.plotly_chart(fig_exp, use_container_width=True)

    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
else:
    # Красивое приветствие, если файл не загружен
    st.info("👋 Bienvenue ! Veuillez charger votre fichier 'Demo Dashboard Financier.xlsx' dans la barre latérale pour commencer l'analyse.")
    st.image("https://images.unsplash.com/photo-1551288049-bbb6518147ad?auto=format&fit=crop&q=80&w=1000", use_container_width=True)