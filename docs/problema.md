# O problema: vulnerabilidade da malha aérea brasileira a fechamentos

## Contexto

O Brasil depende do transporte aéreo para ligar regiões distantes. Para boa parte das capitais do Norte e do Nordeste, o avião é a única alternativa prática a viagens terrestres de dias. Essa malha, porém, não é uniforme: poucos aeroportos concentram a maior parte das rotas e funcionam como pontos de conexão para o resto do país.

Essa concentração é eficiente no dia a dia, mas cria uma fragilidade. Quando um aeroporto central fecha, por alagamento, nevoeiro, tempestade ou falha operacional, o efeito não fica restrito à sua cidade. Voos que dependiam dele como escala deixam de existir e cidades distantes do evento passam a precisar de mais conexões, ou perdem a ligação aérea.

O caso mais claro dos últimos anos foi o fechamento do Aeroporto Internacional Salgado Filho (POA, SBPA), em Porto Alegre, durante as enchentes do Rio Grande do Sul. As operações foram suspensas em 3 de maio de 2024 e só voltaram em 21 de outubro de 2024. Nesse intervalo, parte dos voos foi transferida para a Base Aérea de Canoas e para aeroportos do interior gaúcho e de Santa Catarina. O episódio é um experimento natural: temos a malha antes do fechamento (abril/2024) e a malha real depois dele (maio e junho/2024).

## Por que é um problema de rede

A pergunta "qual aeroporto é mais importante?" parece ter uma resposta simples: o que tem mais voos. Mas importância para a **robustez** é outra coisa. Um aeroporto pode ter poucos voos e ainda assim ser a única ligação entre uma região e o resto do país. Fechá-lo isola essa região, enquanto fechar um hub grande pode ser compensado por outros hubs.

Essa diferença entre **ser muito conectado** e **ser insubstituível** só aparece olhando a estrutura da rede inteira. Não dá para respondê-la com uma tabela de movimentação por aeroporto: é preciso saber por onde passam os caminhos entre todos os pares de aeroportos e o que acontece com esses caminhos quando um nó sai da rede.

## Pergunta principal

> Quais aeroportos brasileiros, se fechados, mais desconectam a malha doméstica ou mais aumentam o número de escalas entre as capitais? Os aeroportos mais conectados (hubs) são os mesmos que os mais críticos como ponte?

## Definições usadas neste trabalho

| Termo | Significado no projeto |
|---|---|
| **Malha** | Grafo dirigido em que os nós são aeroportos (código ICAO) e há aresta de A para B se existe rota regular doméstica de A para B na janela, acima de um limiar mínimo de frequência. O peso é a frequência de voos. |
| **Fechamento** | Remoção de um nó (e de todas as suas arestas) do grafo. Na literatura de robustez de redes, isso é chamado de "ataque" (Albert, Jeong e Barabási, 2000). |
| **Hub** | Aeroporto com grau alto (muitas rotas de entrada e de saída). |
| **Ponte** | Aeroporto com betweenness alta, isto é, que aparece em muitos dos menores caminhos entre outros pares de aeroportos. Não confundir com "ponte" no sentido de aresta cuja remoção desconecta o grafo. |
| **Escalas** | Número de voos de um menor caminho menos um. Calculado por BFS, sem peso, porque frequência mede força da ligação e não distância. |
| **Capitais** | Os aeroportos principais das 26 capitais estaduais e de Brasília. |

## Como medir o impacto de um fechamento

Cada fechamento é avaliado comparando a rede antes e depois da remoção, por quatro medidas:

1. **Tamanho relativo da maior componente** (fração dos aeroportos restantes na maior componente fortemente conexa e na maior fracamente conexa). Responde "quanto a malha se desconecta".
2. **Eficiência global** (média de 1/distância entre todos os pares). Diferente do diâmetro, continua definida quando a rede se fragmenta, e capta tanto desconexão quanto alongamento de caminhos.
3. **Escalas entre capitais**: média de escalas entre os pares de capitais e número de pares que deixam de ter caminho.
4. **Escalas a partir de Natal (SBSG)**: escalas de Natal até cada capital, como estudo de caso concreto e próximo de nós.

## Subperguntas

1. A malha brasileira tem estrutura núcleo-periferia? Quais aeroportos formam o núcleo?
2. Os aeroportos com maior grau coincidem com os de maior betweenness? Quais aeroportos são pontes sem serem hubs?
3. Como a malha se degrada sob remoção aleatória (falhas dispersas) comparada à remoção direcionada (fechamento dos aeroportos mais centrais)?
4. Um fechamento regional, com vários aeroportos vizinhos fechando ao mesmo tempo, é pior que a soma dos fechamentos individuais?
5. Quantas escalas a mais um passageiro saindo de Natal precisa para chegar às capitais quando um hub fecha?
6. A simulação do fechamento de Porto Alegre prevê o que de fato aconteceu com a malha em maio e junho de 2024?

