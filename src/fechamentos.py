"""Simulação de fechamentos de aeroportos (remoção de nós).

Estratégias:
    aleatória       aeroportos sorteados (falhas dispersas)
    grau            do maior para o menor grau, calculado uma vez na rede intacta
    betweenness     da maior para a menor betweenness, calculada uma vez na rede intacta
    adaptativa      a cada passo, fecha o aeroporto de maior betweenness na rede
                    que sobrou (a betweenness é recalculada depois de cada fechamento)

Todas as medidas são relativas ao tamanho da rede original (n_ref), para que
fechar aeroportos nunca faça uma medida subir só porque a rede ficou menor.
"""

import networkx as nx
import numpy as np
import pandas as pd

from metricas import eficiencia_global_dirigida, escalas_entre_capitais


def medir_rede(G: nx.DiGraph, n_ref: int) -> dict:
    """Medidas de integridade da rede, relativas ao tamanho original n_ref (Semana 4)."""
    if len(G) == 0:
        return {"maior SCC": 0.0, "maior WCC": 0.0, "eficiência": 0.0}
    return {
        "maior SCC": len(max(nx.strongly_connected_components(G), key=len)) / n_ref,
        "maior WCC": len(max(nx.weakly_connected_components(G), key=len)) / n_ref,
        "eficiência": eficiencia_global_dirigida(G, n_referencia=n_ref),
    }


def ordem_por_grau(G: nx.DiGraph) -> list[str]:
    """Aeroportos do maior para o menor grau total; empates pelo código ICAO."""
    return sorted(G, key=lambda n: (-G.degree(n), n))


def ordem_por_betweenness(G: nx.DiGraph) -> list[str]:
    """Aeroportos da maior para a menor betweenness (sem peso); empates pelo código ICAO."""
    b = nx.betweenness_centrality(G, weight=None)
    return sorted(G, key=lambda n: (-b[n], n))


def simular_fechamentos(G: nx.DiGraph, ordem: list[str], passos: int | None = None) -> pd.DataFrame:
    """Fecha os aeroportos na ordem dada e mede a rede depois de cada fechamento.

    A linha 0 é a rede intacta. Colunas: fechados, fração fechada, aeroporto
    (o fechado naquele passo) e as medidas de `medir_rede`.
    """
    n_ref = len(G)
    passos = len(ordem) if passos is None else min(passos, len(ordem))
    H = G.copy()
    linhas = [{"fechados": 0, "aeroporto": None, **medir_rede(H, n_ref)}]
    for i, aeroporto in enumerate(ordem[:passos], start=1):
        H.remove_node(aeroporto)
        linhas.append({"fechados": i, "aeroporto": aeroporto, **medir_rede(H, n_ref)})
    df = pd.DataFrame(linhas)
    df.insert(1, "fração fechada", df["fechados"] / n_ref)
    return df


def fechamento_adaptativo(G: nx.DiGraph, passos: int | None = None) -> pd.DataFrame:
    """Fecha sempre o aeroporto de maior betweenness na rede que sobrou.

    Mesmo formato de saída de `simular_fechamentos`.
    """
    passos = len(G) if passos is None else min(passos, len(G))
    H = G.copy()
    ordem = []
    for _ in range(passos):
        alvo = ordem_por_betweenness(H)[0]
        ordem.append(alvo)
        H.remove_node(alvo)
    return simular_fechamentos(G, ordem)


def fechamento_aleatorio(
    G: nx.DiGraph, repeticoes: int = 50, passos: int | None = None, seed: int = 42
) -> pd.DataFrame:
    """Repete `simular_fechamentos` com ordens sorteadas.

    Devolve as linhas de todas as repetições, com a coluna `repetição`.
    A seed fixa o sorteio, para que o resultado seja reproduzível.
    """
    rng = np.random.default_rng(seed)
    nos = sorted(G)
    resultados = []
    for r in range(repeticoes):
        ordem = list(rng.permutation(nos))
        df = simular_fechamentos(G, ordem, passos)
        df.insert(0, "repetição", r)
        resultados.append(df)
    return pd.concat(resultados, ignore_index=True)


