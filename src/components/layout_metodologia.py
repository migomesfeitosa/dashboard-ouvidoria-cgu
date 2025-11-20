from dash import html

def layout_metodologia():
    return html.Div(
        className="container-principal",
        children=[
            html.H2("Metodologia da Análise e Transformação de Dados"),

            html.Div(
                className="card-texto",
                children=[
                    html.P("""
                        Esta aba descreve como os dados são tratados, limpos,
                        transformados e analisados. Também detalha os indicadores,
                        técnicas estatísticas e métodos de machine learning utilizados.
                    """),
                ],
            ),
        ],
    )
