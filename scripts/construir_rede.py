"""Constrói a rede de aeroportos a partir dos CSVs da VRA e mostra um resumo.

Uso:
    python scripts/baixar_dados.py      # antes, se data/raw/ estiver vazio
    python scripts/construir_rede.py
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from rede import carregar_grafo_vra  # noqa: E402

PASTA_DADOS = RAIZ / "data" / "raw"
ARQUIVOS = ["VRA_2024_04.csv", "VRA_2024_05.csv", "VRA_2024_06.csv"]


def main() -> int:
    for nome in ARQUIVOS:
        caminho = PASTA_DADOS / nome
        if not caminho.exists():
            print(f"Arquivo {caminho} não encontrado! Execute primeiro o script scripts/baixar_dados.py")
            return 1

        G = carregar_grafo_vra(caminho, limiar_frequencia=4)

        print(f"\n--- {nome} ---")
        print(f"Total de Aeroportos (Nós): {G.number_of_nodes()}")
        print(f"Total de Rotas (Arestas): {G.number_of_edges()}")
        print("5 aeroportos mais conectados (grau total):")
        graus = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:5]
        for aeroporto, grau in graus:
            print(f" - {aeroporto}: {grau} rotas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
