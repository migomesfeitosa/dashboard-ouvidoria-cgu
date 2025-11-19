<img width="1915" height="877" alt="image" src="https://github.com/user-attachments/assets/b3337489-ad19-471f-9d14-feebcebeb16b" />
<img width="1902" height="882" alt="image" src="https://github.com/user-attachments/assets/bbb3a463-a59b-4988-86a0-e35c7729f816" />


eda_ouvidoria.py (Com melhorias visuais)
import pandas as pd import plotly.express as px

ARQUIVO_PARQUET = "ouvidoria.parquet" TEMA_GRAFICOS = "plotly_white" # <--- NOSSA CONSTANTE DE TEMA

============================================================
Função base: carregar dados (Sem mudanças)
============================================================
def carregar_dados(): """Carrega todos os dados do Parquet.""" print("Carregando dados completos para a aba EDA...") try: df = pd.read_parquet(ARQUIVO_PARQUET, engine="pyarrow") print(f"Dados carregados com sucesso: {len(df)} linhas.") return df except Exception as e: print(f"ERRO ao carregar dados: {e}") return pd.DataFrame()

============================================================
Gráficos (COM MELHORIAS)
============================================================
def grafico_volume_tempo(df): if not pd.api.types.is_datetime64_any_dtype(df['data_registro']): df["data_registro"] = pd.to_datetime(df["data_registro"])

df["mes"] = df["data_registro"].dt.month
volume_tempo = df.groupby(["ano_registro", "mes"]).size().reset_index(name="total")
fig = px.line(
    volume_tempo,
    x="mes",
    y="total",
    color="ano_registro",
    title="Evolução Mensal das Manifestações",
    template=TEMA_GRAFICOS # <--- APLICA O TEMA
)
fig.update_layout(title_x=0.5) # Centraliza o título
return fig
def grafico_genero(df): # --- MELHORIA: Trocado de Pizza (Pie) para Barras Horizontais --- df_genero = df['genero'].value_counts().reset_index(name="Total")

