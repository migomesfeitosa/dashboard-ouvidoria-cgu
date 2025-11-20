# src/callbacks/cb_tematica.py

from dash import Input, Output
import plotly.express as px
import pandas as pd
from src.utils import ler_dados_filtrados, criar_grafico_responsivo, TEMA_GRAFICOS

def registrar_callbacks_tematica(app):

    @app.callback(
        [
            Output("grafico-tipos-assuntos", "figure"),
            Output("grafico-esfera-servico", "figure"),
            Output("grafico-orgaos-tematico", "figure"),
            Output("grafico-evolucao-temas", "figure"),
        ],
        [
            Input("filtro-ano", "value"),
            Input("filtro-uf", "value"),
            Input("memoria-filtro-tipo", "data"),
        ],
    )
    def atualizar_tematica(anos, ufs, tipo):
        df = ler_dados_filtrados(anos, ufs, tipo)

        empty = {"layout": {"template": TEMA_GRAFICOS,
                            "title": {"text": "Sem dados"}}}

        if df.empty:
            return [empty] * 4

        try:
            # Tipos x Assuntos
            tipo_assunto = df.groupby(["tipo_manifestacao", "assunto"]) \
                             .size().reset_index(name="contagem")

            fig_tipo_assunto = px.treemap(
                tipo_assunto,
                path=["tipo_manifestacao", "assunto"],
                values="contagem",
                template=TEMA_GRAFICOS,
            )

            # Esfera x Serviço
            esfera_serv = df.groupby(["esfera", "servico"]) \
                            .size().reset_index(name="total")

            fig_esfera = px.bar(esfera_serv,
                                x="servico",
                                y="total",
                                color="esfera",
                                template=TEMA_GRAFICOS,
                                title="Esfera x Serviço")

            # Órgãos mais demandados
            org = df["nome_orgao"].value_counts().head(20).reset_index()
            org.columns = ["nome_orgao", "total"]

            fig_orgaos = px.bar(
                org.sort_values("total", ascending=True),
                x="total",
                y="nome_orgao",
                orientation="h",
                template=TEMA_GRAFICOS,
                title="Top 20 Órgãos Mais Demandados",
            )

            # Evolução dos temas
            df["data_registro"] = pd.to_datetime(df["data_registro"], errors="coerce")
            df["mes"] = df["data_registro"].dt.to_period("M").astype(str)

            temas_time = df.groupby(["mes", "tipo_manifestacao"]) \
                           .size().reset_index(name="contagem")

            fig_evolucao = px.line(
                temas_time,
                x="mes",
                y="contagem",
                color="tipo_manifestacao",
                template=TEMA_GRAFICOS,
                title="Evolução dos Temas ao Longo do Tempo",
            )

            return (
                criar_grafico_responsivo(fig_tipo_assunto),
                criar_grafico_responsivo(fig_esfera),
                criar_grafico_responsivo(fig_orgaos),
                criar_grafico_responsivo(fig_evolucao),
            )

        except Exception as e:
            print("Erro atualizar_tematica:", e)
            return [empty] * 4
