# src/callbacks/cb_operacional.py
from src.utils import ler_dados_filtrados, criar_grafico_responsivo
from dash import Input, Output
import plotly.express as px
import pandas as pd

def registrar_callbacks_operacional(app):
    @app.callback(Output("grafico-prazos-resposta", "figure"),
                  [Input("filtro-ano", "value"), Input("filtro-uf", "value")])
    def graf_prazos(anos, ufs):
        df = ler_dados_filtrados(anos, ufs, None)
        if df.empty:
            return criar_grafico_responsivo(px.bar(title="Sem dados"))
        # placeholder: usar dias_de_atraso/dias_para_resolucao
        df2 = df.copy()
        df2["dias_de_atraso"] = pd.to_numeric(df2.get("dias_de_atraso",0), errors="coerce").fillna(0)
        fig = px.histogram(df2, x="dias_de_atraso", nbins=30, title="Prazos de Resposta")
        return criar_grafico_responsivo(fig)

    # Você pode adicionar mais callbacks aqui (atrasos por órgão, demanda atendida, etc.)
