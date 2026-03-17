import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# 1. Configuração da Página
st.set_page_config(
    page_title="Analytics Dashboard | Insight Clarity",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Tema no Session State
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Configurações Dinâmicas de Tema
if st.session_state.theme == 'light':
    bg_main = "#F8FAFC"
    card_bg_purple = "linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%)"
    card_bg_blue = "linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)"
    card_bg_green = "linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%)"
    card_bg_yellow = "linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%)"
    text_headline = "#1E293B"
    text_body = "#64748B"
    border_color = "#E2E8F0"
    plotly_template = "plotly_white"
    card_shadow = "0 4px 6px -1px rgba(0, 0, 0, 0.05)"
else:
    bg_main = "#0F172A"
    card_bg_purple = "linear-gradient(135deg, #312E81 0%, #1E293B 100%)"
    card_bg_blue = "linear-gradient(135deg, #1E3A8A 0%, #1E293B 100%)"
    card_bg_green = "linear-gradient(135deg, #064E3B 0%, #1E293B 100%)"
    card_bg_yellow = "linear-gradient(135deg, #78350F 0%, #1E293B 100%)"
    text_headline = "#F8FAFC"
    text_body = "#94A3B8"
    border_color = "#334155"
    plotly_template = "plotly_dark"
    card_shadow = "0 4px 6px -1px rgba(0, 0, 0, 0.3)"

# Clean Corporate CSS (v4.0)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');

    .stApp {{
        background-color: {bg_main};
        color: {text_body};
        font-family: 'Inter', sans-serif;
    }}

    /* Modern Sidebar with Premium Blue Gradient */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #1E3A8A 0%, #2563EB 100%) !important;
        border-right: none;
    }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: white !important;
    }}
    [data-testid="stSidebar"] .stWidgetLabel p {{
        color: white !important;
    }}
    [data-testid="stSidebar"] h3 {{
        color: white !important;
    }}
    /* Manter o texto dos inputs lúdico (escuro) para leitura no fundo branco */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * {{
        color: #1E293B !important;
    }}
    [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] * {{
        color: #1E293B !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.2) !important;
    }}
    /* Estilização específica para o rádio e botão no sidebar */
    [data-testid="stSidebar"] .stRadio label {{
        color: white !important;
    }}
    [data-testid="stSidebar"] button {{
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
    }}

    /* Standardized Floating KPI Cards */
    .kpi-card {{
        background: {card_bg_purple};
        border: 1px solid {border_color};
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: {card_shadow};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 160px; /* Padronização de Altura */
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    .kpi-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }}
    .kpi-label {{
        font-size: 0.75rem;
        font-weight: 600;
        color: {text_body};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }}
    .kpi-value {{
        font-size: 1.85rem;
        font-weight: 700;
        color: {text_headline};
    }}
    .kpi-delta {{
        font-size: 0.8rem;
        font-weight: 600;
        color: #10B981;
        margin-top: 0.5rem;
    }}

    /* Ensure Sidebar Toggle button is always visible and has correct color */
    button[data-testid="bundle--static-button--sidebar-collapsible"] {{
        color: white !important;
    }}

    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# Carregar variáveis de ambiente
load_dotenv()

# 2. Conexão com o Banco (Supabase)
@st.cache_resource
def get_engine():
    db_url = os.getenv("SUPABASE_URL")
    if not db_url:
        st.error("Erro: Variável de ambiente SUPABASE_URL não encontrada.")
        return None
    return create_engine(db_url)

def run_query(query):
    engine = get_engine()
    if engine:
        try:
            with engine.connect() as conn:
                return pd.read_sql(query, conn)
        except Exception as e:
            st.error(f"Erro ao executar query: {str(e)}")
            return pd.DataFrame()
    return pd.DataFrame()

