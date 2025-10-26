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
    
    # Remove linhas onde a data de registro falhou
    df.dropna(subset=['data_registro', 'ano_registro'], inplace=True)
    df['ano_registro'] = df['ano_registro'].astype(int)

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
        
        # 3. Salva/Anexa no Parquet
        if df_limpo.empty:
            print(f"  AVISO: Nenhum dado válido encontrado em {arquivo_csv}.")
            continue
            
        try:
            # Usando 'fastparquet'
            if i == 0:
                # Cria o arquivo na primeira vez
                df_limpo.to_parquet(ARQUIVO_PARQUET_FINAL, engine='fastparquet')
            else:
                # Anexa nas vezes seguintes
                df_limpo.to_parquet(ARQUIVO_PARQUET_FINAL, engine='fastparquet', append=True)
        except Exception as e:
             print(f"  ERRO FATAL ao salvar Parquet: {e}")
             break # Para o loop se o salvamento falhar

    print(f"\nETL Concluído! Dados salvos em '{ARQUIVO_PARQUET_FINAL}'.")

# --- Roda o script ---
if __name__ == '__main__':
    executar_etl()