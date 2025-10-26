import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State  # <-- Importamos 'State'

ARQUIVO_PARQUET = "ouvidoria.parquet"


# --- 1. CARREGAR OPÇÕES DOS FILTROS (Super leve) ---
# O Parquet permite ler SÓ as colunas que queremos
def carregar_opcoes_filtros():
    print("Carregando opções de filtros do Parquet...")
    try:
        anos_df = pd.read_parquet(
            ARQUIVO_PARQUET, columns=["ano_registro"], engine="fastparquet"
        )
        anos_unicos = sorted(anos_df["ano_registro"].dropna().astype(int).unique())

        ufs_df = pd.read_parquet(
            ARQUIVO_PARQUET,
            columns=["uf_do_municipio_manifestante"],
            engine="fastparquet",
        )
        ufs_unicos = sorted(ufs_df['uf_do_municipio_manifestante'].dropna().unique())

        print("Opções de filtros carregadas.")
        return anos_unicos, ufs_unicos
    except Exception as e:
        print(f"ERRO AO CARREGAR FILTROS DO PARQUET: {e}")
        print("Usando valores padrão.")
        return [2025], ["BR"]


anos_unicos, ufs_unicas = carregar_opcoes_filtros()

# --- 2. CARREGAR AMOSTRA PARA A TABELA (Super leve) ---
try:
    # O Parquet não tem um "LIMIT" fácil, então lemos o DF, pegamos o head, e limpamos
    df_amostra = pd.read_parquet(
        ARQUIVO_PARQUET, columns=None, engine="fastparquet"
    )  # Lê tudo (pode ser lento)
    df_amostra = df_amostra.head(100)  # Pega só os 100 primeiros
    dados_tabela = df_amostra.to_dict("records")
    colunas_tabela = [
        {"name": i.replace("_", " ").title(), "id": i} for i in df_amostra.columns
    ]
    del df_amostra  # Limpa a memória
except Exception as e:
    print(f"ERRO AO CARREGAR AMOSTRA: {e}")
    dados_tabela = []
    colunas_tabela = []


# --- 3. INICIALIZAÇÃO E LAYOUT DO APP ---
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    children=[
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
                                # --- Botão e Filtros Colapsáveis ---
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
                                            value='ufs_unicos',
                                            multi=True,
                                            placeholder="Todas as UFs selecionadas",
                                            className="dropdown-hide-selected",
                                        ),
                                    ],
                                    style={
                                        "padding": "20px",
                                        "backgroundColor": "#f9f9f9",
                                        "marginBottom": "20px",
                                        "display": "none",
                                    },
                                ),
                                # Placeholders dos Gráficos
                                html.H2("1. Volume de Manifestações ao Longo do Tempo"),
                                dcc.Graph(id="grafico-volume-ano"),
                                html.H2("2. Análise dos Tipos de Manifestação"),
                                dcc.Graph(id="grafico-tipo"),
                                html.H2("3. Top 20 Órgãos Mais Demandados"),
                                dcc.Graph(id="grafico-orgaos"),
                                html.H2("4. Satisfação do Usuário vs. Atraso"),
                                dcc.Graph(id="grafico-satisfacao"),
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
                                    f"""
                - **Extração (Extract):** Os 12 arquivos CSV (2014-2025) foram lidos.
                - **Transformação (Transform):** Um script Python (`etl.py`) usando **Pandas** foi executado uma vez. Ele limpou e normalizou os dados (nomes de colunas para `snake_case`, valores padronizados, etc.), processando um arquivo de cada vez para evitar `MemoryError`.
                - **Carga (Load):** O resultado limpo (todos os 11 anos) foi salvo em um único arquivo colunar otimizado: **`ouvidoria.parquet`**.
                - **Visualização:** Este dashboard **lê dados diretamente do arquivo Parquet**, usando filtros otimizados para carregar apenas os dados necessários para os gráficos.
                """
                                ),
                            ],
                        )
                    ],
                ),  # Fim da Aba 2
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
    State("container-filtros", "style"),  # Pega o estilo ATUAL
)
def toggle_filtros_visibility(n_clicks, current_style):
    if n_clicks is None:
        return current_style  # Não faz nada na carga inicial

    if current_style["display"] == "none":
        current_style["display"] = "block"
    else:
        current_style["display"] = "none"
    return current_style


