from dash import html, dcc

def layout_eda():
    return html.Div(
        className="container-principal",
        children=[
            html.H2(
                "Análise Exploratória de Dados (EDA)",
                style={"textAlign": "center", "marginBottom": "30px"},
            ),

            html.Div(
                className="grid-1-1",
                children=[
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Volume ao Longo do Tempo", className="grafico-title"),
                            dcc.Graph(id="eda-volume-tempo"),
                        ],
                    ),
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Distribuição por Gênero", className="grafico-title"),
                            dcc.Graph(id="eda-distribuicao-genero"),
                        ],
                    ),
                ],
            ),

            html.Div(
                className="grid-1-1",
                children=[
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Faixa Etária", className="grafico-title"),
                            dcc.Graph(id="eda-faixa-etaria"),
                        ],
                    ),
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Distribuição por Raça/Cor", className="grafico-title"),
                            dcc.Graph(id="eda-raca"),
                        ],
                    ),
                ],
            ),

            html.Div(
                className="card-grafico",
                children=[
                    html.Div("Mapa de UF", className="grafico-title"),
                    dcc.Graph(id="eda-mapa-uf"),
                ],
            ),
        ],
    )
