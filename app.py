# app.py (VERSÃO COMPLETA E CORRIGIDA)
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash import no_update, ctx
import os # Necessário para criar a pasta assets

# Importamos as funções de gráfico que vamos usar
from eda_ouvidoria import (
    grafico_volume_tempo,
    grafico_genero,
    grafico_faixa_etaria,
    grafico_tipos,
    grafico_satisfacao,
    grafico_mapa,
    grafico_raca
)

ARQUIVO_PARQUET = "ouvidoria.parquet"
TEMA_GRAFICOS = "plotly_white" # Tema unificado

# --- 0. CRIAR PASTA ASSETS SE NÃO EXISTIR ---
# (Garante que o CSS seja carregado)
assets_dir = os.path.join(os.getcwd(), "assets")
if not os.path.exists(assets_dir):
    os.makedirs(assets_dir)
    print(f"Pasta 'assets' criada em {assets_dir}.")
    
# Cria o arquivo style.css se ele não existir
css_file_path = os.path.join(assets_dir, "style.css")
if not os.path.exists(css_file_path):
    with open(css_file_path, "w") as f:
        f.write("""
/* assets/style.css */
.kpi-card {
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 15px;
    text-align: center;
    background-color: #f9f9f9;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    flex: 1; /* Faz todos os cards terem o mesmo tamanho */
}
.kpi-title {
    font-size: 1.1em;
    font-weight: bold;
    color: #555;
}
.kpi-value {
    font-size: 2.2em;
    font-weight: bolder;
    color: #111;
    margin-top: 5px;
}
""")
    print("Arquivo 'style.css' criado na pasta 'assets'.")


# --- 1. CARREGAR OPÇÕES DOS FILTROS (Super leve) ---
def carregar_opcoes_filtros():
    print("Carregando opções de filtros do Parquet...")
    try:
        anos_df = pd.read_parquet(
            ARQUIVO_PARQUET, columns=["ano_registro"], engine="pyarrow"
        )
        anos_unicos = sorted(anos_df["ano_registro"].dropna().unique().astype(int))

        ufs_df = pd.read_parquet(
            ARQUIVO_PARQUET,
            columns=["uf_do_municipio_manifestante"],
            engine="pyarrow"
        )
        ufs_unicos = sorted(ufs_df["uf_do_municipio_manifestante"].dropna().unique())

        print("Opções de filtros carregadas.")
        return anos_unicos, ufs_unicos
    except Exception as e:
        print(f"ERRO AO CARREGAR FILTROS DO PARQUET: {e}")
        return [2025], ["BR"]

anos_unicos, ufs_unicas = carregar_opcoes_filtros()

# --- 2. CARREGAR AMOSTRA PARA A TABELA (Super leve) ---
try:
    df_amostra = pd.read_parquet(
        ARQUIVO_PARQUET, columns=None, engine="pyarrow"
    )
    df_amostra = df_amostra.head(100)
    df_amostra = df_amostra.astype(object).where(pd.notna(df_amostra), None)
    dados_tabela = df_amostra.to_dict("records")
    colunas_tabela = [
        {"name": i.replace("_", " ").title(), "id": i} for i in df_amostra.columns
    ]
    del df_amostra
except Exception as e:
    print(f"ERRO AO CARREGAR AMOSTRA: {e}")
    dados_tabela = []
    colunas_tabela = []


# --- 3. DEFINIÇÃO DOS LAYOUTS DAS "PÁGINAS" ---

def layout_kpis():
    """Retorna o layout da linha de KPIs."""
    return html.Div(
        style={"display": "flex", "flexDirection": "row", "gap": "20px", "marginBottom": "20px"},
        children=[
            # Card 1: Total de Manifestações
            html.Div(
                className="kpi-card",
                children=[
                    html.Div("Total de Manifestações", className="kpi-title"),
                    html.Div(id="kpi-total", className="kpi-value"),
                ]
            ),
            # Card 2: % Em Atraso
            html.Div(
                className="kpi-card",
                children=[
                    html.Div("% de Respostas em Atraso", className="kpi-title"),
                    html.Div(id="kpi-atraso", className="kpi-value"),
                ]
            ),
            # Card 3: Satisfação Média
            html.Div(
                className="kpi-card",
                children=[
                    html.Div("Satisfação Média (1-5)", className="kpi-title"),
                    html.Div(id="kpi-satisfacao", className="kpi-value"),
                ]
            ),
        ]
    )

