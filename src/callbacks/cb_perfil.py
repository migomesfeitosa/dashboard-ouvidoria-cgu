# src/callbacks/cb_perfil.py

from dash import Input, Output
import plotly.express as px
import pandas as pd
from src.utils import ler_dados_filtrados, criar_grafico_responsivo, TEMA_GRAFICOS

def registrar_callbacks_perfil(app):

    @app.callback(
        [
            Output("grafico-distribuicao-demografica", "figure"),
            Output("grafico-genero-raca", "figure"),
            Output("grafico-mapa-manifestantes", "figure"),
            Output("grafico-uf-comparacao", "figure"),
            Output("grafico-satisfacao-perfil", "figure"),
        ],
        [
            Input("filtro-ano", "value"),
            Input("filtro-uf", "value"),
            Input("memoria-filtro-tipo", "data"),
        ],
    )
    def atualizar_perfil(anos, ufs, tipo):
        df = ler_dados_filtrados(anos, ufs, tipo)

        empty = {"layout": {"template": TEMA_GRAFICOS,
                            "title": {"text": "Sem dados"}}}

        if df.empty:
            return [empty] * 5

        try:
            # Gênero
            genero_counts = df["genero"].value_counts().reset_index()
            genero_counts.columns = ["genero", "total"]
            fig_genero = px.bar(genero_counts,
                                x="genero", y="total",
                                template=TEMA_GRAFICOS,
                                title="Distribuição por Gênero")

            # Gênero x Raça
            genero_raca = df.groupby(["genero", "raca_cor"]).size().reset_index(name="contagem")
            fig_genero_raca = px.bar(genero_raca,
                                     x="contagem",
                                     y="genero",
                                     color="raca_cor",
                                     orientation="h",
                                     template=TEMA_GRAFICOS,
                                     title="Gênero x Raça/Cor")

            # Mapa (na verdade gráfico horizontal por UF)
            uf_counts = df["uf_do_municipio_manifestante"].value_counts().reset_index()
            uf_counts.columns = ["UF", "total"]
            fig_mapa = px.bar(uf_counts,
                              x="total", y="UF",
                              orientation="h",
                              template=TEMA_GRAFICOS,
                              title="Manifestações por UF")

            # Comparação UFs – média de satisfação
            df2 = df.copy()
            df2["satisfacao_num"] = df2["satisfacao"].astype(str).str.extract(r"\((\d)\)").astype(float)
            df2 = df2.dropna(subset=["satisfacao_num"])

            satisf_uf = df2.groupby("uf_do_municipio_manifestante")["satisfacao_num"] \
                           .mean().reset_index()

            fig_uf_comp = px.bar(satisf_uf,
                                 x="uf_do_municipio_manifestante",
                                 y="satisfacao_num",
                                 template=TEMA_GRAFICOS,
                                 title="Satisfação Média por UF")

            # Satisfação por Demografia
            fig_sat_dem = px.box(df2,
                                 x="genero",
                                 y="satisfacao_num",
                                 color="raca_cor",
                                 template=TEMA_GRAFICOS,
                                 title="Satisfação por Perfil Demográfico")

            return (
                criar_grafico_responsivo(fig_genero),
                criar_grafico_responsivo(fig_genero_raca),
                criar_grafico_responsivo(fig_mapa),
                criar_grafico_responsivo(fig_uf_comp),
                criar_grafico_responsivo(fig_sat_dem),
            )

        except Exception as e:
            print("Erro atualizar_perfil:", e)
            return [empty] * 5
