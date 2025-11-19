# app.py (VERSÃO COMPLETA E CORRIGIDA + ML)
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash import no_update, ctx
import os 
import joblib # --- NOVO: Para carregar o modelo de ML ---

# Importamos as funções de gráfico
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
TEMA_GRAFICOS = "plotly_white" 
ARQUIVO_MODELO = "modelo_satisfacao.joblib" # --- NOVO: Caminho do modelo ---

# --- 0. CRIAR PASTA ASSETS SE NÃO EXISTIR ---
assets_dir = os.path.join(os.getcwd(), "assets")
if not os.path.exists(assets_dir):
    os.makedirs(assets_dir)
    print(f"Pasta 'assets' criada em {assets_dir}.")
    
css_file_path = os.path.join(assets_dir, "style.css")
if not os.path.exists(css_file_path):
    with open(css_file_path, "w") as f:
        f.write("""
/* assets/style.css */
.kpi-card { border: 1px solid #ddd; border-radius: 5px; padding: 15px; text-align: center; background-color: #f9f9f9; box-shadow: 0 2px 4px rgba(0,0,0,0.05); flex: 1; }
.kpi-title { font-size: 1.1em; font-weight: bold; color: #555; }
.kpi-value { font-size: 2.2em; font-weight: bolder; color: #111; margin-top: 5px; }
.predicao-card { border: 1px solid #eee; border-radius: 5px; padding: 20px; background-color: #fafafa; margin-top: 20px; }
.predicao-resultado-baixa { font-size: 1.8em; font-weight: bold; color: #d9534f; }
.predicao-resultado-alta { font-size: 1.8em; font-weight: bold; color: #5cb85c; }
""")
    print("Arquivo 'style.css' criado na pasta 'assets'.")


# --- 1. CARREGAR OPÇÕES DOS FILTROS (EXPANDIDO) ---
def carregar_opcoes_filtros():
    print("Carregando opções de filtros e ML do Parquet...")
    try:
        # Colunas necessárias para os filtros e para o ML
        colunas_necessarias = [
            "ano_registro", "uf_do_municipio_manifestante",
            "tipo_manifestacao", "nome_orgao", "genero",
            "faixa_etaria", "raca_cor"
        ]
        
        # Lê todas as colunas necessárias de uma vez
        df_opcoes = pd.read_parquet(
            ARQUIVO_PARQUET, columns=colunas_necessarias, engine="pyarrow"
        )
        print("Dados de opções carregados.")

        # Opções para Filtros do Dashboard
        anos_unicos = sorted(df_opcoes["ano_registro"].dropna().unique().astype(int))
        ufs_unicas = sorted(df_opcoes["uf_do_municipio_manifestante"].dropna().unique())

        # Opções para Dropdowns do ML
        tipos_unicos = sorted(df_opcoes["tipo_manifestacao"].dropna().unique())
        # Limita a 1000 órgãos para não sobrecarregar o dropdown
        orgaos_unicos = sorted(df_opcoes["nome_orgao"].value_counts().head(1000).index)
        generos_unicos = sorted(df_opcoes["genero"].dropna().unique())
        faixas_unicas = sorted(df_opcoes["faixa_etaria"].dropna().unique())
        racas_unicas = sorted(df_opcoes["raca_cor"].dropna().unique())
        
        print("Opções de filtros e ML carregadas.")
        
        opcoes = {
            "anos": [{"label": ano, "value": ano} for ano in anos_unicos],
            "ufs": [{"label": uf.upper(), "value": uf} for uf in ufs_unicas],
            "anos_lista": anos_unicos, # Para o valor default
            "ufs_lista": ufs_unicas, # Para o valor default
            
            # Opções para ML
            "tipos_ml": [{"label": i, "value": i} for i in tipos_unicos],
            "orgaos_ml": [{"label": i, "value": i} for i in orgaos_unicos],
            "generos_ml": [{"label": i, "value": i} for i in generos_unicos],
            "faixas_ml": [{"label": i, "value": i} for i in faixas_unicas],
            "racas_ml": [{"label": i, "value": i} for i in racas_unicas],
            "ufs_ml": [{"label": uf.upper(), "value": uf} for uf in ufs_unicas],
        }
        return opcoes
        
    except Exception as e:
        print(f"ERRO AO CARREGAR FILTROS DO PARQUET: {e}")
        # Retorno de emergência
        opcoes_emergencia = {
            "anos": [{"label": 2025, "value": 2025}], "ufs": [{"label": "BR", "value": "BR"}],
            "anos_lista": [2025], "ufs_lista": ["BR"],
            "tipos_ml": [], "orgaos_ml": [], "generos_ml": [], 
            "faixas_ml": [], "racas_ml": [], "ufs_ml": [],
        }
        return opcoes_emergencia