def layout_dashboard():
    """Retorna o layout da 'página' principal do Dashboard."""
    return html.Div([
        # Linha 1: KPIs
        # layout_kpis(), # <-- REMOVIDO DESTA FUNÇÃO
        
        # Linha 2: Gráficos Principais (2/3 + 1/3)
        html.Div(
            style={"display": "flex", "flexDirection": "row", "gap": "20px", "marginBottom": "20px"},
            children=[
                # Coluna da Esquerda (Grande)
                html.Div(
                    # --- MUDANÇA AQUI ---
                    style={
                        "flex": 2, "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px",
                        "height": "450px", "display": "flex", "flexDirection": "column"
                    },
                    children=[
                        html.H4("Evolução Mensal das Manifestações", style={"textAlign": "center"}),
                        # CORREÇÃO: ID alterado para bater com o callback
                        # --- MUDANÇA AQUI ---
                        dcc.Graph(id="grafico-volume-mes", style={"flex": 1, "minHeight": 0}), 
                    ]
                ),
                # Coluna da Direita (Pequena)
                html.Div(
                    # --- MUDANÇA AQUI ---
                    style={
                        "flex": 1, "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px",
                        "height": "450px", "display": "flex", "flexDirection": "column"
                    },
                    children=[
                        html.H4("Distribuição por Tipo (Clique para filtrar)", style={"textAlign": "center"}),
                        # --- MUDANÇA AQUI ---
                        dcc.Graph(id="grafico-tipo", style={"flex": 1, "minHeight": 0}),
                    ]
                ),
            ]
        ),
        
        # Linha 3: Gráficos de Detalhe (2/3 + 1/3)
        html.Div(
            style={"display": "flex", "flexDirection": "row", "gap": "20px"},
            children=[
                # Coluna da Esquerda (Grande)
                html.Div(
                    # --- MUDANÇA AQUI ---
                    style={
                        "flex": 2, "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px",
                        "height": "450px", "display": "flex", "flexDirection": "column"
                    },
                    children=[
                        html.H4("Top 20 Órgãos Mais Demandados", style={"textAlign": "center"}),
                        # --- MUDANÇA AQUI ---
                        dcc.Graph(id="grafico-orgaos", style={"flex": 1, "minHeight": 0}),
                    ]
                ),
                # Coluna da Direita (Pequena)
                html.Div(
                    # --- MUDANÇA AQUI ---
                    style={
                        "flex": 1, "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px",
                        "height": "450px", "display": "flex", "flexDirection": "column"
                    },
                    children=[
                        html.H4("Satisfação do Usuário vs. Atraso", style={"textAlign": "center"}),
                        # --- MUDANÇA AQUI ---
                        dcc.Graph(id="grafico-satisfacao-hist", style={"flex": 1, "minHeight": 0}),
                    ]
                ),
            ]
        )
    ])

