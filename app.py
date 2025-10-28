# app.py CORRIGIDO
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash import no_update, ctx

# Importamos TODAS as funções de gráfico que vamos usar
from eda_ouvidoria import (
    grafico_volume_tempo,
    grafico_genero,
    grafico_faixa_etaria,
    grafico_tipos,       # Usado pela aba EDA
    grafico_satisfacao,  # Usado pela aba EDA (boxplot)
    grafico_mapa,
    grafico_raca        # Precisamos importar este também
)

ARQUIVO_PARQUET = "ouvidoria.parquet"

# --- 1. CARREGAR OPÇÕES DOS FILTROS (Super leve) ---
def carregar_opcoes_filtros():
    print("Carregando opções de filtros do Parquet...")
    try:
        # --- MUDANÇA AQUI ---
        anos_df = pd.read_parquet(
            ARQUIVO_PARQUET, columns=["ano_registro"], engine="pyarrow"
        )
        anos_unicos = sorted(anos_df["ano_registro"].dropna().unique().astype(int))

        ufs_df = pd.read_parquet(
            ARQUIVO_PARQUET,
            columns=["uf_do_municipio_manifestante"],
            engine="pyarrow" # --- MUDANÇA AQUI ---
        )
        # --- FIM DA MUDANÇA ---
        ufs_unicos = sorted(ufs_df["uf_do_municipio_manifestante"].dropna().unique())

        print("Opções de filtros carregadas.")
        return anos_unicos, ufs_unicos
    except Exception as e:
        print(f"ERRO AO CARREGAR FILTROS DO PARQUET: {e}")
        return [2025], ["BR"]


anos_unicos, ufs_unicas = carregar_opcoes_filtros()

# --- 2. CARREGAR AMOSTRA PARA A TABELA (Super leve) ---
try:
    # --- MUDANÇA AQUI ---
    df_amostra = pd.read_parquet(
        ARQUIVO_PARQUET, columns=None, engine="pyarrow"
    )
    # --- FIM DA MUDANÇA ---
    
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


# --- 3. INICIALIZAÇÃO E LAYOUT DO APP ---
app = dash.Dash(__name__)
server = app.server

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# LINHA REMOVIDA: Não vamos mais carregar o DF inteiro aqui.
# A linha "df = pd.read_parquet(...)" que estava aqui (linha 8)
# foi removida. É ela que causava o erro do Traceback.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