opcoes = carregar_opcoes_filtros()


# --- 2. CARREGAR AMOSTRA PARA A TABELA (Sem mudança) ---
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


# --- 3. CARREGAR O MODELO DE ML (NOVO) ---
try:
    modelo_carregado = joblib.load(ARQUIVO_MODELO)
    print(f"Modelo '{ARQUIVO_MODELO}' carregado com sucesso.")
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível carregar o modelo '{ARQUIVO_MODELO}'.")
    print(f"Erro: {e}")
    modelo_carregado = None


# --- 4. DEFINIÇÃO DOS LAYOUTS DAS "PÁGINAS" ---

def layout_kpis():
    # (Sem mudanças)
    return html.Div(
        style={"display": "flex", "flexDirection": "row", "gap": "20px", "marginBottom": "20px"},
        children=[
            html.Div(className="kpi-card", children=[
                html.Div("Total de Manifestações", className="kpi-title"),
                html.Div(id="kpi-total", className="kpi-value"),
            ]),
            html.Div(className="kpi-card", children=[
                html.Div("% de Respostas em Atraso", className="kpi-title"),
                html.Div(id="kpi-atraso", className="kpi-value"),
            ]),
            html.Div(className="kpi-card", children=[
                html.Div("Satisfação Média (1-5)", className="kpi-title"),
                html.Div(id="kpi-satisfacao", className="kpi-value"),
            ]),
        ]
    )

def layout_dashboard():
    # (Sem mudanças)
    return html.Div([
        html.Div(
            style={"display": "flex", "flexDirection": "row", "gap": "20px", "marginBottom": "20px"},
            children=[
                html.Div(
                    style={"flex": 2, "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px", "height": "450px", "display": "flex", "flexDirection": "column"},
                    children=[
                        html.H4("Evolução Mensal das Manifestações", style={"textAlign": "center"}),
                        dcc.Graph(id="grafico-volume-mes", style={"flex": 1, "minHeight": 0}), 
                    ]
                ),
                html.Div(
                    style={"flex": 1, "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px", "height": "450px", "display": "flex", "flexDirection": "column"},
                    children=[
                        html.H4("Distribuição por Tipo (Clique para filtrar)", style={"textAlign": "center"}),
                        dcc.Graph(id="grafico-tipo", style={"flex": 1, "minHeight": 0}),
                    ]
                ),
            ]
        ),
        html.Div(
            style={"display": "flex", "flexDirection": "row", "gap": "20px"},
            children=[
                html.Div(
                    style={"flex": 2, "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px", "height": "450px", "display": "flex", "flexDirection": "column"},
                    children=[
                        html.H4("Top 20 Órgãos Mais Demandados", style={"textAlign": "center"}),
                        dcc.Graph(id="grafico-orgaos", style={"flex": 1, "minHeight": 0}),
                    ]
                ),
                html.Div(
                    style={"flex": 1, "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px", "height": "450px", "display": "flex", "flexDirection": "column"},
                    children=[
                        html.H4("Satisfação do Usuário vs. Atraso", style={"textAlign": "center"}),
                        dcc.Graph(id="grafico-satisfacao-hist", style={"flex": 1, "minHeight": 0}),
                    ]
                ),
            ]
        )
    ])

