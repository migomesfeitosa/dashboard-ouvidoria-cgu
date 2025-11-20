from dash import html, dcc

def layout_predicao():
    return html.Div(
        className="container-principal",
        children=[
            html.H2(
                "Predição – Modelos de Machine Learning",
                style={"textAlign": "center", "marginBottom": "30px"},
            ),

            html.Div(
                className="card",
                children=[
                    html.H3("Selecione os Parâmetros da Manifestação"),
                    html.Label("Tipo de Manifestação"),
                    dcc.Dropdown(id="pred-tipo", options=[], clearable=False),

                    html.Label("UF do Manifestante"),
                    dcc.Dropdown(id="pred-uf", options=[], clearable=False),

                    html.Label("Tempo de Resposta Estimado"),
                    dcc.Input(id="pred-tempo", type="number", min=0),

                    html.Br(), html.Br(),
                    html.Button("Prever Satisfação", id="btn-prever", n_clicks=0),
                ],
            ),

            html.Div(
                className="card",
                children=[
                    html.H3("Resultado da Predição"),
                    html.Div(id="pred-resultado", className="resultado-predicao"),
                ],
            ),
        ],
    )