fig = px.bar(
    df_genero.sort_values(by="Total", ascending=True), # Ordena
    x="Total",
    y="genero",
    orientation='h',
    title="Distribuição por Gênero",
    template=TEMA_GRAFICOS, # <--- APLICA O TEMA
    text_auto=True # <--- ADICIONA RÓTULOS
)
# Limpa os eixos para um visual mais clean
fig.update_layout(yaxis_title=None, xaxis_title=None, title_x=0.5)
return fig
def grafico_faixa_etaria(df): df_faixa = df["faixa_etaria"].value_counts().reset_index() df_faixa.columns = ["faixa_etaria", "count"] fig = px.bar( df_faixa, x="faixa_etaria", y="count", title="Distribuição por Faixa Etária", text_auto=True, template=TEMA_GRAFICOS # <--- APLICA O TEMA ) fig.update_layout(title_x=0.5, xaxis_title=None) return fig

def grafico_raca(df): raca_counts = df["raca_cor"].value_counts().reset_index() raca_counts.columns = ["raca_cor", "contagem"] fig = px.bar( raca_counts, x="raca_cor", y="contagem", title="Distribuição por Raça/Cor", template=TEMA_GRAFICOS, # <--- APLICA O TEMA text_auto=True # <--- ADICIONA RÓTULOS ) fig.update_layout(title_x=0.5, xaxis_title=None) return fig

def grafico_tipos(df): tipo_counts = df["tipo_manifestacao"].value_counts().head(10).reset_index() tipo_counts.columns = ["tipo_manifestacao", "contagem"] fig = px.bar( tipo_counts, x="tipo_manifestacao", y="contagem", title="Top 10 Tipos de Manifestação", template=TEMA_GRAFICOS, # <--- APLICA O TEMA text_auto=True # <--- ADICIONA RÓTULOS ) fig.update_layout(title_x=0.5, xaxis_title=None) return fig

def grafico_satisfacao(df): # CORREÇÃO: Converte 'satisfacao' para numérico para o boxplot df["satisfacao_num"] = pd.to_numeric(df["satisfacao"], errors='coerce') df["em_atraso"] = pd.to_numeric(df["dias_de_atraso"], errors='coerce').fillna(0) > 0

fig = px.box(
    df.dropna(subset=["satisfacao_num"]), # Usa a coluna numérica
    x="em_atraso",
    y="satisfacao_num", # Usa a coluna numérica
    title="Distribuição da Satisfação por Atraso na Resposta",
    labels={"em_atraso": "Em Atraso?", "satisfacao_num": "Nível de Satisfação"},
    template=TEMA_GRAFICOS # <--- APLICA O TEMA
)
fig.update_layout(title_x=0.5)
return fig
def grafico_mapa(df): uf_counts = df["uf_do_municipio_manifestante"].value_counts().head(30).reset_index() uf_counts.columns = ["UF", "Total"]

fig = px.bar(
    uf_counts.sort_values(by="Total", ascending=True), 
    x="Total",
    y="UF",
    orientation='h',
    title="Top 30 Manifestações por UF",
    labels={"UF": "UF do Manifestante", "Total": "Quantidade"},
    text_auto=True,
    template=TEMA_GRAFICOS # <--- APLICA O TEMA
)
fig.update_layout(yaxis_title=None, xaxis_title=None, title_x=0.5)
return fig
Fragmento do código

import pandas as pd
import glob
import re
from unidecode import unidecode
import os

# --- Helper: Função para limpar nomes de colunas ---
def snake_case_nome(nome_coluna):
    """Converte um nome de coluna para snake_case (ex: 'Raça/Cor' -> 'raca_cor')"""
    nome_coluna = unidecode(nome_coluna)
    nome_coluna = nome_coluna.lower()
    nome_coluna = re.sub(r'[^a-z0-9_]+', '_', nome_coluna)
    nome_coluna = nome_coluna.strip('_')
    return nome_coluna

# --- CONSTANTES GLOBAIS PARA O ETL ---
# Definimos todas as colunas que SÃO texto, para forçar o Pandas a lê-las como string
COLUNAS_TEXTO = [
    'faixa etária', 'raça/cor', 'gênero', 'município manifestante', 
    'uf do município manifestante', 'município manifestação', 
    'uf do município manifestação', 'tipo manifestação', 'nome Órgão', 
    'município do Órgão', 'uf do Órgão', 'assunto', 'formulário', 
    'situação', 'esfera', 'serviço', 'outro serviço', 
    'demanda atendida', 'satisfação'
]

# (Opcional, mas boa prática) Definimos as colunas que SÃO número
COLUNAS_NUM = ['dias para resolução', 'dias de atraso']

# --- A CORREÇÃO: Criamos um mapa de 'dtype' ---
# Isso força o Pandas a ler todas as colunas de texto como 'str' (string)
DTYPE_MAP = {col: str for col in COLUNAS_TEXTO}

# --- Helper: Função para limpar o DataFrame ---
def limpar_dataframe(df):
    # 1. Normaliza nomes das colunas
    df.columns = [snake_case_nome(col) for col in df.columns]

    # Pega os nomes de colunas já em "snake_case"
    colunas_texto_limpas = [snake_case_nome(c) for c in COLUNAS_TEXTO]
    colunas_num_limpas = [snake_case_nome(c) for c in COLUNAS_NUM]

    # 2. Normaliza colunas de texto
    for col in colunas_texto_limpas:
        if col in df.columns:
            # A coluna já foi lida como 'str' (graças ao DTYPE_MAP),
            # então não precisamos mais do .astype(str)
            df[col] = df[col].str.lower().str.strip()
            df[col] = df[col].replace(['nan', '', None], 'não informado')

    # 3. Normaliza colunas numéricas
    for col in colunas_num_limpas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(0)

    # 4. Normaliza datas e cria 'ano_registro'
    colunas_data = ['data_registro', 'data_prazo_resposta', 'data_resposta']
    for col in colunas_data:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)

    if 'data_registro' in df.columns:
        df['ano_registro'] = df['data_registro'].dt.year

    # Remove linhas sem data de registro
    df.dropna(subset=['data_registro'], inplace=True)

    # Garante que o ano é numérico e substitui NA por 0
    df['ano_registro'] = pd.to_numeric(df['ano_registro'], errors='coerce').fillna(0).astype(int)

    
    return df

# --- Função Principal do ETL ---
def executar_etl():
    ARQUIVO_PARQUET_FINAL = 'ouvidoria.parquet'
    
    # IMPORTANTE: O caminho 'src/dados/' deve existir
    caminho_dados_csv = 'src/dados/'
    caminho_arquivos = sorted(glob.glob(os.path.join(caminho_dados_csv, '*.csv')))
    
    if not os.path.exists(caminho_dados_csv):
        os.makedirs(caminho_dados_csv)
        print(f"Pasta '{caminho_dados_csv}' criada. Por favor, adicione seus arquivos .csv lá.")
        return

    if not caminho_arquivos:
        print(f"ERRO: Nenhum arquivo CSV encontrado em '{caminho_dados_csv}'")
        print("Por favor, coloque seus arquivos CSV de origem nesta pasta e rode o ETL novamente.")
        return

    print(f"Iniciando ETL para {len(caminho_arquivos)} arquivos CSV...")

    if os.path.exists(ARQUIVO_PARQUET_FINAL):
        os.remove(ARQUIVO_PARQUET_FINAL)
        print(f"Arquivo '{ARQUIVO_PARQUET_FINAL}' antigo removido.")

    # Loop principal: 1 arquivo de cada vez
    for i, arquivo_csv in enumerate(caminho_arquivos):
        print(f"Processando arquivo {i+1}/{len(caminho_arquivos)}: {arquivo_csv}")
        
        # 1. Carrega 1 CSV
        try:
            # --- MUDANÇA AQUI ---
            df_temp = pd.read_csv(
                arquivo_csv, 
                sep=';', 
                low_memory=False, 
                dtype=DTYPE_MAP # Força o tipo string na leitura
            )
        except UnicodeDecodeError:
            # --- MUDANÇA AQUI ---
            df_temp = pd.read_csv(
                arquivo_csv, 
                sep=';', 
                encoding='latin-1', 
                low_memory=False, 
                dtype=DTYPE_MAP # Força o tipo string na leitura
            )
        except Exception as e:
            print(f"  ERRO ao ler {arquivo_csv}: {e}")
            continue 

        # 2. Limpa o DataFrame
        df_limpo = limpar_dataframe(df_temp)

        # --- Correção final: força tipos compatíveis com Parquet ---
        for col in df_limpo.columns:
            if df_limpo[col].dtype == "Int64":  # tipo inteiro com suporte a NA (pandas)
                df_limpo[col] = df_limpo[col].fillna(0).astype("int64")
            elif df_limpo[col].dtype == "boolean":
                df_limpo[col] = df_limpo[col].fillna(False).astype(bool)

        
        # 3. Salva/Anexa no Parquet
        if df_limpo.empty:
            print(f"  AVISO: Nenhum dado válido encontrado em {arquivo_csv}.")
            continue
            
        try:
            # Usando 'pyarrow'
            if i == 0:
                # Cria o arquivo na primeira vez
                df_limpo.to_parquet(ARQUIVO_PARQUET_FINAL, engine='pyarrow')
            else:
                # Anexa nas seguintes
                df_limpo.to_parquet(ARQUIVO_PARQUET_FINAL, engine='pyarrow', append=True)
        except Exception as e:
             print(f"  ERRO FATAL ao salvar Parquet: {e}")
             break # Para o loop se o salvamento falhar

    print(f"\nETL Concluído! Dados salvos em '{ARQUIVO_PARQUET_FINAL}'.")

# --- Roda o script ---
if __name__ == '__main__':
    executar_etl()
```markdown:README:README.md
# Dashboard de Análise de Ouvidoria

Este projeto é um dashboard web interativo para a análise de dados de manifestações de ouvidoria, construído com Plotly e Dash em Python.

O aplicativo permite filtrar dados por ano e UF, apresentando KPIs globais, tendências temporais, rankings de órgãos demandados e análises demográficas (gênero, raça, faixa etária) e de satisfação.

## Funcionalidades

* **KPIs Globais:** Total de manifestações, % de respostas em atraso e satisfação média.
* **Navegação Multi-Página:** Uma interface limpa que separa o Dashboard principal, a Análise Exploratória (EDA), a Metodologia e a Amostra de Dados.
* **Filtragem Dinâmica:** Filtre todo o dashboard por Ano e UF.
* **Cross-filtering:** Clique em um tipo de manifestação no gráfico de barras para filtrar todo o dashboard por esse tipo.
* **Layout Otimizado:** O layout usa "cards" com altura fixa para evitar scroll infinito e manter a informação organizada.
* **Performance:** Os dados são lidos de um arquivo Parquet otimizado, usando filtros `pyarrow` para carregar apenas os dados necessários para os gráficos.

## Estrutura do Projeto

/
├── app.py                 # O aplicativo Dash principal (layouts e callbacks)
├── etl.py                 # Script para processar CSVs e criar o .parquet
├── eda_ouvidoria.py       # Módulo com as funções que geram os gráficos
├── assets/
│   └── style.css          # CSS para os cards de KPI
├── src/
│   └── dados/
│       └── (coloque seus .csv de origem aqui)
├── requirements.txt       # As dependências do Python
├── .gitignore             # Arquivos a serem ignorados pelo Git
└── ouvidoria.parquet      # Arquivo de dados final (GERADO PELO ETL)