def layout_eda():
    # (Sem mudanças)
    return html.Div([
        html.H2("Análises Exploratórias (Dados Filtados)"),
        html.P("Estes gráficos também são atualizados pelos filtros."),
        html.Div(
            style={"height": "450px", "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px", "marginBottom": "20px"},
            children=[dcc.Graph(id="eda-volume-tempo", style={"height": "100%"})]
        ),
        html.H3("Análise Demográfica", style={"marginTop": "20px"}),
        html.Div(style={"display": "flex", "flexDirection": "row", "gap": "20px"}, children=[
            html.Div(style={"flex": 1, "height": "450px", "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px"},
                children=[dcc.Graph(id="eda-genero", style={"height": "100%"})]
            ),
            html.Div(style={"flex": 1, "height": "450px", "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px"},
                children=[dcc.Graph(id="eda-raca", style={"height": "100%"})]
            ),
        ]),
        html.Div(
            style={"height": "450px", "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px", "marginTop": "20px"},
            children=[dcc.Graph(id="eda-faixa-etaria", style={"height": "100%"})]
        ),
        html.H3("Análise das Manifestações", style={"marginTop": "20px"}),
        html.Div(style={"display": "flex", "flexDirection": "row", "gap": "20px"}, children=[
            html.Div(style={"flex": 1, "height": "450px", "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px"},
                children=[dcc.Graph(id="eda-tipos", style={"height": "100%"})]
            ),
            html.Div(style={"flex": 1, "height": "450px", "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px"},
                children=[dcc.Graph(id="eda-satisfacao-box", style={"height": "100%"})]
            ),
        ]),
        html.Div(
            style={"height": "450px", "border": "1px solid #eee", "padding": "10px", "borderRadius": "5px", "marginTop": "20px"},
            children=[dcc.Graph(id="eda-mapa-bar", style={"height": "100%"})]
        ),
    ])

def layout_metodologia():
    # (Levemente atualizado)
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
            html.H2("Modelo de Machine Learning (Classificação)"),
            dcc.Markdown(
                f"""
                - **Objetivo:** Prever a probabilidade de um usuário ficar **Insatisfeito** (nota 1 ou 2).
                - **Arquivo do Modelo:** `{ARQUIVO_MODELO}` (gerado pelo `ml_classificacao_v3.py`).
                - **Dados de Treino:** O modelo foi treinado com **{429208:,}** manifestações que possuíam nota de satisfação válida.
                - **Acurácia:** O modelo atingiu uma acurácia de **{0.6615:.1f}%** nos dados de teste.
                - **Features (Entradas):** O modelo usa as seguintes informações para prever: `Assunto` (texto), `Tipo Manifestação`, `Nome do Órgão`, `Gênero`, `Faixa Etária`, `Raça/Cor` e `UF`.
                """
            ),
        ]
    )

def layout_amostra_dados():
    # (Sem mudanças)
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

# --- NOVO: Layout para a página de Predição ---
def layout_predicao():
    if modelo_carregado is None:
        return html.Div([
            html.H2("Erro na Análise Preditiva"),
            html.P(f"O modelo '{ARQUIVO_MODELO}' não pôde ser carregado."),
            html.P("Por favor, verifique os logs do servidor e se o arquivo existe.")
        ], style={"padding": "20px", "color": "red"})

    # Layout do formulário interativo
    return html.Div(
        style={"padding": "20px"},
        children=[
            html.H2("Simulador de Satisfação (Análise Preditiva)"),
            html.P("Preencha os campos abaixo para prever a probabilidade de insatisfação."),
            
            html.Div(className="predicao-card", children=[
                html.Label("Assunto (Descreva o problema):", style={"fontWeight": "bold"}),
                dcc.Textarea(
                    id="ml-input-assunto",
                    placeholder="Ex: Demora no atendimento do INSS para aposentadoria...",
                    style={"width": "100%", "height": 100, "marginBottom": "15px"}
                ),
                
                html.Div(style={"display": "flex", "gap": "20px", "marginBottom": "15px"}, children=[
                    html.Div(style={"flex": 1}, children=[
                        html.Label("Nome do Órgão:", style={"fontWeight": "bold"}),
                        dcc.Dropdown(id="ml-input-orgao", options=opcoes["orgaos_ml"], placeholder="Selecione o órgão...")
                    ]),
                    html.Div(style={"flex": 1}, children=[
                        html.Label("Tipo da Manifestação:", style={"fontWeight": "bold"}),
                        dcc.Dropdown(id="ml-input-tipo", options=opcoes["tipos_ml"], placeholder="Selecione o tipo...")
                    ]),
                ]),

                html.Div(style={"display": "flex", "gap": "20px", "marginBottom": "15px"}, children=[
                    html.Div(style={"flex": 1}, children=[
                        html.Label("Gênero:", style={"fontWeight": "bold"}),
                        dcc.Dropdown(id="ml-input-genero", options=opcoes["generos_ml"], placeholder="Selecione...")
                    ]),
                    html.Div(style={"flex": 1}, children=[
                        html.Label("Faixa Etária:", style={"fontWeight": "bold"}),
                        dcc.Dropdown(id="ml-input-faixa", options=opcoes["faixas_ml"], placeholder="Selecione...")
                    ]),
                ]),

                html.Div(style={"display": "flex", "gap": "20px", "marginBottom": "15px"}, children=[
                    html.Div(style={"flex": 1}, children=[
                        html.Label("Raça/Cor:", style={"fontWeight": "bold"}),
                        dcc.Dropdown(id="ml-input-raca", options=opcoes["racas_ml"], placeholder="Selecione...")
                    ]),
                    html.Div(style={"flex": 1}, children=[
                        html.Label("UF do Manifestante:", style={"fontWeight": "bold"}),
                        dcc.Dropdown(id="ml-input-uf", options=opcoes["ufs_ml"], placeholder="Selecione...")
                    ]),
                ]),

                html.Button(
                    "Prever Risco de Insatisfação", 
                    id="botao-prever",
                    n_clicks=0,
                    style={"width": "100%", "padding": "10px", "fontSize": "1.2em", "backgroundColor": "#007BFF", "color": "white", "border": "none", "borderRadius": "5px"}
                ),

                # Div para exibir o resultado
                html.Div(id="resultado-predicao", style={"marginTop": "20px", "textAlign": "center"})
            ])
        ]
    )


