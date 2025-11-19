import pandas as pd
import joblib
import re 
import time # Para medir o tempo
import sys

# Tentar importar scikit-learn; se não estiver disponível, mostrar instrução clara.
try:
    from sklearn.model_selection import train_test_split
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
except Exception as e:
    print("ERRO: scikit-learn não pode ser importado. Instale ou atualize com: pip install -U scikit-learn")
    raise

import warnings

#warnings.filterwarnings('ignore', category=FutureWarning)

# --- Constantes ---
ARQUIVO_PARQUET = "ouvidoria.parquet"
MODELO_SALVO = "modelo_satisfacao.joblib"

def treinar_e_salvar_modelo():
    """
    Função completa (v3) com logs detalhados para
    diagnosticar lentidão.
    """
    start_total = time.time()
    print(f"Iniciando o processo de ML (v3 - com logs detalhados)...")
    
    # --- 1. Carga dos Dados ---
    print("\n--- Etapa 1: Carga dos Dados ---")
    start_load = time.time()
    try:
        #
        df = pd.read_parquet(ARQUIVO_PARQUET, engine="pyarrow")
        end_load = time.time()
        print(f"Dados carregados: {len(df)} linhas.")
        print(f"Tempo de Carga: {end_load - start_load:.2f} segundos.")
    except Exception as e:
        print(f"ERRO: Não foi possível ler '{ARQUIVO_PARQUET}'. {e}")
        return

    # --- 2. Preparação dos Dados (Feature Engineering) ---
    print("\n--- Etapa 2: Preparação dos Dados ---")
    start_prep = time.time()
    
    df_ml = df.copy()

    # 2a. Criar o Alvo (y)
    print("Passo 2a: Convertendo 'satisfacao' para string...")
    df_ml['satisfacao_texto'] = df_ml['satisfacao'].astype(str)
    
    print("Passo 2a: Extraindo número da 'satisfacao' (ex: '(1)')...")
    print("(ESTA PODE SER A ETAPA MAIS LENTA - 7.1M de linhas)")
    start_extract = time.time()
    # Formato é (1) muito insatisfeito
    df_ml['satisfacao_num'] = df_ml['satisfacao_texto'].str.extract(r'\((\d)\)')
    end_extract = time.time()
    print(f"Tempo de Extração: {end_extract - start_extract:.2f} segundos.")
    
    print("Passo 2a: Convertendo número extraído para numérico...")
    df_ml['satisfacao_num'] = pd.to_numeric(df_ml['satisfacao_num'], errors='coerce')
    
    print("Passo 2a: Removendo linhas Nulas (drop NA)...")
    df_ml.dropna(subset=['satisfacao_num'], inplace=True)
    
    print(f"Linhas restantes após dropna: {len(df_ml)}")
    
    print("Passo 2a: Criando coluna 'alvo' binária (0 ou 1)...")
    # 1 = Insatisfeito (1, 2) / 0 = Satisfeito (4, 5)
    df_ml['alvo'] = df_ml['satisfacao_num'].apply(lambda x: 1 if x <= 2 else (0 if x >= 4 else -1))
    
    print("Passo 2a: Filtrando apenas classes 0 e 1 (removendo nota 3)...")
    df_ml = df_ml[df_ml['alvo'].isin([0, 1])].copy()
    
    if df_ml.empty or len(df_ml['alvo'].unique()) < 2:
        print("ERRO: Dados insuficientes para treinar.")
        return
        
    print(f"Dados preparados para o alvo (y): {len(df_ml)} linhas úteis.")
    print("Distribuição das classes (Alvo):")
    print(df_ml['alvo'].value_counts(normalize=True))

    # 2b. Definir as Features (X)
    print("\nPasso 2b: Definindo e limpando Features (X)...")
    FEATURES_TEXTO = 'assunto'
    FEATURES_CATEGORICAS = [
        'tipo_manifestacao', 'nome_orgao', 'genero', 
        'faixa_etaria', 'raca_cor', 'uf_do_municipio_manifestante'
    ]
    
    for col in FEATURES_CATEGORICAS:
        if col in df_ml.columns:
            df_ml[col] = df_ml[col].astype(str).fillna('não informado')
        else:
            FEATURES_CATEGORICAS.remove(col)
            
    if FEATURES_TEXTO in df_ml.columns:
         df_ml[FEATURES_TEXTO] = df_ml[FEATURES_TEXTO].astype(str).fillna('sem assunto')
    else:
        print(f"ERRO: Coluna '{FEATURES_TEXTO}' não encontrada.")
        return

    X = df_ml[FEATURES_CATEGORICAS + [FEATURES_TEXTO]]
    y = df_ml['alvo']
    end_prep = time.time()
    print(f"Tempo total de Preparação: {end_prep - start_prep:.2f} segundos.")

    # --- 3. Criar o Pipeline de Pré-processamento e Modelo ---
    print("\n--- Etapa 3: Construindo o Pipeline de ML ---")
    
    preprocessor_texto = TfidfVectorizer(max_features=1000, stop_words=None, ngram_range=(1, 2))
    preprocessor_categorico = OneHotEncoder(handle_unknown='ignore', sparse_output=True)
    preprocessor_combinado = ColumnTransformer(
        transformers=[
            ('texto', preprocessor_texto, FEATURES_TEXTO),
            ('categorico', preprocessor_categorico, FEATURES_CATEGORICAS)
        ],
        remainder='drop' 
    )
    pipeline_completo = Pipeline(steps=[
        ('preprocessor', preprocessor_combinado),
        ('classifier', LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'))
    ])
    print("Pipeline construído.")

    # --- 4. Dividir os Dados (Treino e Teste) ---
    print("\n--- Etapa 4: Dividindo dados em Treino e Teste ---")
    start_split = time.time()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    end_split = time.time()
    print(f"Tamanho do Treino: {len(X_train)}, Tamanho do Teste: {len(X_test)}")
    print(f"Tempo de Divisão: {end_split - start_split:.2f} segundos.")

    # --- 5. Treinar o Modelo ---
    print("\n--- Etapa 5: Treinamento do Modelo ---")
    print("(Isso pode levar alguns minutos...)")
    start_fit = time.time()
    pipeline_completo.fit(X_train, y_train)
    end_fit = time.time()
    print(f"Modelo treinado com sucesso. Tempo de Treino: {end_fit - start_fit:.2f} segundos.")

    # --- 6. Avaliar o Modelo ---
    print("\n--- Etapa 6: Avaliação do Modelo ---")
    start_eval = time.time()
    y_pred = pipeline_completo.predict(X_test)
    end_eval = time.time()
    print(f"Tempo de Avaliação: {end_eval - start_eval:.2f} segundos.")
    
    print(f"Acurácia (Accuracy): {accuracy_score(y_test, y_pred):.4f}")
    print("\nMatriz de Confusão (Linhas=Real, Colunas=Previsto):")
    print(confusion_matrix(y_test, y_pred))
    print("\nRelatório de Classificação:")
    print(classification_report(y_test, y_pred, target_names=['Satisfeito (0)', 'Insatisfeito (1)']))

    # --- 7. Salvar o Modelo ---
    print(f"\n--- Etapa 7: Salvando o Modelo ---")
    start_save = time.time()
    try:
        joblib.dump(pipeline_completo, MODELO_SALVO)
        end_save = time.time()
        print(f"Sucesso! Modelo salvo como '{MODELO_SALVO}'.")
        print(f"Tempo de Salvamento: {end_save - start_save:.2f} segundos.")
    except Exception as e:
        print(f"ERRO ao salvar o modelo: {e}")
        
    end_total = time.time()
    print(f"\n--- Processo Concluído ---")
    print(f"Tempo Total de Execução: {(end_total - start_total) / 60:.2f} minutos.")


if __name__ == "__main__":
    treinar_e_salvar_modelo()