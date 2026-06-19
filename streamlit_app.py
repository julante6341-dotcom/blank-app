import pandas as pd

# --------------------------------------------------
# 1. Configuração da Página
# --------------------------------------------------
st.set_page_config(
    page_title="Market Performance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização para destacar as métricas primárias
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; }
    </style>
    """, unsafe_allowed_html=True)

st.title("📊 Market Performance Dashboard")
st.markdown("Visão integrada de performance de vendas, margens e comportamento de produtos do mercado.")
st.divider()

# --------------------------------------------------
# 2. Carregamento Inteligente dos Dados (Cache)
# --------------------------------------------------
@st.cache_data 
def load_data():
    # Nome alterado estritamente para o arquivo anexado
    file_name = "market.csv" 
    
    # NOTA: Se no seu arquivo a coluna de data se chamar 'Data' ou 'Data do Pedido', altere aqui:
    df = pd.read_csv(file_name, parse_dates=["Order Date"])
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Erro: O arquivo 'market.csv' não foi encontrado. Certifique-se de que ele está na raiz do seu repositório do GitHub.")
    st.stop()

# --------------------------------------------------
# 3. Painel Lateral de Filtros (Sidebar)
# --------------------------------------------------
st.sidebar.header("🎯 Filtros de Mercado")

# Filtro 1: Região / Mercado Regional
# (Se no CSV for 'Regiao', altere o texto dentro dos colchetes)
sorted_regions = sorted(df["Region"].unique())
regions = st.sidebar.multiselect(
    "Região de Mercado",
    options=sorted_regions,
    default=sorted_regions
)

# Filtro 2: Categoria de Produto
sorted_categories = sorted(df["Category"].unique())
categories = st.sidebar.multiselect(
    "Categoria",
    options=sorted_categories,
    default=sorted_categories
)

# Filtro 3: Linha do Tempo (Anos)
years = sorted(df["Order Date"].dt.year.unique())
year_range = st.sidebar.slider(
    "Intervalo Temporal (Anos)",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(int(min(years)), int(max(years)))
)

# Aplicação cirúrgica dos filtros no DataFrame de trabalho
filtered_df = df[
    (df["Region"].isin(regions)) &
    (df["Category"].isin(categories)) &
    (df["Order Date"].dt.year.between(year_range[0], year_range[1]))
]

# --------------------------------------------------
# 4. Indicadores Principais (KPIs)
# --------------------------------------------------
# Ajuste os termos "Sales", "Profit" e "Order ID" caso seu CSV utilize "Vendas", "Lucro", etc.
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
num_orders = filtered_df["Order ID"].nunique()
profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0

# Layout limpo em 4 colunas horizontais
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("💰 Faturamento Total", f"${total_sales:,.2f}")
kpi2.metric("📈 Lucro Líquido", f"${total_profit:,.2f}")
kpi3.metric("📦 Volume de Pedidos", f"{num_orders:,}")
kpi4.metric("📊 Margem Comercial", f"{profit_margin:.1f}%")

st.divider()

# --------------------------------------------------
# 5. Visualizações Gráficas Otimizadas
# --------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    # Gráfico de Linhas: O melhor para analisar comportamento e sazonalidade temporal
    st.subheader("📅 Tendência de Vendas por Categoria")
    
    sales_over_time = (
        filtered_df
        .groupby([pd.Grouper(key="Order Date", freq="ME"), "Category"])["Sales"]
        .sum()
        .reset_index()
    )
    
    sales_pivot = sales_over_time.pivot(
        index="Order Date",
        columns="Category",
        values="Sales"
    ).fillna(0)
    
    st.line_chart(sales_pivot)

with col_right:
    # Gráfico de Barras: O formato ideal para rankear e comparar fatias de mercado
    st.subheader("🌍 Participação de Vendas por Região")
    
    sales_by_region = (
        filtered_df
        .groupby("Region")["Sales"]
        .sum()
        .sort_values(ascending=True) # Barras ordenadas evitam poluição visual
    )
    
    st.bar_chart(sales_by_region)

st.divider()

# --------------------------------------------------
# 6. Tabela Estratégica (Rankings)
# --------------------------------------------------
# Gráficos de barras para dezenas de produtos ficam ilegíveis; tabelas ricas resolvem isso.
st.subheader("🏆 Top 10 Produtos em Destaque")

top_products = (
    filtered_df
    .groupby("Product Name")[["Sales", "Profit"]]
    .sum()
    .sort_values(by="Sales", ascending=False)
    .head(10)
)

st.dataframe(
    top_products.style.format({"Sales": "${:,.2f}", "Profit": "${:,.2f}"}),
    use_container_width=True
)

# --------------------------------------------------
# 7. Rodapé Técnico
# --------------------------------------------------
st.caption(f"Origem dos dados ativos: **{file_name}** | Estrutura adaptada para produção via GitHub.")
