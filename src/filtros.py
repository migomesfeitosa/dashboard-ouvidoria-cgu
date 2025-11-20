# ARQUIVO: src/filtros.py

from dash import html, dcc
from src.utils import carregar_opcoes_filtros

# Carrega opções de dropdowns via utils.py
opcoes = carregar_opcoes_filtros()

def criar_filtros():
    """
    Retorna o container HTML completo dos filtros (Ano, UF, Tipo),
    com IDs que já são reconhecidos pelos callbacks.
    """
    return html.Div(
        id="container-filtros",
        # Inicia invisível se quiser, ou visível. O callback de toggle controla isso.
        style={"display": "none", "marginBottom": "20px"},
        children=[
            html.Div(
                className="filtro-card",
                children=[

                    # 1. Filtro de ANO
                    html.Div(
                        className="filtro-item",
                        children=[
                            html.Label("Ano"),
                            dcc.Dropdown(
                                id="filtro-ano",
                                options=opcoes["anos"],
                                multi=True,
                                placeholder="Selecione o(s) ano(s)",
                                value=opcoes["anos_lista"][:1],  # Padrão: primeiro ano
                            ),
                        ],
                    ),

                    # 2. Filtro de UF
                    html.Div(
                        className="filtro-item",
                        children=[
                            html.Label("UF"),
                            dcc.Dropdown(
                                id="filtro-uf",
                                options=opcoes["ufs"],
                                multi=True,
                                placeholder="Selecione UF(s)",
                                value=opcoes["ufs_lista"][:1],  # Padrão: primeiro estado
                            ),
                        ],
                    ),

                    # 3. Filtro de TIPO (Dropdown + Botão Limpar)
                    html.Div(
                        className="filtro-item",
                        children=[
                            html.Label("Tipo de Manifestação"),
                            dcc.Dropdown(
                                id="filtro-tipo",
                                options=opcoes["tipos_ml"],
                                placeholder="Filtrar por tipo",
                                multi=False,
                                clearable=True,
                            ),
                            # Botão para limpar o tipo (visual)
                            html.Button(
                                "Limpar Tipo Selecionado",
                                id="botao-limpar-tipo",
                                n_clicks=0,
                                style={
                                    "marginTop": "5px",
                                    "backgroundColor": "#e74c3c",
                                    "color": "white",
                                    "border": "none",
                                    "padding": "5px 10px",
                                    "borderRadius": "5px",
                                    "cursor": "pointer",
                                    "fontSize": "0.8em"
                                },
                            ),
                        ],
                    ),
                ],
            ),

            # MEMÓRIA DO TIPO SELECIONADO (Store para cross-filtering)
            dcc.Store(id="memoria-filtro-tipo", data=None),
        ],
    )

def botao_toggle_filtros():
    """
    Botão azul que aparece no topo para Mostrar/Ocultar os filtros.
    """
    return html.Button(
        "Mostrar/Ocultar Filtros",
        id="botao-toggle-filtros",
        n_clicks=0,
        style={
            "marginBottom": "10px",
            "backgroundColor": "#3498db",
            "color": "white",
            "padding": "8px 16px",
            "borderRadius": "6px",
            "border": "none",
            "cursor": "pointer",
        },
    )