# --- 5. INICIALIZAÇÃO E LAYOUT PRINCIPAL (O "CASCO") ---
# --- CORREÇÃO IMPORTANTE AQUI ---
#app = dash.Dash(__name__, suppress_callback_exceptions=True)
#server = app.server
app = dash.Dash(__name__, suppress_callback_exceptions=True)
print("--- DEBUG: O MODO DE SUPRESSÃO DE ERRO ESTÁ ATIVO! ---") # <-- ADICIONE ESTA LINHA
server = app.server

app.layout = html.Div(
    style={"padding": "20px", "fontFamily": "Arial, sans-serif"}, 
    children=[
        dcc.Store(id='memoria-filtro-tipo'),
        dcc.Location(id="url", refresh=False),

        html.H1(children="Análise Exploratória - Ouvidoria CGU"),
        html.P(
            children=f"Análise dos dados de {opcoes['anos_lista'][0]} a {opcoes['anos_lista'][-1]} (Via Parquet)"
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
                    options=opcoes["anos"],
                    value=[opcoes["anos_lista"][-1]], # Default = último ano
                    multi=True,
                ),
                html.Label("Selecione a(s) UF(s):"),
                dcc.Dropdown(
                    id="filtro-uf",
                    options=opcoes["ufs"],
                    value=opcoes["ufs_lista"], # Default = todas as UFs
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

        layout_kpis(),

        # --- BARRA DE NAVEGAÇÃO ATUALIZADA ---
        html.Nav(
            style={
                "display": "flex", "alignItems": "center", "borderBottom": "1px solid #ddd", 
                "padding": "10px 0", "marginBottom": "20px", "marginTop": "20px", "fontSize": "1.1em"
            },
            children=[
                dcc.Link("Dashboard (Gráficos)", href="/", style={"textDecoration": "none", "padding": "0 10px", "color": "#007BFF"}),
                html.Span(">", style={"color": "#888"}),
                dcc.Link("Análise Exploratória (EDA)", href="/eda", style={"textDecoration": "none", "padding": "0 10px", "color": "#007BFF"}),
                html.Span(">", style={"color": "#888"}),
                # --- NOVO LINK ---
                dcc.Link("Análise Preditiva (ML)", href="/predicao", style={"textDecoration": "none", "padding": "0 10px", "color": "#007BFF", "fontWeight": "bold"}),
                html.Span(">", style={"color": "#888"}),
                dcc.Link("Metodologia (ETL/ML)", href="/metodologia", style={"textDecoration": "none", "padding": "0 10px", "color": "#007BFF"}),
                html.Span(">", style={"color": "#888"}),
                dcc.Link("Amostra dos Dados (Parquet)", href="/dados", style={"textDecoration": "none", "padding": "0 10px", "color": "#007BFF"}),
            ]
        ),

        # Container da Página
        html.Div(id="page-content")
    ]
)

# --- 6. FUNÇÃO HELPER DE FILTRAGEM ---
def ler_dados_filtrados(anos, ufs, tipo_clicado):
    # (Sem mudanças)
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


# --- 7. CALLBACKS ---

# Callback 7.1: Roteador (Renderiza a página correta) - ATUALIZADO
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname") 
)
def display_page(pathname):
    if pathname == "/eda":
        return layout_eda()
    elif pathname == "/metodologia":
        return layout_metodologia()
    elif pathname == "/dados":
        return layout_amostra_dados()
    # --- NOVA ROTA ---
    elif pathname == "/predicao":
        return layout_predicao()
    else:
        # Página inicial (href="/")
        return layout_dashboard()