# Callback 4.2: Atualizar Gráficos
@app.callback(
    [
        Output("grafico-volume-ano", "figure"),
        Output("grafico-tipo", "figure"),
        Output("grafico-orgaos", "figure"),
        Output("grafico-satisfacao", "figure"),
    ],
    [Input("filtro-ano", "value"), Input("filtro-uf", "value")],
)
def atualizar_graficos(anos_selecionados, ufs_selecionadas):
    print("Callback disparado. Lendo do Parquet...")

    if not anos_selecionados or not ufs_selecionadas:
        print("Filtros vazios, retornando gráficos em branco.")
        return {}, {}, {}, {}

    # --- 1. A MÁGICA DO PARQUET ---
    # Construímos os filtros para o pyarrow
    # Isso faz o Pandas ler SÓ as linhas e colunas que queremos
    filtros_parquet = [
        ("ano_registro", "in", anos_selecionados),
        ("uf_do_municipio_manifestante", "in", ufs_selecionadas),
    ]

    colunas_necessarias = [
        "ano_registro",
        "tipo_manifestacao",
        "nome_orgao",
        "satisfacao",
        "dias_de_atraso",
    ]

    try:
        df_filtrado = pd.read_parquet(
            ARQUIVO_PARQUET,
            columns=colunas_necessarias,
            filters=filtros_parquet,
            engine="fastparquet",  # <--- ADICIONE AQUI
        )
    except Exception as e:
        print(f"ERRO ao ler Parquet com filtros: {e}")
        return {}, {}, {}, {}

    if df_filtrado.empty:
        print("Query não retornou dados.")
        return {}, {}, {}, {}

    print(f"Leitura do Parquet retornou {len(df_filtrado)} linhas.")

    # --- 3. GERAR OS GRÁFICOS (Este código é o mesmo de antes) ---

    # Gráfico 1 (Volume por Ano)
    manifestacoes_por_ano = (
        df_filtrado.groupby("ano_registro").size().reset_index(name="total")
    )
    fig_ano = px.line(
        manifestacoes_por_ano,
        x="ano_registro",
        y="total",
        title="Total de Manifestações por Ano",
        markers=True,
    )

    # Gráfico 2 (Tipos)
    tipo_counts = (
        df_filtrado["tipo_manifestacao"].value_counts().reset_index(name="Contagem")
    )
    fig_tipo = px.bar(
        tipo_counts,
        x="tipo_manifestacao",
        y="Contagem",
        title="Distribuição por Tipo de Manifestação",
        labels={"tipo_manifestacao": "Tipo", "Contagem": "Contagem"},
    )

    # Gráfico 3 (Top Órgãos)
    orgao_counts = (
        df_filtrado["nome_orgao"].value_counts().head(20).reset_index(name="Contagem")
    )
    fig_orgaos = px.bar(
        orgao_counts,
        y="nome_orgao",
        x="Contagem",
        orientation="h",
        title="Top 20 Órgãos Mais Demandados",
    )
    fig_orgaos.update_layout(
        yaxis={"categoryorder": "total ascending", "title": "Órgão"}
    )

    # Gráfico 4 (Satisfação)
    df_filtrado["em_atraso"] = df_filtrado["dias_de_atraso"] > 0
    fig_satisfacao = px.histogram(
        df_filtrado.dropna(subset=["satisfacao"]),
        x="satisfacao",
        color="em_atraso",
        barmode="group",
        title="Satisfação vs. Atraso na Resposta",
        labels={"em_atraso": "Em Atraso?"},
    )

    return fig_ano, fig_tipo, fig_orgaos, fig_satisfacao


# --- 5. EXECUÇÃO DO APP ---
if __name__ == "__main__":
    app.run(debug=True)
