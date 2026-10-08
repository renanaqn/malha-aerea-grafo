"""Construção da rede de aeroportos a partir da base VRA da ANAC.

As escolhas de filtros, janelas e limiar estão justificadas em docs/modelagem.md.
"""

import math
from pathlib import Path

import networkx as nx
import pandas as pd

COLUNAS_VRA = {
    "origem": "Sigla ICAO Aeroporto Origem",
    "destino": "Sigla ICAO Aeroporto Destino",
    "nome_origem": "Descrição Aeroporto Origem",
    "nome_destino": "Descrição Aeroporto Destino",
    "tipo_linha": "Código Tipo Linha",
    "di": "Código DI",
    "situacao": "Situação Voo",
    "partida_real": "Partida Real",
}

# N = Doméstica Mista (passageiros ou mista), segundo o dicionário da ANAC
TIPO_LINHA_DOMESTICA = "N"
# grupo "Regular" do dicionário da ANAC
DI_REGULAR = {"0", "4", "C"}

# (início, fim), datas inclusivas, pela data da partida real
JANELAS = {
    "referencia": ("2024-04-01", "2024-04-30"),
    "pos_fechamento": ("2024-05-04", "2024-06-30"),
}


def ler_voos_vra(caminhos: list[Path]) -> pd.DataFrame:
    """Lê um ou mais CSVs da VRA e devolve só os voos domésticos regulares realizados.

    Colunas do resultado: origem, destino, nome_origem, nome_destino, partida (datetime).
    """
    usar = list(COLUNAS_VRA.values())
    df = pd.concat(
        [pd.read_csv(c, sep=";", encoding="utf-8", usecols=usar, dtype=str) for c in caminhos],
        ignore_index=True,
    )
    df = df.rename(columns={v: k for k, v in COLUNAS_VRA.items()})

    df = df[
        (df["situacao"].str.upper() == "REALIZADO")
        & (df["tipo_linha"] == TIPO_LINHA_DOMESTICA)
        & (df["di"].isin(DI_REGULAR))
    ]
    df = df.dropna(subset=["origem", "destino", "partida_real"])
    df["partida"] = pd.to_datetime(df["partida_real"], format="%d/%m/%Y %H:%M")

    return df[["origem", "destino", "nome_origem", "nome_destino", "partida"]].reset_index(drop=True)


def recortar_janela(voos: pd.DataFrame, inicio: str, fim: str) -> pd.DataFrame:
    """Voos com partida entre as datas inicio e fim, inclusive."""
    inicio_ts = pd.Timestamp(inicio)
    fim_ts = pd.Timestamp(fim) + pd.Timedelta(days=1)
    return voos[(voos["partida"] >= inicio_ts) & (voos["partida"] < fim_ts)]


def construir_grafo(
    voos: pd.DataFrame,
    inicio: str,
    fim: str,
    limiar_semanal: float = 1.0,
) -> nx.DiGraph:
    """Monta o grafo dirigido de rotas na janela [inicio, fim].

    Atributos das arestas:
        voos: total de voos na janela
        weight: frequência média em voos por semana (força da ligação, não distância)
    Atributo dos nós:
        nome: descrição do aeroporto na VRA
    Rotas com menos de `limiar_semanal` voos por semana ficam de fora. O corte é
    feito em piso(limiar_semanal * semanas) voos na janela, que é o mínimo que uma
    rota com essa frequência sempre tem: um voo semanal acontece 4 ou 5 vezes em
    abril (4,3 semanas), conforme o dia da semana.
    """
    janela = recortar_janela(voos, inicio, fim)
    semanas = ((pd.Timestamp(fim) - pd.Timestamp(inicio)).days + 1) / 7

    rotas = janela.groupby(["origem", "destino"]).size().reset_index(name="voos")
    rotas["weight"] = rotas["voos"] / semanas
    rotas = rotas[rotas["voos"] >= math.floor(limiar_semanal * semanas)]

    G = nx.from_pandas_edgelist(
        rotas, source="origem", target="destino", edge_attr=["voos", "weight"], create_using=nx.DiGraph
    )

    nomes = dict(zip(janela["origem"], janela["nome_origem"]))
    nomes.update(zip(janela["destino"], janela["nome_destino"]))
    nx.set_node_attributes(G, {n: nomes.get(n, "") for n in G}, "nome")
    G.graph.update(inicio=inicio, fim=fim, limiar_semanal=limiar_semanal)
    return G


def arestas_para_df(G: nx.DiGraph) -> pd.DataFrame:
    """Tabela de arestas com origem, destino, voos e weight, ordenada por peso."""
    df = nx.to_pandas_edgelist(G, source="origem", target="destino")
    return df[["origem", "destino", "voos", "weight"]].sort_values("weight", ascending=False, ignore_index=True)


def carregar_grafo(caminho: Path) -> nx.DiGraph:
    """Carrega um grafo salvo em GraphML por scripts/construir_rede.py."""
    return nx.read_graphml(caminho)
