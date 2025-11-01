# eda_ouvidoria.py (ATUALIZADO)
import pandas as pd
import plotly.express as px

ARQUIVO_PARQUET = "ouvidoria.parquet"
TEMA_GRAFICOS = "plotly_white" # <--- NOSSA CONSTANTE DE TEMA

# ============================================================
# Função base: carregar dados (Sem mudanças)
# ============================================================
def carregar_dados():
    """Carrega todos os dados do Parquet."""
    print("Carregando dados completos para a aba EDA...")
    try:
        df = pd.read_parquet(ARQUIVO_PARQUET, engine="pyarrow")
        print(f"Dados carregados com sucesso: {len(df)} linhas.")
        return df
    except Exception as e:
        print(f"ERRO ao carregar dados: {e}")
        return pd.DataFrame()


# ============================================================
# Gráficos (COM MELHORIAS)
# ============================================================

def grafico_volume_tempo(df):
    if not pd.api.types.is_datetime64_any_dtype(df['data_registro']):
         df["data_registro"] = pd.to_datetime(df["data_registro"])
         
    df["mes"] = df["data_registro"].dt.month
    volume_tempo = df.groupby(["ano_registro", "mes"]).size().reset_index(name="total")
    fig = px.line(
        volume_tempo,
        x="mes",
        y="total",
        color="ano_registro",
        title="Evolução Mensal das Manifestações",
        template=TEMA_GRAFICOS # <--- APLICA O TEMA
    )
    fig.update_layout(title_x=0.5) # Centraliza o título
    return fig


def grafico_genero(df):
    # --- MELHORIA: Trocado de Pizza (Pie) para Barras Horizontais ---
    df_genero = df['genero'].value_counts().reset_index(name="Total")
    
    fig = px.bar(
        df_genero.sort_values(by="Total", ascending=True), # Ordena
        x="Total",
        y="genero",
        orientation='h',
        title="Distribuição por Gênero",
        template=TEMA_GRAFICOS, # <--- APLICA O TEMA
        text_auto=True # <--- ADICIONA RÓTULOS
    )
    # Limpa os eixos para um visual mais clean
    fig.update_layout(yaxis_title=None, xaxis_title=None, title_x=0.5)
    return fig


def grafico_faixa_etaria(df):
    df_faixa = df["faixa_etaria"].value_counts().reset_index()
    df_faixa.columns = ["faixa_etaria", "count"]
    fig = px.bar(
        df_faixa,
        x="faixa_etaria",
        y="count",
        title="Distribuição por Faixa Etária",
        text_auto=True,
        template=TEMA_GRAFICOS # <--- APLICA O TEMA
    )
    fig.update_layout(title_x=0.5, xaxis_title=None)
    return fig


def grafico_raca(df):
    raca_counts = df["raca_cor"].value_counts().reset_index()
    raca_counts.columns = ["raca_cor", "contagem"]
    fig = px.bar(
        raca_counts,
        x="raca_cor",
        y="contagem",
        title="Distribuição por Raça/Cor",
        template=TEMA_GRAFICOS, # <--- APLICA O TEMA
        text_auto=True # <--- ADICIONA RÓTULOS
    )
    fig.update_layout(title_x=0.5, xaxis_title=None)
    return fig


def grafico_tipos(df):
    tipo_counts = df["tipo_manifestacao"].value_counts().head(10).reset_index()
    tipo_counts.columns = ["tipo_manifestacao", "contagem"]
    fig = px.bar(
        tipo_counts,
        x="tipo_manifestacao",
        y="contagem",
        title="Top 10 Tipos de Manifestação",
        template=TEMA_GRAFICOS, # <--- APLICA O TEMA
        text_auto=True # <--- ADICIONA RÓTULOS
    )
    fig.update_layout(title_x=0.5, xaxis_title=None)
    return fig


def grafico_satisfacao(df):
    df["em_atraso"] = pd.to_numeric(df["dias_de_atraso"], errors='coerce').fillna(0) > 0
    fig = px.box(
        df.dropna(subset=["satisfacao"]),
        x="em_atraso",
        y="satisfacao",
        title="Distribuição da Satisfação por Atraso na Resposta",
        labels={"em_atraso": "Em Atraso?", "satisfacao": "Nível de Satisfação"},
        template=TEMA_GRAFICOS # <--- APLICA O TEMA
    )
    fig.update_layout(title_x=0.5)
    return fig


def grafico_mapa(df):
    uf_counts = df["uf_do_municipio_manifestante"].value_counts().head(30).reset_index()
    uf_counts.columns = ["UF", "Total"]
    
    fig = px.bar(
        uf_counts.sort_values(by="Total", ascending=True), 
        x="Total",
        y="UF",
        orientation='h',
        title="Top 30 Manifestações por UF",
        labels={"UF": "UF do Manifestante", "Total": "Quantidade"},
        text_auto=True,
        template=TEMA_GRAFICOS # <--- APLICA O TEMA
    )
    fig.update_layout(yaxis_title=None, xaxis_title=None, title_x=0.5)
    return fig