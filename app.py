import dash
from dash import html, dcc, Input, Output

# Importando os layouts
from src.components.layout_dashboard import layout_dashboard
from src.components.layout_executivo import layout_executivo
from src.components.layout_operacional import layout_operacional
from src.components.layout_eda import layout_eda
from src.components.layout_predicao import layout_predicao
from src.components.layout_perfil import layout_perfil_usuario
from src.components.layout_tematica import layout_analise_tematica

# Importando Filtros (ESSENCIAL PARA OS DADOS APARECEREM)
from src.filtros import criar_filtros, botao_toggle_filtros

# Importando Callbacks
from src.callbacks.cb_dashboard import registrar_callbacks_dashboard
from src.callbacks.cb_executivo import registrar_callbacks_executivo
from src.callbacks.cb_operacional import registrar_callbacks_operacional
from src.callbacks.cb_eda import registrar_callbacks_eda
from src.callbacks.cb_predicao import registrar_callbacks_predicao
from src.callbacks.cb_filtros import registrar_callbacks_filtros
from src.callbacks.cb_perfil import registrar_callbacks_perfil
from src.callbacks.cb_tematica import registrar_callbacks_tematica

# Inicializa o App
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# --- Layout Principal ---
app.layout = html.Div([
    # URL para controle de navegação
    dcc.Location(id="url", refresh=False),

    # 1. BARRA DE NAVEGAÇÃO (Estilizada com CSS)
    html.Div(className="navbar", children=[
        dcc.Link('Visão Geral', href='/', className='nav-link'),
        dcc.Link('Executivo', href='/executivo', className='nav-link'),
        dcc.Link('Operacional', href='/operacional', className='nav-link'),
        dcc.Link('Perfil Usuário', href='/perfil', className='nav-link'),
        dcc.Link('Temática', href='/tematica', className='nav-link'),
        dcc.Link('EDA (Exploratória)', href='/eda', className='nav-link'),
        dcc.Link('Predição ML', href='/predicao', className='nav-link'),
    ]),

    # 2. ÁREA DE CONTROLE (Botão + Filtros)
    html.Div(style={'padding': '0 20px'}, children=[
        botao_toggle_filtros(), # Botão azul
        criar_filtros()         # Os dropdowns (Isso fará os gráficos funcionarem!)
    ]),

    # 3. CONTEÚDO DA PÁGINA
    html.Div(id="page-content")
])

# --- Registrando Callbacks ---
registrar_callbacks_filtros(app)
registrar_callbacks_dashboard(app)
registrar_callbacks_executivo(app)
registrar_callbacks_operacional(app)
registrar_callbacks_eda(app)
registrar_callbacks_predicao(app)
registrar_callbacks_perfil(app)
registrar_callbacks_tematica(app)

# --- Callback de Roteamento (Navegação) ---
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/" or pathname is None:
        return layout_dashboard()
    elif pathname == "/executivo":
        return layout_executivo()
    elif pathname == "/operacional":
        return layout_operacional()
    elif pathname == "/perfil":
        return layout_perfil_usuario()
    elif pathname == "/tematica":
        return layout_analise_tematica()
    elif pathname == "/eda":
        return layout_eda()
    elif pathname == "/predicao":
        return layout_predicao()
    else:
        return layout_dashboard() # Fallback

if __name__ == "__main__":
    app.run(debug=True)