def layout_eda():
    """Retorna o layout da 'página' de Análise Exploratória (EDA)."""
    return html.Div([
        html.H2("Análises Exploratórias (Dados Filtados)"),
        html.P("Estes gráficos também são atualizados pelos filtros."),
        # --- MUDANÇA AQUI: Adiciona contêiner com altura fixa ---
        html.Div(
            style={"height": "450px", "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px", "marginBottom": "20px"},
            children=[dcc.Graph(id="eda-volume-tempo", style={"height": "100%"})]
        ),
        html.H3("Análise Demográfica", style={"marginTop": "20px"}),
        html.Div(
            style={"display": "flex", "flexDirection": "row", "gap": "20px"},
            children=[
                # --- MUDANÇA AQUI: Adiciona contêiner com altura fixa ---
                html.Div(
                    style={"flex": 1, "height": "450px", "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px"},
                    children=[dcc.Graph(id="eda-genero", style={"height": "100%"})]
                ),
                # --- MUDANÇA AQUI: Adiciona contêiner com altura fixa ---
                html.Div(
                    style={"flex": 1, "height": "450px", "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px"},
                    children=[dcc.Graph(id="eda-raca", style={"height": "100%"})]
                ),
            ]
        ),
        # --- MUDANÇA AQUI: Adiciona contêiner com altura fixa ---
        html.Div(
            style={"height": "450px", "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px", "marginTop": "20px"},
            children=[dcc.Graph(id="eda-faixa-etaria", style={"height": "100%"})]
        ),
        html.H3("Análise das Manifestações", style={"marginTop": "20px"}),
        html.Div(
            style={"display": "flex", "flexDirection": "row", "gap": "20px"},
            children=[
                # --- MUDANÇA AQUI: Adiciona contêiner com altura fixa ---
                html.Div(
                    style={"flex": 1, "height": "450px", "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px"},
                    children=[dcc.Graph(id="eda-tipos", style={"height": "100%"})]
                ),
                # --- MUDANÇA AQUI: Adiciona contêiner com altura fixa ---
                html.Div(
                    style={"flex": 1, "height": "450px", "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px"},
                    children=[dcc.Graph(id="eda-satisfacao-box", style={"height": "100%"})]
                ),
            ]
        ),
        # --- MUDANÇA AQUI: Adiciona contêiner com altura fixa ---
        html.Div(
            style={"height": "450px", "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px", "marginTop": "20px"},
            children=[dcc.Graph(id="eda-mapa-bar", style={"height": "100%"})]
        ),
    ])

def layout_metodologia():
    """Retorna o layout da 'página' de Metodologia."""
    return html.Div(
        style={"padding": "20px"},
        children=[
            html.H2("Processo de ETL (Extract, Transform, Load)"),
            dcc.Markdown(
                """
                - **Extração (Extract):** Múltiplos arquivos CSV foram lidos.
                - **Transformação (Transform):** Um script Python (`etl.py`) usando Pandas limpou e normalizou os dados.
                - **Carga (Load):** O resultado limpo foi salvo em um único arquivo: **`ouvidoria.parquet`** (usando o motor `pyarrow`).
                - **Visualização:** Este dashboard **lê dados diretamente do arquivo Parquet** (usando `pyarrow`), aplicando filtros antes de carregar os dados na memória.
                """
            ),
        ]
    )

def layout_amostra_dados():
    """Retorna o layout da 'página' de Amostra de Dados."""
    return html.Div(
        style={"padding": "20px"},
        children=[
            html.H2("Amostra de 100 Linhas do Arquivo Parquet"),
            dash_table.DataTable(
                id="tabela-dados",
                columns=colunas_tabela,
                data=dados_tabela,
                page_size=10,
                sort_action="native",
                filter_action="native",
                style_table={"overflowX": "auto"},
            ),
        ]
    )

