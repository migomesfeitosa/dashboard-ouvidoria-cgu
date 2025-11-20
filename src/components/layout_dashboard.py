from dash import html, dcc

def layout_dashboard():
    return html.Div(
        className="container-principal",
        children=[
            html.H2(
                "Painel Geral – Visão Integrada",
                style={"textAlign": "center", "marginBottom": "30px"},
            ),

            # Linha 1 KPIs
            html.Div(
                className="kpi-grid",
                children=[
                    html.Div(
                        className="kpi-card",
                        children=[
                            html.Div("Total de Manifestações", className="kpi-title"),
                            html.Div(id="kpi-total-geral", className="kpi-value"),
                        ],
                    ),
                    html.Div(
                        className="kpi-card",
                        children=[
                            html.Div("Tempo Médio de Resposta", className="kpi-title"),
                            html.Div(id="kpi-tempo-medio-geral", className="kpi-value"),
                        ],
                    ),
                    html.Div(
                        className="kpi-card",
                        children=[
                            html.Div("Taxa de Conclusão", className="kpi-title"),
                            html.Div(id="kpi-taxa-conclusao-geral", className="kpi-value"),
                        ],
                    ),
                    html.Div(
                        className="kpi-card",
                        children=[
                            html.Div("Satisfação Média", className="kpi-title"),
                            html.Div(id="kpi-satisfacao-geral", className="kpi-value"),
                        ],
                    ),
                ],
            ),

            # Linha 2 gráficos
            html.Div(
                className="grid-1-1",
                children=[
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Volume por Mês", className="grafico-title"),
                            dcc.Graph(id="grafico-volume-mes"),
                        ],
                    ),
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Tipos de Manifestação", className="grafico-title"),
                            dcc.Graph(id="grafico-tipo"),
                        ],
                    ),
                ],
            ),

            # Linha 3
            html.Div(
                className="grid-1-1",
                children=[
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Órgãos Mais Demandados", className="grafico-title"),
                            dcc.Graph(id="grafico-top-orgaos"),
                        ],
                    ),
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Satisfação", className="grafico-title"),
                            dcc.Graph(id="grafico-satisfacao-hist"),
                        ],
                    ),
                ],
            ),
        ],
    )
