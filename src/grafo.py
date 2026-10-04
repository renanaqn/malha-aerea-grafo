"""Módulo para construção e manipulação da rede de aeroportos a partir da VRA/ANAC."""

from pathlib import Path
import pandas as pd
import networkx as nx

COLUNAS_VRA = {
    "empresa": "Sigla ICAO Empresa Aérea",
    "origem": "Sigla ICAO Aeroporto Origem",
    "destino": "Sigla ICAO Aeroporto Destino",
    "tipo_linha": "Código Tipo Linha",
    "situacao": "Situação Voo",
}

def carregar_grafo_vra(
    caminho_csv: Path,
    limiar_frequencia: int = 4,
    somente_nacional: bool = True,
    somente_realizados: bool = True,
) -> nx.DiGraph:
    """Carrega o CSV da VRA e retorna um DiGraph do NetworkX.

    Arestas possuem atributo 'weight' correspondendo à frequência mensal de voos.
    """
    df = pd.read_csv(caminho_csv, sep=";", encoding="utf-8", low_memory=False)

    # 1. Filtros de Escopo
    if somente_realizados:
        df = df[df[COLUNAS_VRA["situacao"]].str.upper() == "REALIZADO"]

    if somente_nacional:
        # 'N' = Nacional Regular
        df = df[df[COLUNAS_VRA["tipo_linha"]] == "N"]

    col_origem = COLUNAS_VRA["origem"]
    col_destino = COLUNAS_VRA["destino"]

    # Remover linhas com ICAO inválido ou ausente
    df = df.dropna(subset=[col_origem, col_destino])

    # 2. Agrupamento para Arestas Ponderadas
    df_rotas = (
        df.groupby([col_origem, col_destino])
        .size()
        .reset_index(name="weight")
    )

    # Filtrar rotas esporádicas abaixo do limiar
    df_rotas = df_rotas[df_rotas["weight"] >= limiar_frequencia]

    # 3. Construção do Grafo Dirigido
    G = nx.DiGraph()
    for _, row in df_rotas.iterrows():
        G.add_edge(row[col_origem], row[col_destino], weight=int(row["weight"]))

    return G

if __name__ == "__main__":
    # Caminho para o arquivo de teste (Abril/2024)
    caminho_dados = Path("data/raw/VRA_2024_04.csv")
    
    if not caminho_dados.exists():
        print(f"Arquivo {caminho_dados} não encontrado! Execute primeiro o script scripts/baixar_dados.py")
    else:
        print("Carregando o grafo a partir dos dados da VRA...")
        G = carregar_grafo_vra(caminho_dados, limiar_frequencia=4)
        
        print("\n--- GRAFO GERADO COM SUCESSO ---")
        print(f"Total de Aeroportos (Nós): {G.number_of_nodes()}")
        print(f"Total de Rotas (Arestas): {G.number_of_edges()}")
        
        # Exibir alguns nós e seus graus
        print("\nExemplo dos 5 aeroportos mais conectados (Grau total):")
        graus = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:5]
        for aeroporto, grau in graus:
            print(f" - {aeroporto}: {grau} rotas")