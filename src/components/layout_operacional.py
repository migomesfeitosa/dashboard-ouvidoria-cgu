from dash import html, dcc

def layout_operacional():
    return html.Div(
        className="container-principal",
        children=[
            html.H2(
                "Análise Operacional - Performance do Atendimento",
                style={"textAlign": "center", "marginBottom": "30px"},
            ),

            html.Div(
                className="grid-1-1",
                children=[
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Gestão de Prazos de Resposta", className="grafico-title"),
                            dcc.Graph(id="grafico-prazos-resposta"),
                        ],
                    ),
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Atrasos por Órgão (Top 15)", className="grafico-title"),
                            dcc.Graph(id="grafico-atrasos-por-orgao"),
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
                            html.Div("Eficácia na Demanda Atendida", className="grafico-title"),
                            dcc.Graph(id="grafico-demanda-atendida"),
                        ],
                    ),
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Situação das Manifestações", className="grafico-title"),
                            dcc.Graph(id="grafico-situacao-manifestacoes"),
                        ],
                    ),
                ],
            ),

            html.Div(
                className="card-grafico",
                children=[
                    html.Div("Análise por Formulário e Tipo de Serviço", className="grafico-title"),
                    dcc.Graph(id="grafico-formulario-servico"),
                ],
            ),
        ],
    )
