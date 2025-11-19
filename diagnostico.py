# diagnostico.py
import pandas as pd
import sys

ARQUIVO_PARQUET = "ouvidoria.parquet"

print(f"Carregando {ARQUIVO_PARQUET} para diagnóstico...")
try:
    df = pd.read_parquet(
        ARQUIVO_PARQUET, 
        # Carrega só as colunas que precisamos
        columns=['satisfacao', 'dias_de_atraso'], 
        engine="pyarrow"
    )
    print("Arquivo carregado com sucesso.\n")
    
    print("--- 1. Análise da Coluna 'satisfacao' ---")
    print("Valores mais comuns (Top 10):")
    print(df['satisfacao'].value_counts(dropna=False).head(10))
    
    print("\n--- 2. Análise da Coluna 'dias_de_atraso' ---")
    # Seu etl.py já converte 'dias_de_atraso' para numérico
    print(f"Total de linhas: {len(df)}")
    
    # Verifica se a coluna é numérica
    if pd.api.types.is_numeric_dtype(df['dias_de_atraso']):
        print(f"Linhas com atraso (dias_de_atraso > 0): { (df['dias_de_atraso'] > 0).sum() }")
        print(f"Média de dias de atraso: { df[df['dias_de_atraso'] > 0]['dias_de_atraso'].mean():.2f } dias")
        print(f"Atraso máximo: { df['dias_de_atraso'].max() } dias")
    else:
        print("AVISO: A coluna 'dias_de_atraso' não é numérica. Verifique o etl.py.")
        print(df['dias_de_atraso'].value_counts(dropna=False).head(10))

except Exception as e:
    print(f"Erro ao ler o arquivo: {e}")
    sys.exit(1)