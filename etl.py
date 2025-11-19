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
COLUNAS_TEXTO = [
    'faixa etária', 'raça/cor', 'gênero', 'município manifestante', 
    'uf do município manifestante', 'município manifestação', 
    'uf do município manifestação', 'tipo manifestação', 'nome Órgão', 
    'município do Órgão', 'uf do Órgão', 'assunto', 'formulário', 
    'situação', 'esfera', 'serviço', 'outro serviço', 
    'demanda atendida', 'satisfação'
]

COLUNAS_NUM = ['dias para resolução', 'dias de atraso']

# Mapa para forçar leitura como string
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

    # Garante que o ano é numérico
    df['ano_registro'] = pd.to_numeric(df['ano_registro'], errors='coerce').fillna(0).astype(int)
    
    return df

# --- Função Principal do ETL ---
def executar_etl():
    ARQUIVO_PARQUET_FINAL = 'ouvidoria.parquet'
    
    caminho_arquivos = sorted(glob.glob('src/dados/*.csv'))
    
    if not caminho_arquivos:
        print("ERRO: Nenhum arquivo CSV encontrado em 'src/dados/'")
        return

    print(f"Iniciando ETL para {len(caminho_arquivos)} arquivos CSV...")

    if os.path.exists(ARQUIVO_PARQUET_FINAL):
        try:
            os.remove(ARQUIVO_PARQUET_FINAL)
            print(f"Arquivo '{ARQUIVO_PARQUET_FINAL}' antigo removido.")
        except PermissionError:
            print(f"AVISO: Não foi possível remover '{ARQUIVO_PARQUET_FINAL}'. Verifique se ele está aberto.")

    # --- NOVA ESTRATÉGIA: Lista para acumular os DataFrames ---
    lista_dfs_processados = []

    for i, arquivo_csv in enumerate(caminho_arquivos):
        print(f"Processando arquivo {i+1}/{len(caminho_arquivos)}: {arquivo_csv}")
        
        try:
            df_temp = pd.read_csv(
                arquivo_csv, 
                sep=';', 
                low_memory=False, 
                dtype=DTYPE_MAP
            )
        except UnicodeDecodeError:
            df_temp = pd.read_csv(
                arquivo_csv, 
                sep=';', 
                encoding='latin-1', 
                low_memory=False, 
                dtype=DTYPE_MAP
            )
        except Exception as e:
            print(f"  ERRO ao ler {arquivo_csv}: {e}")
            continue 

        # Limpa o DataFrame
        df_limpo = limpar_dataframe(df_temp)

        # Correção final de tipos
        for col in df_limpo.columns:
            if df_limpo[col].dtype == "Int64":
                df_limpo[col] = df_limpo[col].fillna(0).astype("int64")
            elif df_limpo[col].dtype == "boolean":
                df_limpo[col] = df_limpo[col].fillna(False).astype(bool)
        
        if df_limpo.empty:
            print(f"  AVISO: Arquivo {arquivo_csv} vazio após limpeza.")
            continue
            
        # --- ADICIONA NA LISTA EM VEZ DE SALVAR ---
        lista_dfs_processados.append(df_limpo)

    # --- ETAPA FINAL: CONCATENA E SALVA DE UMA VEZ ---
    if not lista_dfs_processados:
        print("\nERRO: Nenhum dado foi processado com sucesso. Verifique seus arquivos CSV.")
        return

    print("\nConcatenando todos os dados (isso pode levar alguns segundos)...")
    try:
        # Junta todos os pedaços em um único DataFrame Gigante
        df_final = pd.concat(lista_dfs_processados, ignore_index=True)
        
        print(f"Salvando arquivo final '{ARQUIVO_PARQUET_FINAL}' com {len(df_final)} linhas...")
        # Salva de uma vez só (sem append, evitando o erro)
        df_final.to_parquet(ARQUIVO_PARQUET_FINAL, engine='pyarrow')
        
        print(f"ETL Concluído com SUCESSO! Dados salvos em '{ARQUIVO_PARQUET_FINAL}'.")
        
    except Exception as e:
        print(f"ERRO FATAL ao salvar o arquivo final: {e}")

# --- Roda o script ---
if __name__ == '__main__':
    executar_etl()