# Callback 7.2: Mostrar/Esconder Filtros
@app.callback(
    Output("container-filtros", "style"),
    Input("botao-toggle-filtros", "n_clicks"),
    State("container-filtros", "style"),
)
def toggle_filtros_visibility(n_clicks, current_style):
    # (Sem mudanças)
    if n_clicks is None:
        return current_style
    if current_style.get("display") == "none":
        current_style["display"] = "block"
    else:
        current_style["display"] = "none"
    return current_style

# Callback 7.3: Gerenciador do Filtro de Clique (Cross-filter)
@app.callback(
    Output("memoria-filtro-tipo", "data"),
    Input("grafico-tipo", "clickData"),
    Input("botao-limpar-tipo", "n_clicks"),
)
def gerenciar_filtro_clique(clique_grafico, clique_limpar):
    # (Sem mudanças)
    trigger = ctx.triggered_id
    if trigger == "botao-limpar-tipo":
        return None 
    if trigger == "grafico-tipo" and clique_grafico:
        valor_clicado = clique_grafico['points'][0]['x']
        return valor_clicado 
    return no_update


# Callback 7.4: Atualiza os KPIs 
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
    # (ESSA É A PARTE QUE FALTAVA)
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
    
    # --- 3. KPI Satisfação (CORRIGIDO com extração) ---
    df_satisfacao = df_filtrado.copy()
    # Extrai o número de "(1) muito insatisfeito"
    df_satisfacao["satisfacao_num"] = df_satisfacao["satisfacao"].astype(str).str.extract(r'\((\d)\)')
    df_satisfacao["satisfacao_num"] = pd.to_numeric(df_satisfacao["satisfacao_num"], errors='coerce')
    df_satisfacao = df_satisfacao.dropna(subset=["satisfacao_num"])

    if not df_satisfacao.empty:
        media_satisfacao = df_satisfacao["satisfacao_num"].mean()
        str_satisfacao = f"{media_satisfacao:.2f}"
    else:
        str_satisfacao = "N/A"

    return f"{total_manifestacoes:,}", f"{pct_atraso:.1f}%", str_satisfacao