def comparar_estrategias(
    G: nx.DiGraph, passos: int | None = None, repeticoes: int = 50, seed: int = 42
) -> pd.DataFrame:
    """Roda as quatro estratégias e devolve tudo numa tabela longa.

    Para a aleatória, cada passo traz a média das repetições, e as colunas
    `<medida> p5` e `<medida> p95` trazem os percentis 5 e 95.
    """
    medidas = ["maior SCC", "maior WCC", "eficiência"]
    aleatoria = fechamento_aleatorio(G, repeticoes, passos, seed)
    resumo = aleatoria.groupby(["fechados", "fração fechada"])[medidas]
    aleatoria = resumo.mean().join(resumo.quantile(0.05).add_suffix(" p5")).join(
        resumo.quantile(0.95).add_suffix(" p95")
    ).reset_index()

    partes = {
        "aleatória": aleatoria,
        "grau": simular_fechamentos(G, ordem_por_grau(G), passos),
        "betweenness": simular_fechamentos(G, ordem_por_betweenness(G), passos),
        "adaptativa": fechamento_adaptativo(G, passos),
    }
    return pd.concat([df.assign(estratégia=nome) for nome, df in partes.items()], ignore_index=True)


def fechados_ate(curva: pd.DataFrame, medida: str, limite: float) -> int | None:
    """Menor número de fechamentos com que `medida` fica abaixo de `limite`.

    `curva` é a saída de uma única estratégia. None se nunca fica abaixo.
    """
    abaixo = curva[curva[medida] < limite]
    return int(abaixo["fechados"].min()) if len(abaixo) else None


def impacto_individual(G: nx.DiGraph, capitais: dict[str, list[str]]) -> pd.DataFrame:
    """Fecha cada aeroporto sozinho (os demais abertos) e mede o impacto.

    Colunas, uma linha por aeroporto fechado:
        perda de eficiência (%)      queda da eficiência global, com o n original
        aeroportos fora da SCC       outros aeroportos que saem da maior SCC, isto é,
                                     perdem a ida e volta com o resto da malha
        capital sem aeroporto        capital que fica sem nenhum aeroporto na rede
        pares de capitais sem caminho, pares de capitais com mais escalas,
        escalas a mais entre capitais
                                     comparação com a rede intacta, só entre as
                                     capitais que continuam com aeroporto
    """
    n_ref = len(G)
    ef_intacta = eficiencia_global_dirigida(G)
    scc_intacta = max(nx.strongly_connected_components(G), key=len)
    escalas_intacta = escalas_entre_capitais(G, capitais)

    linhas = []
    for aeroporto in sorted(G):
        H = G.copy()
        H.remove_node(aeroporto)
        restantes = {c: [a for a in aeroportos if a != aeroporto] for c, aeroportos in capitais.items()}
        sem_aeroporto = [c for c, aeroportos in restantes.items() if not aeroportos]
        restantes = {c: aeroportos for c, aeroportos in restantes.items() if aeroportos}

        antes = escalas_intacta.loc[list(restantes), list(restantes)]
        depois = escalas_entre_capitais(H, restantes)
        tinha_caminho = antes.notna()
        aumento = (depois - antes)[tinha_caminho & depois.notna()]
        maior_scc = len(max(nx.strongly_connected_components(H), key=len))

        linhas.append({
            "aeroporto": aeroporto,
            "perda de eficiência (%)": 100 * (1 - eficiencia_global_dirigida(H, n_referencia=n_ref) / ef_intacta),
            "aeroportos fora da SCC": len(scc_intacta) - maior_scc - (aeroporto in scc_intacta),
            "capital sem aeroporto": ", ".join(sem_aeroporto),
            "pares de capitais sem caminho": int((depois.isna() & tinha_caminho).sum().sum()),
            "pares de capitais com mais escalas": int((aumento > 0).sum().sum()),
            "escalas a mais entre capitais": float(aumento.sum().sum()),
        })
    return pd.DataFrame(linhas).set_index("aeroporto")
