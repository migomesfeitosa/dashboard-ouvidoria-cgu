from dash import html, dcc

def layout_executivo():
    return html.Div(
        className="container-principal",
        children=[
            html.H2(
                "Visão Executiva - KPIs Estratégicos",
                style={"textAlign": "center", "marginBottom": "30px"},
            ),

            # KPIs
            html.Div(
                className="kpi-grid",
                children=[
                    html.Div(
                        className="kpi-card",
                        children=[
                            html.Div("Volume Total", className="kpi-title"),
                            html.Div(id="kpi-volume-total", className="kpi-value"),
                        ],
                    ),
                    html.Div(
                        className="kpi-card",
                        children=[
                            html.Div("Taxa de Resolução", className="kpi-title"),
                            html.Div(id="kpi-taxa-resolucao", className="kpi-value"),
                        ],
                    ),
                    html.Div(
                        className="kpi-card",
                        children=[
                            html.Div("Satisfação Média", className="kpi-title"),
                            html.Div(id="kpi-satisfacao-exec", className="kpi-value"),
                        ],
                    ),
                    html.Div(
                        className="kpi-card",
                        children=[
                            html.Div("Tempo Médio Resposta", className="kpi-title"),
                            html.Div(id="kpi-tempo-resposta", className="kpi-value"),
                        ],
                    ),
                ],
            ),

            # Primeira linha de gráficos
            html.Div(
                className="grid-1-1",
                children=[
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Evolução Mensal das Manifestações", className="grafico-title"),
                            dcc.Graph(id="grafico-evolucao-mensal-exec"),
                        ],
                    ),
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Satisfação por UF", className="grafico-title"),
                            dcc.Graph(id="grafico-satisfacao-por-uf"),
                        ],
                    ),
                ],
            ),

            # Segunda linha
            html.Div(
                className="grid-1-1",
                children=[
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Top 10 Órgãos Mais Demandados", className="grafico-title"),
                            dcc.Graph(id="grafico-top-orgaos-exec"),
                        ],
                    ),
                    html.Div(
                        className="card-grafico",
                        children=[
                            html.Div("Eficiência no Atendimento", className="grafico-title"),
                            dcc.Graph(id="grafico-eficiencia-atendimento"),
                        ],
                    ),
                ],
            ),
        ],
    )
