"""Construção da rede de aeroportos a partir da base VRA da ANAC."""

from pathlib import Path

import networkx as nx
import pandas as pd

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
        # 'N' = Nacional Regular (a confirmar no dicionário de dados da ANAC)
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