### Como cada subpergunta se traduz em conceitos do curso

| Subpergunta | Conceitos | Semana |
|---|---|---|
| 1. Núcleo e periferia | k-core, k-shell, core number, núcleo e periferia | 3 e 5 |
| 2. Hubs vs pontes | grau de entrada e de saída, distribuição de grau, centralidade de betweenness, closeness e eigenvector | 2 e 4 |
| 3. Remoção aleatória vs direcionada | componentes (SCC, WCC, GCC), eficiência, centralidades | 4 |
| 4. Fechamento regional | subredes, componentes, eficiência | 2 e 4 |
| 5. Escalas a partir de Natal | BFS, caminhos e distâncias | 3 e 4 |
| 6. POA simulado vs real | comparação entre a rede de abril com POA removido e a rede real de maio e junho: grau, componentes, eficiência, escalas | 2 e 4 |

## Hipóteses

Cada hipótese vem acompanhada do resultado que a refutaria.

- **H1.** A malha é robusta a falhas aleatórias e frágil a fechamentos direcionados, como outras redes com distribuição de grau concentrada.
  *Refutada se* as curvas de tamanho da maior componente e de eficiência sob remoção por grau ou betweenness ficarem próximas da média das remoções aleatórias.
- **H2.** Existem aeroportos com betweenness alta e grau baixo ou médio, que funcionam como pontes regionais e não aparecem em rankings de movimentação.
  *Refutada se* o ranking por grau e o ranking por betweenness forem praticamente iguais no topo (por exemplo, mesmos 10 primeiros).
- **H3.** A remoção adaptativa (recalculando a betweenness a cada fechamento) degrada a malha mais rápido que a remoção por grau.
  *Refutada se* a curva adaptativa não ficar abaixo da curva por grau nos primeiros fechamentos.
- **H4.** A simulação estática superestima o dano de fechar POA, porque não captura a realocação de voos para aeroportos próximos.
  *Refutada se* as métricas da rede real de maio e junho forem iguais ou piores que as da rede de abril com POA removido.

## Quem se beneficia

- **Órgãos de planejamento** (ANAC, secretarias estaduais de infraestrutura): identificar aeroportos cuja falha tem efeito desproporcional e que merecem investimento em contingência.
- **Companhias aéreas**: antecipar quais rotas alternativas absorvem a demanda quando um hub fecha.
- **Estados com poucas ligações aéreas**: entender o quanto dependem de um único aeroporto de conexão.

## Escopo

**Inclui:** voos domésticos regulares de passageiros, a partir da base VRA (Voo Regular Ativo) da ANAC, em duas janelas de 2024: abril (referência, antes do fechamento de POA) e maio a junho (malha real após o fechamento).

**Não inclui:** voos internacionais, cargueiros e táxi aéreo; volume de passageiros; conexões terrestres; capacidade de infraestrutura; dinâmica de propagação de atrasos ao longo do dia; modelos epidemiológicos de difusão.

A propagação de surtos pela malha aérea é uma pergunta relacionada, mas exige modelos de difusão que estão fora do conteúdo das semanas 2 a 6. Fica registrada como extensão possível.

## Como saberemos que a pergunta foi respondida

- Um ranking de aeroportos críticos por cada critério (grau, betweenness, impacto na maior componente, impacto na eficiência), com a comparação entre eles.
- Curvas de fechamento que mostrem quantos fechamentos bastam para fragmentar a malha em cada estratégia.
- A variação de escalas de Natal até as capitais em pelo menos um cenário de fechamento.
- A comparação entre a simulação e a malha real após o fechamento de POA, dizendo onde o modelo acertou e onde falhou.

## Riscos e limitações previstas

- **Topologia não é demanda:** uma ponte estrutural pode transportar poucos passageiros. Sem dados de passageiros, a análise mede impacto estrutural, não impacto em pessoas.
- **Análise estática:** a rede real se adapta em dias; a simulada não. A subpergunta 6 existe justamente para medir esse erro.
- **Sensibilidade às escolhas de modelagem:** janela temporal, limiar de frequência e agregação de aeroportos da mesma cidade (por exemplo, GRU, CGH e VCP em São Paulo) mudam os resultados. Por isso testamos variações, registradas em `docs/modelagem.md`.
- **Conexões terrestres:** aeroportos próximos (por exemplo, Navegantes e Florianópolis) se substituem por estrada, o que a rede não enxerga.
- **Qualidade dos dados:** a VRA registra voos previstos e realizados; voos cancelados precisam ser filtrados para não inflar a frequência.

## Referências

- AGÊNCIA NACIONAL DE AVIAÇÃO CIVIL (ANAC). Voo Regular Ativo (VRA). Dados abertos.
