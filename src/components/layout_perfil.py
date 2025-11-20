from dash import html, dcc

def layout_perfil_usuario():
    return html.Div(
        className="container-principal",
        children=[
            html.H2(
                "Perfil do Usuário - Análise Demográfica",
                style={"textAlign": "center", "marginBottom": "30px"},
            ),

            html.Div(
                className="grid-1-1",
                children=[
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Distribuição por Gênero", className="grafico-title"),
                            dcc.Graph(id="grafico-distribuicao-demografica"),
                        ],
                    ),
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Distribuição por Raça/Cor", className="grafico-title"),
                            dcc.Graph(id="grafico-genero-raca"),
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
                            html.Div("Distribuição por UF", className="grafico-title"),
                            dcc.Graph(id="grafico-mapa-manifestantes"),
                        ],
                    ),
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Comparação entre UFs", className="grafico-title"),
                            dcc.Graph(id="grafico-uf-comparacao"),
                        ],
                    ),
                ],
            ),

            html.Div(
                className="card-grafico",
                children=[
                    html.Div("Satisfação por Perfil Demográfico", className="grafico-title"),
                    dcc.Graph(id="grafico-satisfacao-perfil"),
                ],
            ),
        ],
    )
