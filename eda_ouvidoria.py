# eda_ouvidoria.py
import pandas as pd
import plotly.express as px

ARQUIVO_PARQUET = "ouvidoria.parquet"

# ============================================================
# Função base: carregar dados
# ============================================================
def carregar_dados():
    """Carrega todos os dados do Parquet."""
    print("Carregando dados completos para a aba EDA...")
    try:
        # --- MUDANÇA AQUI ---
        df = pd.read_parquet(ARQUIVO_PARQUET, engine="pyarrow")
        # --- FIM DA MUDANÇA ---
        print(f"Dados carregados com sucesso: {len(df)} linhas.")
        return df
    except Exception as e:
        print(f"ERRO ao carregar dados: {e}")
        return pd.DataFrame()


# ============================================================
# Gráficos
# ============================================================

def grafico_volume_tempo(df):
    # Verifica se 'data_registro' foi carregada corretamente
    if not pd.api.types.is_datetime64_any_dtype(df['data_registro']):
         df["data_registro"] = pd.to_datetime(df["data_registro"])
         
    df["mes"] = df["data_registro"].dt.month
    volume_tempo = df.groupby(["ano_registro", "mes"]).size().reset_index(name="total")
    fig = px.line(
        volume_tempo,
        x="mes",
        y="total",
        color="ano_registro",
        title="Evolução Mensal das Manifestações (por Ano Filtrado)",
    )
    return fig


def grafico_genero(df):
    return px.pie(df, names="genero", title="Distribuição por Gênero")


def grafico_faixa_etaria(df):
    df_faixa = df["faixa_etaria"].value_counts().reset_index()
    df_faixa.columns = ["faixa_etaria", "count"]
    fig = px.bar(
        df_faixa,
        x="faixa_etaria",
        y="count",
        title="Distribuição por Faixa Etária",
        text_auto=True,
    )
    return fig


def grafico_raca(df):
    raca_counts = df["raca_cor"].value_counts().reset_index()
    raca_counts.columns = ["raca_cor", "contagem"]
    fig = px.bar(
        raca_counts,
        x="raca_cor",
        y="contagem",
        title="Distribuição por Raça/Cor",
    )
    return fig


def grafico_tipos(df):
    tipo_counts = df["tipo_manifestacao"].value_counts().head(10).reset_index()
    tipo_counts.columns = ["tipo_manifestacao", "contagem"]
    fig = px.bar(
        tipo_counts,
        x="tipo_manifestacao",
        y="contagem",
        title="Top 10 Tipos de Manifestação",
    )
    return fig


def grafico_satisfacao(df):
    # Coluna 'dias_de_atraso' pode não ser 'float' se foi corrigida no ETL
    df["em_atraso"] = pd.to_numeric(df["dias_de_atraso"], errors='coerce').fillna(0) > 0
    fig = px.box(
        df.dropna(subset=["satisfacao"]),
        x="em_atraso",
        y="satisfacao",
        title="Distribuição da Satisfação por Atraso na Resposta",
        labels={"em_atraso": "Em Atraso?", "satisfacao": "Nível de Satisfação"},
    )
    return fig


def grafico_mapa(df):
    # --- MUDANÇA AQUI: Gráfico de mapa trocado por barras ---
    uf_counts = df["uf_do_municipio_manifestante"].value_counts().head(30).reset_index()
    uf_counts.columns = ["UF", "Total"]
    
    fig = px.bar(
        uf_counts.sort_values(by="Total", ascending=True), # Ordena para o gráfico
        x="Total",
        y="UF",
        orientation='h', # Gráfico horizontal
        title="Top 30 Manifestações por UF",
        labels={"UF": "UF do Manifestante", "Total": "Quantidade"},
        text_auto=True,
    )
    fig.update_layout(yaxis_title=None)
    return fig
    # --- FIM DA MUDANÇA ---