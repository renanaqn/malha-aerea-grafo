"""Reproduz o projeto inteiro em um comando.

Etapas:
    1. baixa os dados da VRA/ANAC para data/raw/ (pula meses já baixados)
    2. constrói as redes e salva em data/processed/
    3. executa os notebooks em ordem, gravando as saídas neles
    4. confere se todas as figuras esperadas foram geradas em figures/

Uso:
    python run_all.py                    # tudo
    python run_all.py --forcar-download  # baixa os dados de novo
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

# a ordem de iteração de conjuntos de strings varia entre execuções do Python;
# fixar a semente deixa as saídas impressas nos notebooks idênticas a cada execução
os.environ["PYTHONHASHSEED"] = "0"
# acentos corretos na saída dos scripts e dos notebooks, mesmo no Windows
os.environ["PYTHONUTF8"] = "1"

NOTEBOOKS = [
    "01_descricao_rede.ipynb",
    "02_hipoteses_e_centralidades.ipynb",
    "03_curvas_fechamento.ipynb",
    "04_aeroportos_criticos.ipynb",
    "05_poa_simulado_vs_real.ipynb",
]

FIGURAS = [
    "01_distribuicao_grau.png",
    "01_matriz_adjacencia.png",
    "01_mapa_rede.png",
    "02_grau_vs_betweenness.png",
    "02_kshells.png",
    "02_escalas_capitais.png",
    "03_curvas_fechamento.png",
    "03_primeiros_fechamentos.png",
    "04_dano_vs_centralidade.png",
    "04_capitais_sem_brasilia.png",
    "05_simulado_vs_real.png",
    "05_sul_antes_depois.png",
    "05_mapa_antes_depois.png",
]


def rodar_script(nome: str, *args: str) -> None:
    subprocess.run([sys.executable, str(RAIZ / "scripts" / nome), *args], cwd=RAIZ, check=True)


def executar_notebook(caminho: Path) -> None:
    import nbformat
    from nbclient import NotebookClient

    nb = nbformat.read(caminho, as_version=4)
    NotebookClient(nb, timeout=1800, kernel_name="python3",
                   resources={"metadata": {"path": str(caminho.parent)}}).execute()
    # horários de execução mudam a cada rodada e só poluiriam o histórico do git
    for celula in nb.cells:
        celula.metadata.pop("execution", None)
    nbformat.write(nb, caminho)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--forcar-download", action="store_true", help="baixa os dados da ANAC de novo")
    args = parser.parse_args()
    # sem isso, os títulos das etapas aparecem fora de ordem com a saída dos scripts
    sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")

    inicio = time.time()

    print("\n=== 1/4 Baixando os dados da ANAC ===")
    rodar_script("baixar_dados.py", *(["--forcar"] if args.forcar_download else []))

    print("\n=== 2/4 Construindo as redes ===")
    rodar_script("construir_rede.py")

    print("\n=== 3/4 Executando os notebooks ===")
    for nome in NOTEBOOKS:
        t = time.time()
        print(f"[..] {nome}", flush=True)
        executar_notebook(RAIZ / "notebooks" / nome)
        print(f"[ok] {nome} ({time.time() - t:.0f} s)")

    print("\n=== 4/4 Conferindo as figuras ===")
    faltando = [f for f in FIGURAS if not (RAIZ / "figures" / f).exists()]
    if faltando:
        print(f"[erro] figuras não geradas: {faltando}")
        return 1
    print(f"[ok] {len(FIGURAS)} figuras em figures/")

    print(f"\nConcluído em {(time.time() - inicio) / 60:.1f} min.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
