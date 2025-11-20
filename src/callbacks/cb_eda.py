# src/callbacks/cb_eda.py
from dash import Input, Output
from src.utils import ler_dados_filtrados, criar_grafico_responsivo, TEMA_GRAFICOS
from eda_ouvidoria import (
    grafico_volume_tempo, 
    grafico_genero, 
    grafico_faixa_etaria, 
    grafico_raca, 
    grafico_mapa
)
import plotly.express as px

def registrar_callbacks_eda(app):
    @app.callback(
        [
            Output("eda-volume-tempo", "figure"),
            Output("eda-distribuicao-genero", "figure"), # ID CORRIGIDO
            Output("eda-faixa-etaria", "figure"),
            Output("eda-raca", "figure"),
            Output("eda-mapa-uf", "figure"),             # ID CORRIGIDO
        ],
        [
            Input("filtro-ano", "value"),
            Input("filtro-uf", "value"),
            Input("memoria-filtro-tipo", "data"),
        ],
    )
    def atualizar_eda(anos, ufs, tipo):
        df = ler_dados_filtrados(anos, ufs, tipo)
        
        # Figura vazia padrão para evitar erros
        empty = {"layout": {"template": TEMA_GRAFICOS, "title": {"text": "Sem dados"}}}
        
        if df.empty:
            return [empty] * 5 # Retorna 5 gráficos vazios

        try:
            # Gera os gráficos usando as funções do eda_ouvidoria.py
            f1 = grafico_volume_tempo(df.copy())
            f2 = grafico_genero(df.copy())
            f3 = grafico_faixa_etaria(df.copy())
            f4 = grafico_raca(df.copy())
            f5 = grafico_mapa(df.copy())
            
            return [
                criar_grafico_responsivo(f1),
                criar_grafico_responsivo(f2),
                criar_grafico_responsivo(f3),
                criar_grafico_responsivo(f4),
                criar_grafico_responsivo(f5)
            ]
        except Exception as e:
            print("Erro atualizar_eda:", e)
            return [empty] * 5