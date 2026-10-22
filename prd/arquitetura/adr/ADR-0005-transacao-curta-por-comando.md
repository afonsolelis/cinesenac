# ADR-0005: Transação curta por comando de escrita

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Integridade: transação atômica com confirmação ou desfazimento (commit e rollback)
**RNFs:** [RNF25](../../requisitos-nao-funcionais.md), [RNF26](../../requisitos-nao-funcionais.md), [RNF07](../../requisitos-nao-funcionais.md)
**RFs:** RF21, RF22, RF25, RF27, RF30
**Personas:** Cliente, Gestor, Admin

---

## Contexto

Uma reserva de vários assentos (RN02) precisa ser tudo ou nada. Também é preciso que a resposta de sucesso só seja enviada depois da gravação, para que uma queda não deixe o cliente com confirmação sem reserva (RNF26). A latência de escrita tem meta de p95 de 800 ms (RNF07).

## Decisão

Cada comando de escrita executa em **uma transação curta**:

- A reserva de todos os assentos é gravada junta ou não é gravada.
- A resposta de sucesso só sai após o commit.
- Nenhuma chamada externa (envio de e-mail, serviço de terceiros) acontece dentro da transação.
- Criação de sala e de seus assentos (RF11) também é uma transação única.

O número máximo de assentos por pedido é um parâmetro a definir, para limitar o tamanho da transação.

## Alternativas consideradas

- Gravar assento por assento: gera reserva parcial e viola RN02.
- Transação longa abrangendo o fluxo da tela: prende bloqueios por tempo demais.
- Chamada externa dentro da transação: aumenta a latência e o risco de inconsistência.

## Consequências

**Positivas:**

- Sem reserva parcial.
- Bloqueios mantidos por pouco tempo, o que sustenta RNF07.

**Negativas e riscos:**

- Limite de assentos por pedido precisa ser definido e comunicado à interface.
- Operações que dependem de sistemas externos ficam fora da transação e precisam de compensação.

## Relacionados

- RF22, RF11, RF30
- ADR-0004
- ADR-0006

---

_Última atualização: 2026-10-22 | Rascunho para validação_
