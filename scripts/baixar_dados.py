"""Baixa os arquivos mensais da base VRA (Voo Regular Ativo) da ANAC.

Fonte: https://siros.anac.gov.br/siros/registros/diversos/vra/
Formato conferido em 01/10/2026: um CSV por mês (VRA_AAAA_MM.csv), UTF-8,
separador ";", uma linha por voo.

Uso:
    python scripts/baixar_dados.py            # baixa os meses do projeto
    python scripts/baixar_dados.py --forcar   # baixa de novo mesmo se já existir
"""

import argparse
import shutil
import sys
import urllib.request
from pathlib import Path

URL_BASE = "https://siros.anac.gov.br/siros/registros/diversos/vra/{ano}/VRA_{ano}_{mes:02d}.csv"

# abril/2024: referência, antes do fechamento de POA (03/05/2024)
# maio e junho/2024: malha real com POA fechado
MESES = [(2024, 4), (2024, 5), (2024, 6)]

COLUNAS_ESPERADAS = [
    "Sigla ICAO Empresa Aérea",
    "Sigla ICAO Aeroporto Origem",
    "Sigla ICAO Aeroporto Destino",
    "Código Tipo Linha",
    "Situação Voo",
]

RAIZ = Path(__file__).resolve().parents[1]
PASTA_DESTINO = RAIZ / "data" / "raw"


def conferir_cabecalho(caminho: Path) -> None:
    """Falha se o arquivo não tiver as colunas que o parser usa."""
    with open(caminho, encoding="utf-8") as f:
        cabecalho = f.readline().strip().split(";")
    faltando = [c for c in COLUNAS_ESPERADAS if c not in cabecalho]
    if faltando:
        raise ValueError(f"{caminho.name}: colunas ausentes {faltando}. Verificar formato da VRA")


def baixar_mes(ano: int, mes: int, forcar: bool = False) -> Path:
    destino = PASTA_DESTINO / f"VRA_{ano}_{mes:02d}.csv"
    if destino.exists() and not forcar:
        print(f"[ok] {destino.name} já existe, pulando")
        return destino

    url = URL_BASE.format(ano=ano, mes=mes)
    temporario = destino.with_suffix(".part")
    print(f"[..] baixando {url}")
    # se der CERTIFICATE_VERIFY_FAILED, o problema é o Python local sem certificados raiz
    # (ex.: Python do MSYS2). Use um .venv criado com o Python do python.org.
    with urllib.request.urlopen(url, timeout=120) as resposta, open(temporario, "wb") as f:
        shutil.copyfileobj(resposta, f)

    # só substitui o arquivo final se o download terminou e o formato confere
    conferir_cabecalho(temporario)
    temporario.replace(destino)
    print(f"[ok] {destino.name} ({destino.stat().st_size / 1e6:.1f} MB)")
    return destino


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--forcar", action="store_true", help="baixa de novo mesmo se o arquivo já existir")
    args = parser.parse_args()

    PASTA_DESTINO.mkdir(parents=True, exist_ok=True)
    for ano, mes in MESES:
        baixar_mes(ano, mes, forcar=args.forcar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
