# src/callbacks/cb_dashboard.py
from dash import Input, Output, no_update
import plotly.express as px
import pandas as pd
from src.utils import ler_dados_filtrados, criar_grafico_responsivo, TEMA_GRAFICOS
from eda_ouvidoria import grafico_volume_tempo

def registrar_callbacks_dashboard(app):
    # Callback 1: Atualiza os gráficos do Dashboard
    @app.callback(
        [
            Output("grafico-volume-mes", "figure"),
            Output("grafico-tipo", "figure"),
            Output("grafico-top-orgaos", "figure"),
            Output("grafico-satisfacao-hist", "figure"),
        ],
        [
            Input("filtro-ano", "value"),
            Input("filtro-uf", "value"),
            Input("memoria-filtro-tipo", "data"),
        ],
    )
    def atualizar_dashboard(anos_selecionados, ufs_selecionadas, tipo_clicado):
        df = ler_dados_filtrados(anos_selecionados, ufs_selecionadas, tipo_clicado)
        empty_fig = {"layout": {"template": TEMA_GRAFICOS, "title": {"text": "Sem dados"}}}
        
        if df.empty:
            return empty_fig, empty_fig, empty_fig, empty_fig

        try:
            # 1. Volume por Mês
            fig_volume = grafico_volume_tempo(df.copy())
            
            # 2. Tipos de Manifestação
            tipo_counts = df["tipo_manifestacao"].value_counts().reset_index(name="Contagem")
            fig_tipo = px.bar(tipo_counts, x="tipo_manifestacao", y="Contagem", template=TEMA_GRAFICOS)
            fig_tipo.update_layout(title=None, title_x=0.5)
            
            # 3. Órgãos (Top 20)
            org_counts = df["nome_orgao"].value_counts().head(20).reset_index(name="Contagem")
            fig_orgaos = px.bar(org_counts, y="nome_orgao", x="Contagem", orientation="h", template=TEMA_GRAFICOS)
            fig_orgaos.update_layout(yaxis={"categoryorder": "total ascending"}, title=None)
            
            # 4. Histograma de Satisfação
            df["em_atraso"] = pd.to_numeric(df.get("dias_de_atraso", 0), errors="coerce").fillna(0) > 0
            if "satisfacao" in df.columns:
                fig_satisf = px.histogram(df.dropna(subset=["satisfacao"]), x="satisfacao", color="em_atraso", barmode="group", template=TEMA_GRAFICOS)
                fig_satisf.update_layout(title=None)
            else:
                 fig_satisf = empty_fig

            return (
                criar_grafico_responsivo(fig_volume), 
                criar_grafico_responsivo(fig_tipo), 
                criar_grafico_responsivo(fig_orgaos), 
                criar_grafico_responsivo(fig_satisf)
            )

        except Exception as e:
            print("Erro atualizar_dashboard:", e)
            return empty_fig, empty_fig, empty_fig, empty_fig

    # NOVO CALLBACK: Captura o clique no gráfico (Cross-filtering)
    @app.callback(
        Output("memoria-filtro-tipo", "data", allow_duplicate=True),
        Input("grafico-tipo", "clickData"),
        prevent_initial_call=True
    )
    def atualizar_filtro_por_clique(clickData):
        if clickData:
            valor = clickData["points"][0]["x"]
            return valor
        return no_update