# Callback 7.5: Atualiza SÓ os gráficos do DASHBOARD
@app.callback(
    [
        Output("grafico-volume-mes", "figure"), 
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
    # (Função que estava faltando)
    print("Atualizando gráficos do DASHBOARD...")
    df_filtrado = ler_dados_filtrados(
        anos_selecionados, ufs_selecionadas, tipo_clicado
    )
    empty_fig = {"layout": {"template": TEMA_GRAFICOS, "title": {"text": "Sem dados para exibir"}}}

    if df_filtrado.empty:
        return empty_fig, empty_fig, empty_fig, empty_fig

    fig_volume_mes = grafico_volume_tempo(df_filtrado.copy())
    fig_volume_mes.update_layout(title=None) 

    tipo_counts_dash = (df_filtrado["tipo_manifestacao"].value_counts().reset_index(name="Contagem"))
    fig_tipo_dash = px.bar(tipo_counts_dash, x="tipo_manifestacao", y="Contagem", template=TEMA_GRAFICOS)
    fig_tipo_dash.update_layout(title=None, title_x=0.5)

    orgao_counts = (df_filtrado["nome_orgao"].value_counts().head(20).reset_index(name="Contagem"))
    fig_orgaos = px.bar(orgao_counts, y="nome_orgao", x="Contagem", orientation="h", template=TEMA_GRAFICOS)
    fig_orgaos.update_layout(yaxis={"categoryorder": "total ascending"}, title=None, title_x=0.5) 

    df_filtrado["em_atraso"] = pd.to_numeric(df_filtrado["dias_de_atraso"], errors='coerce').fillna(0) > 0
    # CORREÇÃO: Usar a coluna 'satisfacao' original para o histograma
    fig_satisfacao_hist = px.histogram(
        df_filtrado.dropna(subset=["satisfacao"]),
        x="satisfacao", color="em_atraso", barmode="group",
        template=TEMA_GRAFICOS,
        # Ordena o eixo X pelo texto (ex: (1), (2)...)
        category_orders={"satisfacao": sorted(df_filtrado[df_filtrado['satisfacao'] != 'não informado']['satisfacao'].unique())}
    )
    fig_satisfacao_hist.update_layout(title=None, title_x=0.5) 

    return fig_volume_mes, fig_tipo_dash, fig_orgaos, fig_satisfacao_hist


# Callback 7.6: Atualiza SÓ os gráficos do EDA
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
    # (Função que estava faltando)
    print("Atualizando gráficos do EDA...")
    df_filtrado = ler_dados_filtrados(
        anos_selecionados, ufs_selecionadas, tipo_clicado
    )
    empty_fig = {"layout": {"template": TEMA_GRAFICOS, "title": {"text": "Sem dados para exibir"}}}

    if df_filtrado.empty:
        return [empty_fig] * 7

    #
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


# --- NOVO: Callback 7.7: Previsão do Modelo de ML ---
@app.callback(
    Output("resultado-predicao", "children"),
    Input("botao-prever", "n_clicks"),
    [
        State("ml-input-assunto", "value"),
        State("ml-input-orgao", "value"),
        State("ml-input-tipo", "value"),
        State("ml-input-genero", "value"),
        State("ml-input-faixa", "value"),
        State("ml-input-raca", "value"),
        State("ml-input-uf", "value"),
    ],
    prevent_initial_call=True # Não roda quando o app carrega
)
def callback_prever_satisfacao(
    n_clicks, assunto, orgao, tipo, genero, faixa, raca, uf
):
    # (Função que estava faltando - FAZ O BOTÃO FUNCIONAR)
    if modelo_carregado is None:
        return html.P("ERRO: O modelo de ML não está carregado.", style={"color": "red"})

    # Validação simples de entrada
    if not all([assunto, orgao, tipo, genero, faixa, raca, uf]):
        return html.P("Por favor, preencha todos os campos para prever.", style={"color": "orange"})
    
    # As colunas devem ser EXATAMENTE estas
    colunas_modelo = [
        'tipo_manifestacao', 'nome_orgao', 'genero', 
        'faixa_etaria', 'raca_cor', 'uf_do_municipio_manifestante',
        'assunto'
    ]
    
    # Criar um DataFrame de 1 linha com os dados de entrada
    dados_para_prever = {
        'tipo_manifestacao': [tipo],
        'nome_orgao': [orgao],
        'genero': [genero],
        'faixa_etaria': [faixa],
        'raca_cor': [raca],
        'uf_do_municipio_manifestante': [uf],
        'assunto': [assunto]
    }
    
    # Garantir que os inputs 'não informado' sejam consistentes
    for k, v in dados_para_prever.items():
        if v[0] is None:
            dados_para_prever[k] = ['não informado']
    if dados_para_prever['assunto'][0] == 'não informado':
        dados_para_prever['assunto'] = ['sem assunto'] # Como no treino

    
    df_novo = pd.DataFrame(dados_para_prever, columns=colunas_modelo)
    
    try:
        # Fazer a predição de PROBABILIDADE
        # O resultado será algo como [[prob_satisfeito, prob_insatisfeito]]
        probabilidades = modelo_carregado.predict_proba(df_novo)
        
        # Classe 1 = Insatisfeito
        prob_insatisfeito = probabilidades[0][1] 
        
        # Formatando o resultado
        pct_insatisfeito = prob_insatisfeito * 100
        
        if prob_insatisfeito > 0.6: # Risco Alto
            cor_texto = "predicao-resultado-baixa" # Vermelho
            risco = "Alto"
        elif prob_insatisfeito > 0.4: # Risco Médio
            cor_texto = "orange"
            risco = "Médio"
        else: # Risco Baixo
            cor_texto = "predicao-resultado-alta" # Verde
            risco = "Baixo"
            
        return html.Div([
            html.H3("Resultado da Predição:"),
            html.P(f"Risco de Insatisfação: {risco}", className=cor_texto, style={"color": cor_texto if cor_texto == 'orange' else None}),
            html.P(f"Probabilidade de Insatisfação (Nota 1 ou 2): {pct_insatisfeito:.1f}%")
        ])

    except Exception as e:
        print(f"ERRO na predição: {e}")
        return html.P(f"Erro ao processar a predição: {e}", style={"color": "red"})

# --- 8. EXECUÇÃO DO APP ---
if __name__ == "__main__":
    app.run(debug=True)