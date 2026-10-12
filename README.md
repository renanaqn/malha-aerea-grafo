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
| Grafo dirigido e ponderado | 2 | `src/rede.py`, `construir_grafo` | modelar rotas com sentido e frequência semanal |
| Densidade | 2 | `src/metricas.py`, `resumo_rede`; `01_descricao_rede.ipynb`, seção 1 | mostrar que só 3,5% dos pares têm voo direto |
| Grau e distribuição de grau | 2 | `src/metricas.py`, `tabela_graus`; `01_descricao_rede.ipynb`, seções 3 e 4 | medir a concentração em poucos hubs e comparar o ranking antes e depois de POA |
| Matriz de adjacência | 2 | `01_descricao_rede.ipynb`, seção 6 | visualizar o bloco denso do núcleo e a periferia ligada a ele |
| Grau de entrada e de saída | 3 | `src/metricas.py`, `tabela_graus`; `01_descricao_rede.ipynb`, seção 2 | verificar que a malha é quase simétrica |
| Componentes (WCC, SCC) | 4 | `src/metricas.py`, `resumo_rede`; `01_descricao_rede.ipynb`, seção 5 | verificar a conectividade e achar aeroportos alcançáveis só em um sentido |
| Caminhos, distâncias e diâmetro | 4 | `src/metricas.py`, `resumo_rede`; `01_descricao_rede.ipynb`, seção 5 | medir a linha de base de escalas antes dos fechamentos |
| Triângulos e clustering | 4 | `src/metricas.py`, `resumo_rede`; `01_descricao_rede.ipynb`, seção 7 | mostrar onde há caminhos alternativos: clustering alto nos aeroportos médios e baixo nos hubs |
| BFS | 3 | `src/metricas.py`, `escalas_bfs_origem` e `escalas_entre_capitais`; `02_hipoteses_e_centralidades.ipynb`, seção 4 | contar escalas de Natal até cada aeroporto e entre todas as capitais |
| Caminhos e distâncias | 4 | `src/metricas.py`, `escalas_entre_capitais`; `02_hipoteses_e_centralidades.ipynb`, seção 4 | mostrar que todas as capitais se ligam com no máximo 1 escala e que Brasília liga todas diretamente |
| Centralidade de betweenness | 4 | `src/metricas.py`, `calcular_centralidades`; `02_hipoteses_e_centralidades.ipynb`, seção 1 | testar H2: identificar pontes (Manaus, Cuiabá e aeroportos amazônicos de grau baixo) |
| Centralidades de closeness e eigenvector | 4 | `src/metricas.py`, `calcular_centralidades`; `02_hipoteses_e_centralidades.ipynb`, seção 2 | mostrar que proximidade e prestígio acompanham o grau, e só a betweenness destaca as pontes |
| Eficiência | 4 | `src/metricas.py`, `eficiencia_global_dirigida`; `02_hipoteses_e_centralidades.ipynb`, seção 5 | registrar a linha de base para as simulações de fechamento |
| k-core, k-shell, core number e degeneracy | 5 | `src/metricas.py`, `analise_kcore`; `02_hipoteses_e_centralidades.ipynb`, seção 3 | confirmar a estrutura núcleo-periferia e mostrar que as pontes ficam na borda do núcleo |

## Como executar

Requer Python 3.13 (instalador do [python.org](https://www.python.org/downloads/)).

```bash
# criar e ativar o ambiente virtual
py -3.13 -m venv .venv            # Linux/macOS: python3.13 -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate

# instalar as dependências
pip install -r requirements.txt

# baixar os dados da ANAC (cerca de 75 MB, vão para data/raw/)
python scripts/baixar_dados.py

# construir a rede
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