# --- 4. INICIALIZAÇÃO E LAYOUT PRINCIPAL (O "CASCO") ---
# CORREÇÃO: Adicionado suppress_callback_exceptions=True
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div(
    style={"padding": "20px", "fontFamily": "Arial, sans-serif"}, # Adiciona uma fonte base
    children=[
        # Componentes "invisíveis" de memória
        dcc.Store(id='memoria-filtro-tipo'),
        dcc.Location(id="url", refresh=False), # Lê a URL do navegador

        # Título
        html.H1(children="Análise Exploratória - Ouvidoria CGU"),
        html.P(
            children=f"Análise dos dados de {anos_unicos[0]} a {anos_unicos[-1]} (Via Parquet)"
        ),
        
        # Filtros Globais
        html.Button(
            "Mostrar/Esconder Filtros",
            id="botao-toggle-filtros",
            style={"marginBottom": "10px", "width": "100%"},
        ),
        html.Div(
            id="container-filtros",
            className="filtros",
            children=[
                html.Label("Selecione o(s) Ano(s):"),
                dcc.Dropdown(
                    id="filtro-ano",
                    options=[{"label": ano, "value": ano} for ano in anos_unicos],
                    value=[anos_unicos[-1]],
                    multi=True,
                ),
                html.Label("Selecione a(s) UF(s):"),
                dcc.Dropdown(
                    id="filtro-uf",
                    options=[
                        {"label": uf.upper(), "value": uf} for uf in ufs_unicas
                    ],
                    value=ufs_unicas,
                    multi=True,
                ),
                html.Button(
                    "Limpar seleção de Tipo (clique no gráfico)", 
                    id="botao-limpar-tipo",
                    style={"marginTop": "10px", "width": "100%"}
                )
            ],
            style={"display": "none"}, # Inicia fechado
        ),

        # --- KPI LAYOUT MOVIDO PARA CÁ ---
        # Agora os KPIs são globais e sempre visíveis
        layout_kpis(),

        # Barra de Navegação (Estilo "Breadcrumb" com >)
        html.Nav(
            style={
                "display": "flex",
                "alignItems": "center", # Alinha links e separadores
                "borderBottom": "1px solid #ddd", 
                "padding": "10px 0",
                "marginBottom": "20px",
                "marginTop": "20px",
                "fontSize": "1.1em" # Fonte um pouco maior
            },
            children=[
                dcc.Link(
                    "Dashboard (Gráficos)", 
                    href="/", 
                    style={"textDecoration": "none", "padding": "0 10px", "color": "#007BFF"}
                ),
                html.Span(">", style={"color": "#888"}),
                dcc.Link(
                    "Análise Exploratória (EDA)", 
                    href="/eda", 
                    style={"textDecoration": "none", "padding": "0 10px", "color": "#007BFF"}
                ),
                html.Span(">", style={"color": "#888"}),
                dcc.Link(
                    "Metodologia (ETL)", 
                    href="/metodologia", 
                    style={"textDecoration": "none", "padding": "0 10px", "color": "#007BFF"}
                ),
                html.Span(">", style={"color": "#888"}),
                dcc.Link(
                    "Amostra dos Dados (Parquet)", 
                    href="/dados", 
                    style={"textDecoration": "none", "padding": "0 10px", "color": "#007BFF"}
                ),
            ]
        ),

        # Container da Página (Onde o conteúdo será renderizado)
        html.Div(id="page-content")
    ]
)

# --- 5. FUNÇÃO HELPER DE FILTRAGEM ---
def ler_dados_filtrados(anos, ufs, tipo_clicado):
    """Lê o Parquet com os filtros aplicados."""
    if not anos or not ufs:
        print("Filtros vazios.")
        return pd.DataFrame()

    filtros_parquet = [
        ("ano_registro", "in", anos),
        ("uf_do_municipio_manifestante", "in", ufs),
    ]
    if tipo_clicado:
        print(f"Filtrando também por TIPO: {tipo_clicado}")
        filtros_parquet.append(("tipo_manifestacao", "==", tipo_clicado))

    colunas_necessarias = [
        "ano_registro", "data_registro",
        "tipo_manifestacao", "nome_orgao",
        "satisfacao", "dias_de_atraso",
        "genero", "faixa_etaria", "raca_cor",
        "uf_do_municipio_manifestante",
    ]
    colunas_necessarias = list(set(colunas_necessarias)) 

    try:
        df_filtrado = pd.read_parquet(
            ARQUIVO_PARQUET,
            columns=colunas_necessarias,
            filters=filtros_parquet,
            engine="pyarrow",
        )
        print(f"Leitura do Parquet retornou {len(df_filtrado)} linhas.")
        return df_filtrado
    except Exception as e:
        print(f"ERRO ao ler Parquet com filtros: {e}")
        return pd.DataFrame()


# --- 6. CALLBACKS ---

# Callback 6.1: Roteador (Renderiza a página correta)
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname") # Monitora a URL
)
def display_page(pathname):
    if pathname == "/eda":
        return layout_eda()
    elif pathname == "/metodologia":
        return layout_metodologia()
    elif pathname == "/dados":
        return layout_amostra_dados()
    else:
        # Página inicial (href="/")
        return layout_dashboard()

