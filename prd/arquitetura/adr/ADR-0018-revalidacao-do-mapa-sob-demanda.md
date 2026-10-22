# ADR-0018: Revalidação do mapa de assentos sob demanda, sem polling

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Desempenho e integridade: revalidar sob demanda em vez de atualizar continuamente
**RNFs:** [RNF01](../../requisitos-nao-funcionais.md), [RNF06](../../requisitos-nao-funcionais.md), [RNF08](../../requisitos-nao-funcionais.md), [RNF20](../../requisitos-nao-funcionais.md)
**RFs:** RF03, RF05, RF10, RF13, RF15, RF17, RF20, RF21, RF22, RF23, RF24, RF26, RF29, RF30
**Personas:** Cliente

---

## Contexto

O mapa de assentos precisa mostrar ocupação atual sem sobrecarregar o servidor. Atualizar a cada 5 s com 10.000 usuários adicionaria cerca de 2.000 req/s, equivalente a 80% da carga média estimada (decisão D2). O cache de programação não se aplica ao mapa (ADR-0007).

## Decisão

- O mapa é carregado ao abrir a sessão.
- Ele é **revalidado antes da confirmação** (RF21) e pode ser atualizado pelo cliente.
- A **garantia final** é sempre a restrição do banco (ADR-0003). O mapa é apenas uma prévia.
- Não há polling automático nem conexão persistente no escopo inicial.

O critério para revisitar esta decisão é a taxa de conflitos de assento (409 de RF23) medida nos testes; se passar de um limite a definir, avalia-se atualização por push.

## Alternativas consideradas

- Polling a cada 5 s: cerca de 80% de carga extra sobre a média.
- Conexão persistente por sessão: custo de conexões com 10.000 usuários e estado por instância, em conflito com ADR-0009.
- Push para todos os clientes: complexidade sem ganho proporcional.

## Consequências

**Positivas:**

- Carga previsível e baixa.
- Garantia de integridade independente da prévia na tela.

**Negativas e riscos:**

- O cliente pode ver assento como livre até revalidar; mitigado pela mensagem de conflito (RNF20).
- Exige teste específico de taxa de conflito.

## Relacionados

- RF20, RF21, RF23
- [Decisão D2](../../requisitos-nao-funcionais.md)
- ADR-0003
- ADR-0007

---

_Última atualização: 2026-10-22 | Rascunho para validação_