app.layout = html.Div(
    children=[
        dcc.Store(id='memoria-filtro-tipo'),
        html.H1(children="Análise Exploratória - Ouvidoria CGU"),
        html.P(
            children=f"Análise dos dados de {anos_unicos[0]} a {anos_unicos[-1]} (Via Parquet)"
        ),
        dcc.Tabs(
            id="abas-principais",
            value="tab-dashboard",
            children=[
                # --- ABA 1: DASHBOARD (GRÁFICOS) ---
                dcc.Tab(
                    label="Dashboard (Gráficos)",
                    value="tab-dashboard",
                    children=[
                        html.Div(
                            className="container-graficos",
                            style={"padding": "20px"},
                            children=[
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
                                            options=[
                                                {"label": ano, "value": ano}
                                                for ano in anos_unicos
                                            ],
                                            value=[anos_unicos[-1]],
                                            multi=True,
                                        ),
                                        html.Label("Selecione a(s) UF(s):"),
                                        dcc.Dropdown(
                                            id="filtro-uf",
                                            options=[
                                                {"label": uf.upper(), "value": uf}
                                                for uf in ufs_unicas
                                            ],
                                            value=ufs_unicas,
                                            multi=True,
                                        ),
                                        # --- ADICIONE ISSO ---
                                        html.Button(
                                            "Limpar seleção de Tipo (clique no gráfico)", 
                                            id="botao-limpar-tipo",
                                            style={"marginTop": "10px", "width": "100%"}
                                        )
                                        # --- FIM DA ADIÇÃO ---
                                    ],
                                    style={"display": "none"}, # Inicia fechado
                                ),
                                # Placeholders dos Gráficos do Dashboard
                                html.H2("1. Volume de Manifestações ao Longo do Tempo"),
                                dcc.Graph(id="grafico-volume-ano"),
                                html.H2("2. Análise dos Tipos de Manifestação"),
                                dcc.Graph(id="grafico-tipo"),
                                html.H2("3. Top 20 Órgãos Mais Demandados"),
                                dcc.Graph(id="grafico-orgaos"),
                                html.H2("4. Satisfação do Usuário vs. Atraso"),
                                dcc.Graph(id="grafico-satisfacao-hist"), # Renomeado para não confundir
                            ],
                        )
                    ],
                ),  # Fim da Aba 1
                
                # --- ABA 2: METODOLOGIA (NOVA) ---
                dcc.Tab(
                    label="Metodologia (ETL)",
                    value="tab-metodologia",
                    children=[
                        html.Div(
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
                            ],
                        )
                    ],
                ),  # Fim da Aba 2

                # --- ABA NOVA: ANÁLISE EXPLORATÓRIA (EDA) ---
                dcc.Tab(
                    label="Análise Exploratória (EDA)",
                    value="tab-eda",
                    children=[
                        html.Div(
                            style={"padding": "20px"},
                            children=[
                                html.H2("Análises Exploratórias (Dados Filtados)"),
                                html.P("Estes gráficos também são atualizados pelos filtros da aba 'Dashboard'."),
                                dcc.Graph(id="eda-volume-tempo"),
                                dcc.Graph(id="eda-genero"),
                                dcc.Graph(id="eda-faixa-etaria"),
                                dcc.Graph(id="eda-raca"),
                                dcc.Graph(id="eda-tipos"),
                                dcc.Graph(id="eda-satisfacao-box"), # Renomeado
                                dcc.Graph(id="eda-mapa-bar"), # Renomeado
                            ],
                        )
                    ],
                ),
                # Fim da Aba EDA

                # --- ABA 3: TABELA DE DADOS (AMOSTRA) ---
                dcc.Tab(
                    label="Amostra dos Dados (Parquet)",
                    value="tab-dados",
                    children=[
                        html.Div(
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
                            ],
                        )
                    ],
                ),  # Fim da Aba 3
            ],
        ),  # Fim do dcc.Tabs
    ]
)

# --- 4. CALLBACKS (O CÉREBRO) ---

# Callback 4.1: Mostrar/Esconder Filtros
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

# Em app.py, cole isso ANTES do "Callback 4.2"

# --- Callback 4.1-B: Gerenciador do Filtro de Clique ---
@app.callback(
    Output("memoria-filtro-tipo", "data"),
    Input("grafico-tipo", "clickData"),
    Input("botao-limpar-tipo", "n_clicks"),
)
def gerenciar_filtro_clique(clique_grafico, clique_limpar):
    # Pega o ID do componente que disparou o callback
    trigger = ctx.triggered_id

    if trigger == "botao-limpar-tipo":
        return None # Limpa a memória

    if trigger == "grafico-tipo" and clique_grafico:
        # Pega o valor do eixo X da barra clicada
        valor_clicado = clique_grafico['points'][0]['x']
        return valor_clicado # Salva o valor na memória

    return no_update # Não faz nada se o callback foi disparado por outro motivo


