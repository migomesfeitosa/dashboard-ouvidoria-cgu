# src/utils.py
import os
import pandas as pd
import joblib
import plotly.express as px

ARQUIVO_PARQUET = "ouvidoria.parquet"
TEMA_GRAFICOS = "plotly_white"
ARQUIVO_MODELO = "modelo_satisfacao.joblib"

# Carrega opções para dropdowns (same logic do seu app original)
def carregar_opcoes_filtros():
    try:
        colunas_necessarias = [
            "ano_registro",
            "uf_do_municipio_manifestante",
            "tipo_manifestacao",
            "nome_orgao",
            "genero",
            "faixa_etaria",
            "raca_cor",
        ]
        df = pd.read_parquet(ARQUIVO_PARQUET, columns=colunas_necessarias, engine="pyarrow")
        anos_unicos = sorted(df["ano_registro"].dropna().unique().astype(int))
        ufs_unicas = sorted(df["uf_do_municipio_manifestante"].dropna().unique())
        tipos_unicos = sorted(df["tipo_manifestacao"].dropna().unique())
        orgaos_unicos = sorted(df["nome_orgao"].value_counts().head(1000).index)
        generos_unicos = sorted(df["genero"].dropna().unique())
        faixas_unicas = sorted(df["faixa_etaria"].dropna().unique())
        racas_unicas = sorted(df["raca_cor"].dropna().unique())
        return {
            "anos": [{"label": a, "value": a} for a in anos_unicos],
            "ufs": [{"label": u.upper(), "value": u} for u in ufs_unicas],
            "anos_lista": anos_unicos,
            "ufs_lista": ufs_unicas,
            "tipos_ml": [{"label": i, "value": i} for i in tipos_unicos],
            "orgaos_ml": [{"label": i, "value": i} for i in orgaos_unicos],
            "generos_ml": [{"label": i, "value": i} for i in generos_unicos],
            "faixas_ml": [{"label": i, "value": i} for i in faixas_unicas],
            "racas_ml": [{"label": i, "value": i} for i in racas_unicas],
            "ufs_ml": [{"label": u.upper(), "value": u} for u in ufs_unicas],
        }
    except Exception as e:
        print("Erro carregar_opcoes_filtros:", e)
        return {
            "anos": [{"label": 2025, "value": 2025}],
            "ufs": [{"label": "BR", "value": "BR"}],
            "anos_lista": [2025],
            "ufs_lista": ["BR"],
            "tipos_ml": [],
            "orgaos_ml": [],
            "generos_ml": [],
            "faixas_ml": [],
            "racas_ml": [],
            "ufs_ml": [],
        }

# Função principal de leitura filtrada (usa filtros do parquet)
def ler_dados_filtrados(anos, ufs, tipo_clicado):
    if not anos or not ufs:
        return pd.DataFrame()
    filtros_parquet = [
        ("ano_registro", "in", anos),
        ("uf_do_municipio_manifestante", "in", ufs),
    ]
    if tipo_clicado:
        filtros_parquet.append(("tipo_manifestacao", "==", tipo_clicado))
    colunas_necessarias = [
        "ano_registro",
        "data_registro",
        "tipo_manifestacao",
        "nome_orgao",
        "satisfacao",
        "dias_de_atraso",
        "genero",
        "faixa_etaria",
        "raca_cor",
        "uf_do_municipio_manifestante",
        # campos opcionais:
        "data_resposta",
        "dias_para_resolucao",
        "situacao",
    ]
    colunas_necessarias = list(set(colunas_necessarias))
    try:
        df = pd.read_parquet(ARQUIVO_PARQUET, columns=colunas_necessarias, filters=filtros_parquet, engine="pyarrow")
        return df
    except Exception as e:
        print("Erro ler_dados_filtrados:", e)
        return pd.DataFrame()

# Layouts/fig helpers
def criar_grafico_responsivo(fig, altura=400):
    try:
        fig.update_layout(autosize=True, height=altura, margin=dict(l=50, r=50, t=50, b=50),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    except Exception:
        pass
    return fig

# Carrega modelo de ML (retorna None se falhar)
def carregar_modelo():
    try:
        model = joblib.load(ARQUIVO_MODELO)
        print("Modelo carregado:", ARQUIVO_MODELO)
        return model
    except Exception as e:
        print("Falha ao carregar modelo:", e)
        return None

# Opcional: expose tema
TEMAS = {"plotly": "plotly_white"}
