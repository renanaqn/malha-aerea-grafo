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


def calcular_centralidades(G: nx.DiGraph) -> pd.DataFrame:
    """Calcula Betweenness, Closeness e Eigenvector (Semana 4).

    Usado para testar a H2: comparar aeroportos 'Hubs' (Grau) vs 'Pontes' (Betweenness).
    """
    # Betweenness não usa peso, pois queremos caminhos topológicos (voos/escalas)
    betweenness = nx.betweenness_centrality(G, weight=None)

    # Closeness e eigenvector no grafo não dirigido (95% das rotas têm volta).
    # No dirigido, a closeness do networkx mede a distância *até* o aeroporto, e
    # um aeroporto que só recebe voos (ex.: Iguatu) ficaria com valor alto.
    # O eigenvector dirigido também não é bem definido fora de uma única SCC.
    U = G.to_undirected()
    closeness = nx.closeness_centrality(U)
    eigenvector = nx.eigenvector_centrality(U, max_iter=1000)

    df = pd.DataFrame({
        "betweenness": betweenness,
        "closeness": closeness,
        "eigenvector": eigenvector
    })
    return df.sort_values(by="betweenness", ascending=False)


def analise_kcore(G: nx.DiGraph) -> pd.DataFrame:
    """Calcula o core number de cada aeroporto (Semana 5).

    O k-shell de um aeroporto é o seu core number: o k-shell k reúne os
    aeroportos com core number exatamente k.
    Responde à Subpergunta 1: Estrutura núcleo-periferia.
    """
    # k-core é tipicamente analisado no grafo subjacente não-dirigido
    U = G.to_undirected()
    
    # Remove auto-loops caso existam, pois o core_number não suporta
    U.remove_edges_from(nx.selfloop_edges(U))
    
    core_numbers = nx.core_number(U)
    
    df = pd.DataFrame.from_dict(core_numbers, orient='index', columns=['core_number'])
    return df.sort_values(by="core_number", ascending=False)


def escalas_bfs_origem(G: nx.DiGraph, origem: str) -> pd.DataFrame:
    """Usa BFS para achar a distância (escalas) de uma origem a todos os destinos (Semana 3).
    
    Responde à Subpergunta 5: Escalas a partir de Natal (SBSG).
    Distância de 1 voo = 0 escalas.  """
    if origem not in G:
        return pd.DataFrame()

    # Retorna dicionário (destino: numero_de_arestas)
    distancias = nx.single_source_shortest_path_length(G, origem)
    
    df = pd.DataFrame([
        {"destino": dest, "voos": dist, "escalas": dist - 1}
        for dest, dist in distancias.items() if dest != origem
    ])
    return df.sort_values(by="escalas")


def escalas_entre_capitais(G: nx.DiGraph, capitais: dict[str, list[str]]) -> pd.DataFrame:
    """Matriz de escalas entre capitais, calculada por BFS (Semanas 3 e 4).

    `capitais` mapeia o nome da capital para a lista de aeroportos que a atendem.
    A distância entre duas capitais é a menor entre quaisquer aeroportos delas.
    Linhas são origens e colunas são destinos. NaN indica que não há caminho
    (por exemplo, capital sem aeroporto na rede); a diagonal fica em NaN.
    """
    nomes = list(capitais)
    matriz = pd.DataFrame(np.nan, index=nomes, columns=nomes)
    for origem in nomes:
        voos = {}
        for aeroporto in capitais[origem]:
            if aeroporto not in G:
                continue
            for destino, d in nx.single_source_shortest_path_length(G, aeroporto).items():
                voos[destino] = min(d, voos.get(destino, d))
        for destino in nomes:
            if destino == origem:
                continue
            alcancaveis = [voos[a] for a in capitais[destino] if a in voos]
            if alcancaveis:
                matriz.loc[origem, destino] = min(alcancaveis) - 1
    return matriz


def eficiencia_global_dirigida(G: nx.DiGraph, n_referencia: int | None = None) -> float:
    """Calcula a eficiência global da rede (Semana 4).

    Média de 1/d sobre os n(n - 1) pares ordenados; pares sem caminho contam 0.

    `n_referencia` fixa o n do denominador. Nas simulações de fechamento, passe o
    número de aeroportos da rede original: os pares que envolvem aeroportos
    removidos passam a contar como 0, e a eficiência não sobe artificialmente
    só porque a rede ficou menor. Sem ele, n é o número de nós de G.
    """
    n = len(G) if n_referencia is None else n_referencia
    if n <= 1:
        return 0.0
    
    soma_inv_dist = 0.0
    for u in G:
        # Caminhos mínimos a partir de u
        paths = nx.single_source_shortest_path_length(G, u)
        for v, dist in paths.items():
            if u != v and dist > 0:
                soma_inv_dist += 1.0 / dist
                
    return soma_inv_dist / (n * (n - 1))