# Callback 4.2: Atualizar TODOS os Gráficos (MODIFICADO)
@app.callback(
    [
        # 11 Gráficos...
        Output("grafico-volume-ano", "figure"),
        Output("grafico-tipo", "figure"),
        Output("grafico-orgaos", "figure"),
        Output("grafico-satisfacao-hist", "figure"),
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
        Input("memoria-filtro-tipo", "data") # <-- ADICIONA A MEMÓRIA COMO INPUT
    ]
)
def atualizar_graficos(anos_selecionados, ufs_selecionadas, tipo_clicado): # <-- NOVO ARGUMENTO
    print("Callback disparado. Lendo do Parquet com PyArrow...")

    empty_fig = {}
    if not anos_selecionados or not ufs_selecionadas:
        print("Filtros vazios, retornando gráficos em branco.")
        return [empty_fig] * 11 

    # --- 1. CONSTRUÇÃO DOS FILTROS ---
    filtros_parquet = [
        ("ano_registro", "in", anos_selecionados),
        ("uf_do_municipio_manifestante", "in", ufs_selecionadas),
    ]

    # --- A MÁGICA DO CROSS-FILTERING ---
    if tipo_clicado:
        print(f"Filtrando também por TIPO: {tipo_clicado}")
        # Adiciona o filtro de "tipo" à lista de filtros do Parquet
        filtros_parquet.append(("tipo_manifestacao", "==", tipo_clicado))
    # --- FIM DA MÁGICA ---


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
            filters=filtros_parquet, # <-- O filtro de "tipo" agora está aqui
            engine="pyarrow",
        )
    except Exception as e:
        print(f"ERRO ao ler Parquet com filtros: {e}")
        return [empty_fig] * 11

    if df_filtrado.empty:
        print("Query não retornou dados.")
        return [empty_fig] * 11
    
    # ... O RESTO DA SUA FUNÇÃO (GERAR GRÁFICOS) CONTINUA EXATAMENTE IGUAL ...
    # (Não precisa colar o resto, só o que mostrei acima)

    print(f"Leitura do Parquet retornou {len(df_filtrado)} linhas.")

    # --- 3. GERAR OS GRÁFICOS (Dashboard) ---
    manifestacoes_por_ano = (
        df_filtrado.groupby("ano_registro").size().reset_index(name="total")
    )
    fig_ano = px.line(
        manifestacoes_por_ano, x="ano_registro", y="total",
        title="Total de Manifestações por Ano", markers=True,
    )

    tipo_counts_dash = (
        df_filtrado["tipo_manifestacao"].value_counts().reset_index(name="Contagem")
    )
    fig_tipo_dash = px.bar(
        tipo_counts_dash, x="tipo_manifestacao", y="Contagem",
        title="Distribuição por Tipo de Manifestação",
    )

    orgao_counts = (
        df_filtrado["nome_orgao"].value_counts().head(20).reset_index(name="Contagem")
    )
    fig_orgaos = px.bar(
        orgao_counts, y="nome_orgao", x="Contagem",
        orientation="h", title="Top 20 Órgãos Mais Demandados",
    )
    fig_orgaos.update_layout(yaxis={"categoryorder": "total ascending"})

    df_filtrado["em_atraso"] = pd.to_numeric(df_filtrado["dias_de_atraso"], errors='coerce').fillna(0) > 0
    fig_satisfacao_hist = px.histogram(
        df_filtrado.dropna(subset=["satisfacao"]),
        x="satisfacao", color="em_atraso", barmode="group",
        title="Satisfação vs. Atraso na Resposta",
    )

    # --- 4. GERAR OS GRÁFICOS (EDA) ---
    fig_eda_volume = grafico_volume_tempo(df_filtrado.copy())
    fig_eda_genero = grafico_genero(df_filtrado)
    fig_eda_faixa = grafico_faixa_etaria(df_filtrado)
    fig_eda_raca = grafico_raca(df_filtrado) 
    fig_eda_tipos = grafico_tipos(df_filtrado)
    fig_eda_satisfacao_box = grafico_satisfacao(df_filtrado.copy())
    fig_eda_mapa = grafico_mapa(df_filtrado)

    # --- 5. RETORNAR TUDO ---
    return (
        fig_ano, fig_tipo_dash, fig_orgaos, fig_satisfacao_hist,
        fig_eda_volume, fig_eda_genero, fig_eda_faixa,
        fig_eda_raca, fig_eda_tipos, fig_eda_satisfacao_box,
        fig_eda_mapa,
    )

# --- 5. EXECUÇÃO DO APP ---
if __name__ == "__main__":
    app.run(debug=True)