# Sidebar - Tema e Navegação
with st.sidebar:
    st.markdown("<h3 style='font-weight: 700; color: white !important;'>Analytics Pro</h3>", unsafe_allow_html=True)
    
    # Theme Toggle
    theme_btn = st.button("🌙 Alternar Tema" if st.session_state.theme == 'light' else "☀️ Alternar Tema")
    if theme_btn:
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
        st.rerun()

    page = st.radio("Seções", ["Vendas", "Clientes", "Pricing"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"<p style='font-size: 0.75rem; color: #94A3B8;'>Enterprise Edition v4.0 | {st.session_state.theme.upper()} MODE</p>", unsafe_allow_html=True)

# Funções de Auxílio
def kpi_box(label, value, delta=None, style='purple'):
    bg = card_bg_purple
    if style == 'blue': bg = card_bg_blue
    elif style == 'green': bg = card_bg_green
    elif style == 'yellow': bg = card_bg_yellow

    delta_html = f"<div class='kpi-delta'>↑ {delta}</div>" if delta else ""
    st.markdown(f"""
    <div class="kpi-card" style="background: {bg};">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def format_currency(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Global Plotly Theme
template = plotly_template
brand_palette = ['#2563EB', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']

# --- PÁGINA 1: VENDAS ---
if page == "Vendas":
    st.title("📈 Dashboard de Vendas")
    st.markdown("---")

    # Filtro de Mês
    df_months = run_query("SELECT DISTINCT mes_venda, ano_venda FROM public_gold_sales.vendas_temporais ORDER BY ano_venda DESC, mes_venda DESC")
    if not df_months.empty:
        # Garantir tipo int para evitar erro de formatação se vier como float/null
        df_months['mes_venda'] = df_months['mes_venda'].astype(int)
        df_months['ano_venda'] = df_months['ano_venda'].astype(int)
        
        month_options = [f"{m:02d}/{a}" for m, a in zip(df_months['mes_venda'], df_months['ano_venda'])]
        selected_month_str = st.sidebar.selectbox("Filtrar por Mês (MM/AAAA):", ["Todos"] + month_options)
        
        if selected_month_str != "Todos":
            sel_m, sel_a = map(int, selected_month_str.split("/"))
            query_where = f"WHERE mes_venda = {sel_m} AND ano_venda = {sel_a}"
        else:
            query_where = ""
    else:
        query_where = ""

    # Carregar Dados
    query_vendas = f"SELECT * FROM public_gold_sales.vendas_temporais {query_where} ORDER BY data_venda DESC, hora_venda ASC"
    df_vendas = run_query(query_vendas)

    if not df_vendas.empty:
        # KPIs
        receita_total = df_vendas['receita_total'].sum()
        total_vendas = df_vendas['total_vendas'].sum()
        ticket_medio = receita_total / total_vendas if total_vendas > 0 else 0
        clientes_unicos = df_vendas['total_clientes_unicos'].max()

        col1, col2, col3, col4 = st.columns(4)
        mom_val = f"{df_vendas['percentual_mom'].mean():.1f}% vs MoM" if 'percentual_mom' in df_vendas.columns else None
        with col1: kpi_box("Receita Total", format_currency(receita_total), mom_val, style='blue')
        with col2: kpi_box("Total de Vendas", f"{total_vendas:,.0f}".replace(",", "."), "+ 14.2% daily", style='green')
        with col3: kpi_box("Ticket Médio", format_currency(df_vendas['ticket_medio'].mean()), style='yellow')
        with col4: kpi_box("Clientes Únicos", f"{clientes_unicos:,.0f}".replace(",", "."), style='purple')

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráficos
        col_g1, col_g2 = st.columns([2, 1])

        with col_g1:
            df_diario = df_vendas.groupby('data_venda')['receita_total'].sum().reset_index()
            fig_diario = px.line(df_diario, x='data_venda', y='receita_total', title="Evolução Temporal da Receita", 
                               template=template, line_shape="spline", color_discrete_sequence=[brand_palette[0]])
            fig_diario.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_diario, use_container_width=True)

        with col_g2:
            ordem_dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            df_semanal = df_vendas.groupby('dia_semana_nome')['receita_total'].sum().reindex(ordem_dias).reset_index()
            fig_semanal = px.bar(df_semanal, x='dia_semana_nome', y='receita_total', title="Distribuição por Dia", 
                               template=template, color_discrete_sequence=[brand_palette[1]])
            fig_semanal.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_semanal, use_container_width=True)

        df_hora = df_vendas.groupby('hora_venda')['total_vendas'].sum().reset_index()
        fig_hora = px.bar(df_hora, x='hora_venda', y='total_vendas', title="Volume de Vendas por Hora", 
                        template=template, color_discrete_sequence=[brand_palette[2]])
        fig_hora.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_hora, use_container_width=True)
    else:
        st.warning("Nenhum dado de vendas disponível para o filtro selecionado.")

# --- PÁGINA 2: CLIENTES ---
elif page == "Clientes":
    st.title("👥 Dashboard de Clientes")
    st.markdown("---")

    query_clientes = "SELECT * FROM public_gold_cs.clientes_segmentacao"
    df_clientes = run_query(query_clientes)

    if not df_clientes.empty:
        # Filtro Sidebar
        segmento_filtro = st.sidebar.selectbox("Filtrar Segmento:", ["Todos"] + list(df_clientes['segmento_cliente'].unique()))
        if segmento_filtro != "Todos":
            df_filtered = df_clientes[df_clientes['segmento_cliente'] == segmento_filtro]
        else:
            df_filtered = df_clientes

        # KPIs
        total_clientes = len(df_clientes)
        clientes_vip = len(df_clientes[df_clientes['segmento_cliente'] == 'VIP'])
        receita_vip = df_clientes[df_clientes['segmento_cliente'] == 'VIP']['receita_total'].sum()
        ticket_medio_geral = df_clientes['ticket_medio'].mean()

        col1, col2, col3, col4 = st.columns(4)
        with col1: kpi_box("Base Total", f"{total_clientes:,.0f}".replace(",", "."), style='purple')
        with col2: kpi_box("Segmento VIP", f"{clientes_vip:,.0f}".replace(",", "."), f"{(clientes_vip/total_clientes)*100:.1f}% base", style='blue')
        with col3: kpi_box("Receita VIP", format_currency(receita_vip), style='green')
        with col4: kpi_box("Ticket Médio", format_currency(ticket_medio_geral), style='yellow')

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráficos
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            df_segmento = df_clientes['segmento_cliente'].value_counts().reset_index()
            df_segmento.columns = ['segmento', 'count']
            fig_seg = px.pie(df_segmento, names='segmento', values='count', title="Distribuição por Tier", 
                           hole=0.6, template=template, color_discrete_sequence=brand_palette)
            fig_seg.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_seg, use_container_width=True)

        with col_c2:
            df_rec_seg = df_clientes.groupby('segmento_cliente')['receita_total'].sum().reset_index()
            fig_rec_seg = px.bar(df_rec_seg, x='segmento_cliente', y='receita_total', title="Receita Global por Tier", 
                               template=template, color_discrete_sequence=[brand_palette[0]])
            fig_rec_seg.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_rec_seg, use_container_width=True)

        col_c3, col_c4 = st.columns(2)

        with col_c3:
            df_top = df_clientes.sort_values('ranking_receita').head(10)
            fig_top = px.bar(df_top, x='receita_total', y='nome_cliente', orientation='h', title="Top 10 Clientes por Receita", labels={'receita_total': 'Receita (R$)', 'nome_cliente': 'Cliente'})
            fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_top, use_container_width=True)

        with col_c4:
            df_estado = df_clientes['estado'].value_counts().reset_index()
            df_estado.columns = ['estado', 'count']
            fig_estado = px.bar(df_estado, x='estado', y='count', title="Clientes por Estado", labels={'count': 'Qtd Clientes', 'estado': 'UF'})
            st.plotly_chart(fig_estado, use_container_width=True)

        st.subheader("Detalhes dos Clientes")
        st.dataframe(df_filtered.drop(columns=['cliente_id']), use_container_width=True)
    else:
        st.warning("Nenhum dado de clientes disponível.")

# --- PÁGINA 3: PRICING ---
elif page == "Pricing":
    st.title("🏷️ Dashboard de Pricing")
    st.markdown("---")

    query_pricing = "SELECT * FROM public_gold_pricing.precos_competitividade"
    df_pricing = run_query(query_pricing)

    if not df_pricing.empty:
        # Filtro Categoria
        categorias = list(df_pricing['categoria'].unique())
        cat_filtro = st.sidebar.multiselect("Filtrar Categoria:", categorias, default=categorias)
        
        df_filtered = df_pricing[df_pricing['categoria'].isin(cat_filtro)]

        # KPIs
        total_prod = len(df_pricing)
        mais_caros = len(df_pricing[df_pricing['classificacao_preco'] == 'MAIS_CARO_QUE_TODOS'])
        mais_baratos = len(df_pricing[df_pricing['classificacao_preco'] == 'MAIS_BARATO_QUE_TODOS'])
        dif_media = df_pricing['diferenca_percentual_vs_media'].mean()

        col1, col2, col3, col4 = st.columns(4)
        with col1: kpi_box("SKUs Ativos", f"{total_prod:,.0f}".replace(",", "."), style='purple')
        with col2: kpi_box("Overpriced Alert", f"{mais_caros:,.0f}".replace(",", "."), "Ação recomendada", style='yellow')
        with col3: kpi_box("Underpriced Opportunity", f"{mais_baratos:,.0f}".replace(",", "."), style='green')
        with col4: kpi_box("Market Index", f"{dif_media:+.1f}%", "vs competitors", style='blue')

        st.markdown("<br>", unsafe_allow_html=True)

        col_p1, col_p2 = st.columns(2)

        with col_p1:
            df_class = df_pricing['classificacao_preco'].value_counts().reset_index()
            df_class.columns = ['classificacao', 'count']
            fig_class = px.pie(df_class, names='classificacao', values='count', title="Posicionamento de Mercado", 
                             template=template, hole=0.6, color_discrete_sequence=brand_palette)
            fig_class.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_class, use_container_width=True)

        with col_p2:
            df_cat_dif = df_filtered.groupby('categoria')['diferenca_percentual_vs_media'].mean().reset_index()
            df_cat_dif = df_cat_dif.sort_values('diferenca_percentual_vs_media')
            fig_cat = px.bar(df_cat_dif, x='categoria', y='diferenca_percentual_vs_media', 
                             title="Índice de Competitividade por Setor",
                             template=template,
                             color='diferenca_percentual_vs_media',
                             color_continuous_scale=['#10B981', '#F59E0B', '#EF4444'])
            fig_cat.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_cat, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        fig_scatter = px.scatter(df_filtered, x='diferenca_percentual_vs_media', y='quantidade_total', 
                                 size='receita_total', color='classificacao_preco',
                                 hover_name='nome_produto', title="Relatividade Preço x Volume Coletado",
                                 template=template, color_discrete_sequence=brand_palette)
        fig_scatter.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.subheader("⚠️ Alertas: Produtos mais caros que toda a concorrência")
        df_alerta = df_pricing[df_pricing['classificacao_preco'] == 'MAIS_CARO_QUE_TODOS']
        cols_alerta = ['produto_id', 'nome_produto', 'categoria', 'nosso_preco', 'preco_maximo_concorrentes', 'diferenca_percentual_vs_media']
        st.dataframe(df_alerta[cols_alerta], use_container_width=True)

    else:
        st.warning("Nenhum dado de pricing disponível.")
