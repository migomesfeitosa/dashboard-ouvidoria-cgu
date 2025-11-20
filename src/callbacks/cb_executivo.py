# src/callbacks/cb_executivo.py
from dash import Input, Output
import plotly.express as px
import pandas as pd
from src.utils import ler_dados_filtrados, criar_grafico_responsivo, TEMA_GRAFICOS
from eda_ouvidoria import grafico_volume_tempo

def registrar_callbacks_executivo(app):
    
    # --- CALLBACK DOS KPIS (Mantido igual, apenas garantindo funcionamento) ---
    @app.callback(
        [
            Output("kpi-volume-total", "children"),
            Output("kpi-taxa-resolucao", "children"),
            Output("kpi-satisfacao-exec", "children"),
            Output("kpi-tempo-resposta", "children"),
        ],
        [
            Input("filtro-ano", "value"),
            Input("filtro-uf", "value"),
            Input("memoria-filtro-tipo", "data"),
        ],
    )
    def atualizar_kpis_executivo(anos, ufs, tipo):
        df = ler_dados_filtrados(anos, ufs, tipo)
        if df.empty:
            return "0", "0.0%", "N/A", "N/A"
            
        total = len(df)
        
        # Taxa de Resolução (Simulada baseada em situação ou atraso)
        if "situacao" in df.columns:
            resolvidas = df["situacao"].str.lower().isin(["concluída", "concluido", "atendida", "resolvida", "finalizada"]).sum()
            taxa = (resolvidas / total) * 100
        else:
            # Fallback: Se não tem coluna situação, considera resolvido quem não tem atraso
            em_atraso = pd.to_numeric(df.get("dias_de_atraso", 0), errors="coerce").fillna(0) > 0
            taxa = (1 - em_atraso.mean()) * 100

        # Satisfação Média
        s = df.copy()
        # Extrai o número se for string "(5) satisfeito" -> 5
        if s["satisfacao"].dtype == object:
            s["satisfacao_num"] = s["satisfacao"].astype(str).str.extract(r"\((\d)\)").astype(float)
        else:
            s["satisfacao_num"] = pd.to_numeric(s["satisfacao"], errors='coerce')
            
        mean_sat = s["satisfacao_num"].mean()
        str_sat = f"{mean_sat:.2f}" if pd.notnull(mean_sat) else "N/A"

        # Tempo Médio
        tempo = "N/A"
        if "dias_para_resolucao" in df.columns:
             media_dias = pd.to_numeric(df["dias_para_resolucao"], errors='coerce').mean()
             if pd.notnull(media_dias):
                 tempo = f"{media_dias:.1f} dias"
        
        return f"{total:,}", f"{taxa:.1f}%", str_sat, tempo


    # --- CALLBACK DOS GRÁFICOS (Atualizado para incluir os 4 gráficos) ---
    @app.callback(
        [
            Output("grafico-evolucao-mensal-exec", "figure"),
            Output("grafico-satisfacao-por-uf", "figure"),
            Output("grafico-top-orgaos-exec", "figure"),        # NOVO
            Output("grafico-eficiencia-atendimento", "figure")  # NOVO
        ],
        [
            Input("filtro-ano", "value"),
            Input("filtro-uf", "value")
        ]
    )
    def atualizar_graficos_executivo(anos, ufs):
        df = ler_dados_filtrados(anos, ufs, None)
        empty = criar_grafico_responsivo(px.bar(title="Sem dados", template=TEMA_GRAFICOS))
        
        if df.empty:
            return empty, empty, empty, empty

        try:
            # 1. Evolução Mensal
            fig_evolucao = grafico_volume_tempo(df.copy())

            # 2. Satisfação por UF
            df_sat = df.copy()
            if df_sat["satisfacao"].dtype == object:
                 df_sat["satisfacao_num"] = df_sat["satisfacao"].astype(str).str.extract(r"\((\d)\)").astype(float)
            else:
                 df_sat["satisfacao_num"] = pd.to_numeric(df_sat["satisfacao"], errors='coerce')
            
            sat_uf = df_sat.dropna(subset=["satisfacao_num"]).groupby("uf_do_municipio_manifestante")["satisfacao_num"].mean().reset_index()
            fig_sat_uf = px.bar(
                sat_uf.sort_values("satisfacao_num").tail(15),
                x="satisfacao_num", 
                y="uf_do_municipio_manifestante", 
                orientation="h",
                title="Satisfação Média por UF (Top 15)",
                template=TEMA_GRAFICOS
            )

            # 3. Top Órgãos (NOVO)
            top_orgaos = df["nome_orgao"].value_counts().head(10).reset_index(name="total")
            fig_orgaos = px.bar(
                top_orgaos.sort_values("total", ascending=True),
                x="total",
                y="nome_orgao",
                orientation="h",
                title="Top 10 Órgãos Mais Demandados",
                template=TEMA_GRAFICOS
            )

            # 4. Eficiência no Atendimento (NOVO - Pizza ou Barra)
            # Vamos ver proporção de atraso vs em dia
            df["status_prazo"] = pd.to_numeric(df.get("dias_de_atraso", 0), errors="coerce").fillna(0).apply(lambda x: "Em Atraso" if x > 0 else "No Prazo")
            status_counts = df["status_prazo"].value_counts().reset_index(name="total")
            fig_eficiencia = px.pie(
                status_counts,
                names="status_prazo",
                values="total",
                title="Status do Prazo de Resposta",
                template=TEMA_GRAFICOS,
                hole=0.4 # Donut chart
            )

            return (
                criar_grafico_responsivo(fig_evolucao),
                criar_grafico_responsivo(fig_sat_uf),
                criar_grafico_responsivo(fig_orgaos),
                criar_grafico_responsivo(fig_eficiencia)
            )

        except Exception as e:
            print("Erro atualizar_graficos_executivo:", e)
            return empty, empty, empty, empty