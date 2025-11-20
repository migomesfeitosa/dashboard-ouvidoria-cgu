from dash import html, dash_table

def layout_amostra_dados():
    return html.Div(
        className="container-principal",
        children=[
            html.H2("Amostra dos Dados Originais"),

            html.Div(
                className="card-grafico",
                children=[
                    dash_table.DataTable(
                        id="tabela-amostra",
                        page_size=10,
                        style_table={"overflowX": "auto"},
                    )
                ],
            ),
        ],
    )
