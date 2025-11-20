# src/callbacks/cb_predicao.py
from dash import Input, Output, State, html
from src.utils import carregar_modelo
import pandas as pd

modelo = carregar_modelo()

def registrar_callbacks_predicao(app):
    @app.callback(
        Output("resultado-predicao", "children"),
        Input("botao-prever", "n_clicks"),
        [
            State("ml-input-assunto", "value"),
            State("ml-input-orgao", "value"),
            State("ml-input-tipo", "value"),
            State("ml-input-genero", "value"),
            State("ml-input-faixa", "value"),
            State("ml-input-raca", "value"),
            State("ml-input-uf", "value"),
        ],
        prevent_initial_call=True,
    )
    def callback_prever_satisfacao(n_clicks, assunto, orgao, tipo, genero, faixa, raca, uf):
        if modelo is None:
            return html.P("ERRO: modelo não carregado.", style={"color":"red"})
        if not all([assunto, orgao, tipo, genero, faixa, raca, uf]):
            return html.P("Preencha todos os campos.", style={"color":"orange"})
        dados = {
            "tipo_manifestacao":[tipo],
            "nome_orgao":[orgao],
            "genero":[genero],
            "faixa_etaria":[faixa],
            "raca_cor":[raca],
            "uf_do_municipio_manifestante":[uf],
            "assunto":[assunto if assunto else "sem assunto"]
        }
        df_novo = pd.DataFrame(dados)
        try:
            probs = modelo.predict_proba(df_novo)
            prob_insat = probs[0][1]
            pct = prob_insat*100
            if prob_insat > 0.6:
                risco = "Alto"
                estilo = {"color":"#d9534f","fontWeight":"bold"}
            elif prob_insat > 0.4:
                risco = "Médio"
                estilo = {"color":"orange","fontWeight":"bold"}
            else:
                risco = "Baixo"
                estilo = {"color":"#5cb85c","fontWeight":"bold"}
            return html.Div([
                html.H3("Resultado da Predição:"),
                html.P(f"Risco de Insatisfação: {risco}", style=estilo),
                html.P(f"Probabilidade de Insatisfação: {pct:.1f}%")
            ])
        except Exception as e:
            print("Erro na predição:", e)
            return html.P(f"Erro na predição: {e}", style={"color":"red"})
