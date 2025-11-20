from dash import html, dcc

def layout_analise_tematica():
    return html.Div(
        className="container-principal",
        children=[
            html.H2("Análise Temática - Conteúdo das Manifestações"),

            html.Div(
                className="card-grafico",
                children=[
                    html.H3("Tipos de Manifestação e Assuntos"),
                    dcc.Graph(id="grafico-tipos-assuntos"),
                ],
            ),

            html.Div(
                style={"display": "flex", "gap": "20px"},
                children=[
                    html.Div(
                        style={"flex": 1},
                        children=[
                            html.H3("Análise por Esfera e Serviço"),
                            dcc.Graph(id="grafico-esfera-servico"),
                        ],
                    ),
                    html.Div(
                        style={"flex": 1},
                        children=[
                            html.H3("Órgãos Mais Demandados"),
                            dcc.Graph(id="grafico-orgaos-tematico"),
                        ],
                    ),
                ],
            ),

            html.Div(
                className="card-grafico",
                children=[
                    html.H3("Evolução dos Temas ao Longo do Tempo"),
                    dcc.Graph(id="grafico-evolucao-temas"),
                ],
            ),
        ],
    )
