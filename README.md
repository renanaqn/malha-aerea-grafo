# Estudo da Malha Áerea do Brasil
Projeto da Unidade 1 de Algoritmos e Estrutura de Dados II.

## Integrantes
Marcelo · Renan de Aquino Pereira

## Vídeo

## Problema e Pergunta

Fechamentos de aeroportos por eventos climáticos (alagamentos, nevoeiro, tempestades) ou falhas operacionais interrompem a malha aérea e afetam cidades que nem estão próximas do evento. Em maio de 2024, as enchentes no Rio Grande do Sul fecharam o Aeroporto Salgado Filho (Porto Alegre) por meses, um caso real desse tipo de problema.
 
**Pergunta principal:** quais aeroportos brasileiros, se fechados, mais desconectam a malha doméstica ou mais aumentam o número de escalas entre as capitais? E os aeroportos mais conectados (hubs) são os mesmos que os mais críticos como ponte?

## Dados 

## Modelagem

## Conteúdo do curso utilizado
| conceito | semana | onde apareceu | para que serviu|
| --- | --- | --- | --- |
| betweenness | 4 | analise.ipynb, cél. 12 | trechos criticos |

## Como executar

Requer Python 3.13 (instalador do [python.org](https://www.python.org/downloads/)).

```bash
# 1. criar e ativar o ambiente virtual
py -3.13 -m venv .venv            # Linux/macOS: python3.13 -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate

# 2. instalar as dependências
pip install -r requirements.txt

# 3. baixar os dados da ANAC (cerca de 75 MB, vão para data/raw/)
python scripts/baixar_dados.py

# 4. construir a rede
python scripts/construir_rede.py
```

Se o download falhar com `CERTIFICATE_VERIFY_FAILED`, o Python em uso não encontra os certificados raiz do sistema (acontece, por exemplo, com o Python do MSYS2). Crie o `.venv` com o Python do python.org.

## Resultados

## Limitações e próximos passos

## Referências

## Estruturação do repositório

```
malha-aerea-grafo/
├── README.md                  
├── requirements.txt           
├── .gitignore
├── run_all.py                 # reproduz tudo em um comando
│
├── data/
│   ├── raw/                   # dados brutos (baixado pelo script)
│   └── processed/             # rede pronta (.graphml / .csv)
│
├── scripts/
│   ├── 01_baixar_vra.py       # obtém os dados da ANAC
│   └── 02_construir_rede.py   # limpeza, filtro de frequência, grafo
│
├── src/                       # funções reutilizáveis
│   ├── rede.py                # montar grafo, agregar aeroportos de SP
│   ├── metricas.py            # grau, betweenness, eficiência, k-core
│   └── fechamentos.py         # remoção de nos
│
├── notebooks/                 # notebooks de analise
│
├── figures/                   # tudo gerado pelos notebooks
└── docs/
```

