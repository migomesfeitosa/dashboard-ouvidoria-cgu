# src/callbacks/cb_filtros.py
from dash import Input, Output, State, ctx
from dash.exceptions import PreventUpdate
from eda_ouvidoria import *  # se precisar das funções de plot (ou importe explicitamente)
from src.utils import carregar_opcoes_filtros

# carregue 'opcoes' uma única vez para o app
opcoes = carregar_opcoes_filtros()

def registrar_callbacks_filtros(app):
    @app.callback(Output("container-filtros", "style"),
                  Input("botao-toggle-filtros", "n_clicks"),
                  State("container-filtros", "style"))
    def toggle_filtros_visibility(n_clicks, current_style):
        if n_clicks is None:
            return current_style or {"display": "none"}
        if not current_style:
            current_style = {"display": "none"}
        current_style["display"] = "block" if current_style.get("display") == "none" else "none"
        return current_style

    @app.callback(Output("memoria-filtro-tipo", "data"),
                  Input("grafico-tipo", "clickData"),
                  Input("botao-limpar-tipo", "n_clicks"))
    def gerenciar_filtro_clique(clique_grafico, clique_limpar):
        if not ctx.triggered:
            raise PreventUpdate
        trigger = ctx.triggered_id
        if trigger == "botao-limpar-tipo":
            return None
        if trigger == "grafico-tipo" and clique_grafico:
            valor = clique_grafico["points"][0]["x"]
            return valor
        raise PreventUpdate
