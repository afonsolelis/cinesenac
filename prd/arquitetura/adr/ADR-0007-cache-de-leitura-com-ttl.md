# ADR-0007: Cache de leitura da programação pública com TTL curto

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Desempenho: manter cópias dos dados de leitura (caching)
**RNFs:** [RNF06](../../requisitos-nao-funcionais.md), [RNF08](../../requisitos-nao-funcionais.md), [RNF14](../../requisitos-nao-funcionais.md)
**RFs:** RF03, RF10, RF13, RF17, RF20, RF21, RF22, RF26, RF29
**Personas:** Visitante, Cliente

---

## Contexto

A consulta pública (RF03 e RF17) é o maior componente da carga do cenário de 10.000 usuários, cerca de 60% do mix (premissa P03). Sem cache, o banco absorve cerca de 2.500 req/s só para leitura de programação, que muda pouco em um intervalo de segundos.

## Decisão

A **programação pública** (filmes em cartaz e sessões publicadas) fica em cache de leitura com **TTL de 30 s**, com chave que inclui os filtros.

Regras:

- O cache só serve leitura. Escritas sempre vão ao banco.
- A invalidação é por expiração (TTL). Não há invalidação ativa no escopo inicial.
- O **mapa de assentos e as reservas do cliente não entram no cache** (ver ADR-0018).

## Alternativas consideradas

- Sem cache: exige dimensionar o banco para toda a leitura pública.
- Invalidação ativa a cada escrita: mais precisa, mas acopla o cache a cada caso de uso.
- TTL longo: reduz mais a carga, mas aumenta a defasagem da programação.

## Consequências

**Positivas:**

- Reduz a carga de leitura no banco (meta de acerto ≥ 90%, RNF14).
- Implementação simples.

**Negativas e riscos:**

- Mudança de programação só aparece para o público após até 30 s.
- Precisa-se confirmar com o produto se 30 s é aceitável para a vitrine (pendência).

## Achados da implementação

Observado em 2026-10-22, na primeira execução real da aplicação (ver [ADR-0021](ADR-0021-stack-de-implementacao-inicial.md)):

- Uma publicação de dia (RF19) não aparece na vitrine enquanto a entrada de cache da programação não expira. Com TTL de 30 s, o atraso máximo é de 30 s.
- A consulta com chave de filtros nova mostra a programação atual, o que confirma que o banco já tem a publicação.
- A decisão de não invalidar ativamente no escopo inicial continua valendo. O efeito é perceptível para o gestor, que publica e espera ver o resultado na vitrine.

**Proposta a decidir pelo [@architect](../../../.github/agents/architect.agent.md):** invalidar a entrada de programação pública ao publicar um dia, cancelar uma sessão ou alterar uma sessão. Escritas nesse cenário são raras, então o custo é baixo e a defasagem some para o gestor. Enquanto isso não for decidido, o comportamento segue a regra documentada acima.

## Relacionados

- RF03, RF17
- ADR-0008 (borda)
- ADR-0018 (exceção do mapa)

---

_Última atualização: 2026-10-22 | Rascunho para validação_
