"""Métricas descritivas e de centralidade da rede de aeroportos."""

import networkx as nx
import numpy as np
import pandas as pd


def resumo_rede(G: nx.DiGraph) -> dict:
    """Medidas globais de um grafo dirigido.

    Caminhos (diâmetro e distância média) são calculados sem peso, em número de
    voos, dentro da maior componente fortemente conexa.
    """
    graus = np.array([g for _, g in G.degree()])
    sccs = sorted(nx.strongly_connected_components(G), key=len, reverse=True)
    maior_scc = G.subgraph(sccs[0])
    com_volta = sum(1 for u, v in G.edges if G.has_edge(v, u))

    return {
        "nós": G.number_of_nodes(),
        "arestas": G.number_of_edges(),
        "densidade": nx.density(G),
        "grau médio": graus.mean(),
        "grau mediano": np.median(graus),
        "grau máximo": graus.max(),
        "rotas com volta (%)": 100 * com_volta / G.number_of_edges(),
        "WCC": nx.number_weakly_connected_components(G),
        "SCC": len(sccs),
        "maior SCC": len(sccs[0]),
        "diâmetro (maior SCC)": nx.diameter(maior_scc),
        "distância média (maior SCC)": nx.average_shortest_path_length(maior_scc),
        "clustering médio": nx.average_clustering(G.to_undirected()),
    }


def tabela_graus(G: nx.DiGraph) -> pd.DataFrame:
    """Grau de entrada, de saída e total por aeroporto, do maior para o menor."""
    df = pd.DataFrame(
        {
            "grau entrada": dict(G.in_degree()),
            "grau saída": dict(G.out_degree()),
            "grau total": dict(G.degree()),
        }
    )
    return df.sort_values("grau total", ascending=False)