# Callback 6.2: Mostrar/Esconder Filtros
@app.callback(
    Output("container-filtros", "style"),
    Input("botao-toggle-filtros", "n_clicks"),
    State("container-filtros", "style"),
)
def toggle_filtros_visibility(n_clicks, current_style):
    if n_clicks is None:
        return current_style
    if current_style.get("display") == "none":
        current_style["display"] = "block"
    else:
        current_style["display"] = "none"
    return current_style

# Callback 6.3: Gerenciador do Filtro de Clique (Cross-filter)
@app.callback(
    Output("memoria-filtro-tipo", "data"),
    Input("grafico-tipo", "clickData"),
    Input("botao-limpar-tipo", "n_clicks"),
)
def gerenciar_filtro_clique(clique_grafico, clique_limpar):
    trigger = ctx.triggered_id
    if trigger == "botao-limpar-tipo":
        return None # Limpa a memória
    if trigger == "grafico-tipo" and clique_grafico:
        valor_clicado = clique_grafico['points'][0]['x']
        return valor_clicado # Salva o valor na memória
    return no_update


# Callback 6.4: Atualiza os KPIs (CORRIGIDO)
@app.callback(
    [
        Output("kpi-total", "children"),
        Output("kpi-atraso", "children"),
        Output("kpi-satisfacao", "children"),
    ],
    [
        Input("filtro-ano", "value"), 
        Input("filtro-uf", "value"),
        Input("memoria-filtro-tipo", "data")
    ]
)
def atualizar_kpis(anos_selecionados, ufs_selecionadas, tipo_clicado):
    # CORREÇÃO: Removida a linha "if ctx.triggered_id..."
    
    print("Atualizando KPIs...")
    df_filtrado = ler_dados_filtrados(
        anos_selecionados, ufs_selecionadas, tipo_clicado
    )

    if df_filtrado.empty:
        return "0", "0.0%", "N/A"

    # --- 1. KPI Total ---
    total_manifestacoes = len(df_filtrado)
    
    # --- 2. KPI Atraso ---
    df_filtrado["em_atraso"] = pd.to_numeric(df_filtrado["dias_de_atraso"], errors='coerce').fillna(0) > 0
    pct_atraso = df_filtrado["em_atraso"].mean() * 100
    
    # --- 3. KPI Satisfação (CORRIGIDO) ---
    df_satisfacao = df_filtrado.copy()
    # Converte a coluna 'satisfacao' (que é texto) para número
    df_satisfacao["satisfacao_num"] = pd.to_numeric(df_satisfacao["satisfacao"], errors='coerce')
    # Remove NAs (criados por "não informado" ou outros textos)
    df_satisfacao = df_satisfacao.dropna(subset=["satisfacao_num"])

    if not df_satisfacao.empty:
        # Calcula a média da coluna numérica
        media_satisfacao = df_satisfacao["satisfacao_num"].mean()
        str_satisfacao = f"{media_satisfacao:.2f}"
    else:
        str_satisfacao = "N/A"

    # Retorna os valores formatados
    return f"{total_manifestacoes:,}", f"{pct_atraso:.1f}%", str_satisfacao


