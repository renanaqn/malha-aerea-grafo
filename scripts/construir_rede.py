"""Constrói a rede de aeroportos a partir dos CSVs da VRA e salva em data/processed/.

Gera, para cada janela (referencia e pos_fechamento):
    rede_<janela>.graphml   grafo completo, com atributos (para os notebooks)
    arestas_<janela>.csv    lista de rotas (para conferência)

Uso:
    python scripts/baixar_dados.py      # antes, se data/raw/ estiver vazio
    python scripts/construir_rede.py
"""

import sys
from pathlib import Path

import networkx as nx

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from rede import JANELAS, arestas_para_df, construir_grafo, ler_voos_vra  # noqa: E402

PASTA_DADOS = RAIZ / "data" / "raw"
PASTA_SAIDA = RAIZ / "data" / "processed"
ARQUIVOS = ["VRA_2024_04.csv", "VRA_2024_05.csv", "VRA_2024_06.csv"]


def main() -> int:
    caminhos = [PASTA_DADOS / nome for nome in ARQUIVOS]
    faltando = [c for c in caminhos if not c.exists()]
    if faltando:
        print(f"Arquivos não encontrados: {[c.name for c in faltando]}. Execute primeiro scripts/baixar_dados.py")
        return 1

    voos = ler_voos_vra(caminhos)
    print(f"Voos domésticos regulares realizados: {len(voos)}")

    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    for nome, (inicio, fim) in JANELAS.items():
        G = construir_grafo(voos, inicio, fim)
        nx.write_graphml(G, PASTA_SAIDA / f"rede_{nome}.graphml")
        arestas_para_df(G).to_csv(PASTA_SAIDA / f"arestas_{nome}.csv", index=False, float_format="%.2f")

        print(f"\n--- {nome}: {inicio} a {fim} ---")
        print(f"Total de Aeroportos (Nós): {G.number_of_nodes()}")
        print(f"Total de Rotas (Arestas): {G.number_of_edges()}")
        print(f"Salvo em {PASTA_SAIDA.relative_to(RAIZ).as_posix()}/rede_{nome}.graphml e arestas_{nome}.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
