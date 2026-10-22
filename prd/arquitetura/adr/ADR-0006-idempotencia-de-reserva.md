# ADR-0006: Idempotência do comando de reserva por chave de requisição

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Confiabilidade: reexecução segura (idempotência)
**RNFs:** [RNF24](../../requisitos-nao-funcionais.md), [RNF07](../../requisitos-nao-funcionais.md), [RNF23](../../requisitos-nao-funcionais.md)
**RFs:** RF21, RF22, RF25; transversais aos demais RFs
**Personas:** Cliente

---

## Contexto

Com 10.000 usuários simultâneos, cliques repetidos e retentativas de rede, o mesmo pedido de reserva chega mais de uma vez. Sem proteção, o cliente pagaria por assentos duplicados ou veria reservas repetidas.

## Decisão

O pedido de reserva recebe uma **chave de idempotência** gerada pelo cliente, uma por tentativa de confirmação. A API:

- guarda o resultado de cada chave por um prazo de retenção a definir;
- responde ao reenvio com o mesmo resultado, sem nova gravação;
- responde 422 se a mesma chave chegar com um corpo diferente.

O frontend desabilita o botão durante a requisição e reutiliza a chave ao reenviar (decisão D3).

## Alternativas consideradas

- Deduplicar por cliente, sessão e assentos: frágil, porque o cliente pode reservar de novo os mesmos assentos após um cancelamento.
- Desabilitar retentativas: piora a disponibilidade percebida pelo usuário.

## Consequências

**Positivas:**

- Reenvio seguro, inclusive por rede instável.
- Resultado idêntico para retentativas, o que simplifica o frontend.

**Negativas e riscos:**

- Armazenamento e limpeza das chaves.
- Prazo de retenção precisa ser definido.

## Relacionados

- RF22, RF25
- [Decisão D3](../../requisitos-nao-funcionais.md)
- ADR-0005

---

_Última atualização: 2026-10-22 | Rascunho para validação_
