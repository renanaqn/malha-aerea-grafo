# Modelagem

Este documento registra como os dados da VRA viram um grafo e por que cada escolha foi feita. Decisões marcadas como **proposta** ainda precisam ser confirmadas; as marcadas como **pendente no código** já foram decididas, mas `src/rede.py` ainda não as implementa.

Os números abaixo foram medidos nos arquivos de abril a junho de 2024.

## 1. Elementos do grafo

| Elemento | Escolha | Justificativa |
|---|---|---|
| Nó | Aeroporto, identificado pelo código ICAO (ex.: SBSG, Governador Aluízio Alves, em Natal) | O fechamento acontece num aeroporto, não numa cidade. O ICAO é único e está presente em todas as linhas da VRA. |
| Aresta | Rota de A para B com voos na janela, acima do limiar de frequência | Representa uma ligação aérea que o passageiro consegue usar com regularidade. |
| Direção | Dirigido | Algumas rotas não são simétricas (ida por um aeroporto, volta por outro). Para medidas que não dependem de direção, usamos a versão não dirigida. |
| Peso | Frequência média semanal (voos na janela / semanas da janela) | Normalizar por semana permite comparar janelas de tamanhos diferentes (abril tem 30 dias; maio e junho, 59). |

**Atenção:** o peso é força da ligação, não distância. Para caminhos e escalas usamos o grafo sem peso (BFS). Se algum cálculo precisar de distância ponderada, usamos `1 / peso`.

## 2. Filtros sobre a VRA

| Filtro | Valor | Efeito | Justificativa |
|---|---|---|---|
| `Situação Voo` | `REALIZADO` | remove cerca de 4% dos voos (cancelados) | A malha que interessa é a que de fato operou. |
| `Código Tipo Linha` | `N` (Doméstica Mista) | remove internacionais (`I`, `G`) e cargueiros domésticos (`C`) | O escopo é da malha doméstica de passageiros. |
| `Código DI` | `0`, `4` ou `C` (grupo "Regular") **pendente no código** | remove cerca de 2,5% dos voos `N` realizados (extras, charters, fretamentos, retornos, voos não remunerados) | O problema trata da malha regular. Voos de retorno (`3`) e não remunerados (`6`) nem levam passageiros pagantes. |

Segundo a ANAC, o grupo "Regular" reúne os DIs 0, 4 e C. No período estudado aparecem 0 (cerca de 182,7 mil voos), 4 (349) e nenhum C.

## 3. Janelas temporais **pendente no código**

O recorte é feito pela data da **partida real** de cada voo, e não pelo arquivo mensal.

| Janela | Período | Papel |
|---|---|---|
| Referência | 01/04/2024 a 30/04/2024 | Malha antes do fechamento de POA. Base de todas as simulações. |
| Pós-fechamento | 04/05/2024 a 30/06/2024 | Malha real com POA fechado, usada para validar a simulação (H4). |

**Por que começar em 04/05 e não em 01/05:** o último voo regular no Salgado Filho (SBPA) partiu às 19h58 de 03/05/2024. Usar o arquivo de maio inteiro mantém SBPA na rede, com cerca de 400 voos dos três primeiros dias, o que contamina a comparação.

Na janela pós-fechamento, SBPA tem um único voo regular registrado (22/06), que cai abaixo do limiar e não vira aresta. A Base Aérea de Canoas (SBCO), que não existia na malha de abril, passa a ter cerca de 79 partidas por mês.

## 4. Limiar de frequência **proposta**

**Proposta:** manter uma rota se ela tiver em média **pelo menos 1 voo por semana** (cerca de 4 por mês), nas duas janelas.

Efeito do limiar (grafo dirigido, filtros da seção 2):

| Limiar (voos/mês) | Abril: nós / arestas / maior SCC | Pós-fechamento: nós / arestas / maior SCC |
|---|---|---|
| 1 | 162 / 877 / 157 | 158 / 877 / 157 |
| 2 | 157 / 840 / 157 | 157 / 836 / 155 |
| **4** | **154 / 816 / 153** | **155 / 811 / 154** |
| 8 | 143 / 732 / 136 | 133 / 713 / 130 |
| 15 | 108 / 617 / 104 | 103 / 596 / 100 |
| 30 | 74 / 449 / 73 | 72 / 428 / 69 |

Até 4 voos por mês a rede quase não muda: o limiar só remove voos esporádicos. A partir de 8, aeroportos regionais começam a sair, e o resultado passa a depender do limiar. Por isso 4 é o valor principal e **2 e 8 entram na análise de sensibilidade**.

Na janela pós-fechamento (59 dias), o limiar é aplicado sobre a frequência semanal, e não sobre o total da janela. Caso contrário, uma janela de dois meses deixaria passar rotas com metade da frequência.