# Callback 6.5: Atualiza SÓ os gráficos do DASHBOARD (CORRIGIDO)
@app.callback(
    [
        Output("grafico-volume-mes", "figure"), # ID Corrigido
        Output("grafico-tipo", "figure"),
        Output("grafico-orgaos", "figure"),
        Output("grafico-satisfacao-hist", "figure"),
    ],
    [
        Input("filtro-ano", "value"), 
        Input("filtro-uf", "value"),
        Input("memoria-filtro-tipo", "data")
    ]
)
def atualizar_dashboard(anos_selecionados, ufs_selecionadas, tipo_clicado):
    # CORREÇÃO: Removida a linha "if ctx.triggered_id..."
    
    print("Atualizando gráficos do DASHBOARD...")
    df_filtrado = ler_dados_filtrados(
        anos_selecionados, ufs_selecionadas, tipo_clicado
    )
    empty_fig = {"layout": {"template": TEMA_GRAFICOS, "title": {"text": "Sem dados para exibir"}}}

    if df_filtrado.empty:
        return empty_fig, empty_fig, empty_fig, empty_fig

    # --- Gerar Gráficos do Dashboard ---
    fig_volume_mes = grafico_volume_tempo(df_filtrado.copy())
    fig_volume_mes.update_layout(title=None) # Remove o título, pois já temos no H4

    tipo_counts_dash = (
        df_filtrado["tipo_manifestacao"].value_counts().reset_index(name="Contagem")
    )
    fig_tipo_dash = px.bar(
        tipo_counts_dash, x="tipo_manifestacao", y="Contagem",
        template=TEMA_GRAFICOS
    )
    fig_tipo_dash.update_layout(title=None, title_x=0.5) # Remove título

    orgao_counts = (
        df_filtrado["nome_orgao"].value_counts().head(20).reset_index(name="Contagem")
    )
    fig_orgaos = px.bar(
        orgao_counts, y="nome_orgao", x="Contagem",
        orientation="h", template=TEMA_GRAFICOS
    )
    fig_orgaos.update_layout(yaxis={"categoryorder": "total ascending"}, title=None, title_x=0.5) # Remove título

    df_filtrado["em_atraso"] = pd.to_numeric(df_filtrado["dias_de_atraso"], errors='coerce').fillna(0) > 0
    fig_satisfacao_hist = px.histogram(
        df_filtrado.dropna(subset=["satisfacao"]),
        x="satisfacao", color="em_atraso", barmode="group",
        template=TEMA_GRAFICOS
    )
    fig_satisfacao_hist.update_layout(title=None, title_x=0.5) # Remove título

    return fig_volume_mes, fig_tipo_dash, fig_orgaos, fig_satisfacao_hist


# Callback 6.6: Atualiza SÓ os gráficos do EDA (CORRIGIDO)
@app.callback(
    [
        Output("eda-volume-tempo", "figure"),
        Output("eda-genero", "figure"),
        Output("eda-faixa-etaria", "figure"),
        Output("eda-raca", "figure"),
        Output("eda-tipos", "figure"),
        Output("eda-satisfacao-box", "figure"),
        Output("eda-mapa-bar", "figure"),
    ],
    [
        Input("filtro-ano", "value"), 
        Input("filtro-uf", "value"),
        Input("memoria-filtro-tipo", "data")
    ]
)
def atualizar_eda(anos_selecionados, ufs_selecionadas, tipo_clicado):
    # CORREÇÃO: Removida a linha "if ctx.triggered_id..."
    
    print("Atualizando gráficos do EDA...")
    df_filtrado = ler_dados_filtrados(
        anos_selecionados, ufs_selecionadas, tipo_clicado
    )
    empty_fig = {"layout": {"template": TEMA_GRAFICOS, "title": {"text": "Sem dados para exibir"}}}

    if df_filtrado.empty:
        return [empty_fig] * 7

    # --- Gerar Gráficos do EDA (usando as funções importadas) ---
    fig_eda_volume = grafico_volume_tempo(df_filtrado.copy())
    fig_eda_genero = grafico_genero(df_filtrado)
    fig_eda_faixa = grafico_faixa_etaria(df_filtrado)
    fig_eda_raca = grafico_raca(df_filtrado) 
    fig_eda_tipos = grafico_tipos(df_filtrado)
    fig_eda_satisfacao_box = grafico_satisfacao(df_filtrado.copy())
    fig_eda_mapa = grafico_mapa(df_filtrado)

    return (
        fig_eda_volume, fig_eda_genero, fig_eda_faixa,
        fig_eda_raca, fig_eda_tipos, fig_eda_satisfacao_box,
        fig_eda_mapa,
    )

# --- 7. EXECUÇÃO DO APP ---
if __name__ == "__main__":
    app.run(debug=True)