## 5. Aeroportos da mesma cidade **proposta**

São Paulo, com Guarulhos (SBGR), Congonhas (SBSP) e Viracopos (SBKP), e Rio de Janeiro, com Galeão (SBGL) e Santos Dumont (SBRJ), têm mais de um aeroporto com voos regulares.

**Proposta:** no modelo principal, **não agregar**. Cada aeroporto é um nó.
- Os fechamentos reais são de um aeroporto, não de uma cidade: Congonhas fecha por nevoeiro sem que Guarulhos feche.
- Agregar esconderia exatamente a redundância que queremos medir.
- Viracopos (SBKP), em Campinas, fica a quase 100 km de São Paulo e funciona como hub próprio (da Azul).

Na **análise de sensibilidade**, rodamos também a versão agregada ("São Paulo" e "Rio de Janeiro" como um nó cada) e verificamos se os rankings mudam.

## 6. Capitais **proposta**

Para as medidas de escalas entre capitais, cada capital é representada pelo **conjunto** de aeroportos com voos regulares que a atendem. A distância até uma capital é a menor distância até qualquer um deles.

| UF | Capital | ICAO | Aeroporto | Município do aeroporto |
|---|---|---|---|---|
| AC | Rio Branco | SBRB | Plácido de Castro | Rio Branco |
| AL | Maceió | SBMO | Zumbi dos Palmares | Rio Largo |
| AM | Manaus | SBEG | Eduardo Gomes | Manaus |
| AP | Macapá | SBMQ | Alberto Alcolumbre | Macapá |
| BA | Salvador | SBSV | Deputado Luís Eduardo Magalhães | Salvador |
| CE | Fortaleza | SBFZ | Pinto Martins | Fortaleza |
| DF | Brasília | SBBR | Presidente Juscelino Kubitschek | Brasília |
| ES | Vitória | SBVT | Eurico de Aguiar Salles | Vitória |
| GO | Goiânia | SBGO | Santa Genoveva | Goiânia |
| MA | São Luís | SBSL | Marechal Cunha Machado | São Luís |
| MG | Belo Horizonte | SBCF | Tancredo Neves (Confins) | Confins |
| MS | Campo Grande | SBCG | Campo Grande | Campo Grande |
| MT | Cuiabá | SBCY | Marechal Rondon | Várzea Grande |
| PA | Belém | SBBE | Val de Cans / Júlio Cezar Ribeiro | Belém |
| PB | João Pessoa | SBJP | Presidente Castro Pinto | Santa Rita |
| PE | Recife | SBRF | Guararapes / Gilberto Freyre | Recife |
| PI | Teresina | SBTE | Senador Petrônio Portella | Teresina |
| PR | Curitiba | SBCT | Afonso Pena | São José dos Pinhais |
| RJ | Rio de Janeiro | SBGL | Galeão / Antonio Carlos Jobim | Rio de Janeiro |
| RJ | Rio de Janeiro | SBRJ | Santos Dumont | Rio de Janeiro |
| RN | Natal | SBSG | Governador Aluízio Alves | São Gonçalo do Amarante |
| RO | Porto Velho | SBPV | Governador Jorge Teixeira de Oliveira | Porto Velho |
| RR | Boa Vista | SBBV | Atlas Brasil Cantanhede | Boa Vista |
| RS | Porto Alegre | SBPA | Salgado Filho | Porto Alegre |
| SC | Florianópolis | SBFL | Hercílio Luz | Florianópolis |
| SE | Aracaju | SBAR | Santa Maria | Aracaju |
| SP | São Paulo | SBGR | Guarulhos / Governador André Franco Montoro | Guarulhos |
| SP | São Paulo | SBSP | Congonhas | São Paulo |
| SP | São Paulo | SBKP | Viracopos (só na versão agregada) | Campinas |
| TO | Palmas | SBPJ | Brigadeiro Lysias Rodrigues | Palmas |

Os nomes seguem a descrição dos aeroportos na própria VRA. O aeroporto da Pampulha (SBBH), em Belo Horizonte, não tem voos regulares domésticos no período e fica fora.

**Ponto em aberto:** com POA fechado, Porto Alegre fica sem aeroporto na rede. Duas formas de tratar: (a) considerar a capital inalcançável, que é o efeito real do fechamento; (b) aceitar Canoas (SBCO) como substituto na rede real. A proposta é usar (a) na simulação e relatar (b) na comparação com a malha real.

## 7. Variações para a análise de sensibilidade

| Variação | Valores |
|---|---|
| Limiar (voos/semana) | 0,5 · **1** · 2 |
| Agregação de cidades | **não** · sim (SP e RJ) |
| Direção | **dirigido** · não dirigido (para medidas de componentes e k-core) |

Em negrito, a versão principal.
