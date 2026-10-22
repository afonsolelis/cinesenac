# ADR-0010: Limitação de taxa e degradação controlada acima da capacidade

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Disponibilidade: limitar a resposta a eventos (limitação de taxa e controle de admissão)
**RNFs:** [RNF27](../../requisitos-nao-funcionais.md), [RNF30](../../requisitos-nao-funcionais.md), [RNF08](../../requisitos-nao-funcionais.md)
**RFs:** RF01, RF03, RF17, RF20, RF21, RF22, RF29
**Personas:** Visitante, Cliente

---

## Contexto

Acima da capacidade medida, uma fila sem limite gera latência indefinida e queda total. RNF30 exige contar falhas de login por e-mail e por IP, sem bloquear a pessoa legítima. Em todo caso, a resposta de erro deve ser útil.

## Decisão

Duas políticas:

1. **Login (RNF30):** limite de tentativas por e-mail e por IP, com bloqueio temporário após N falhas (N a definir). A resposta é 429.
2. **Capacidade (RNF27):** limite por rota, acima da capacidade medida no teste de carga, respondendo **503 com `Retry-After`**. O frontend mostra "tente novamente" e não exibe tela em branco.

Os limites numéricos são definidos depois do teste de carga, e não estimados.

## Alternativas consideradas

- Sem limite: queda total sob sobrecarga.
- Fila sem limite: latência indefinida para todos.
- Bloqueio permanente de IP: gera falsos positivos em redes compartilhadas.

## Consequências

**Positivas:**

- Sistema responde de forma previsível sob sobrecarga.
- Força bruta no login fica contida sem afetar usuários comuns.

**Negativas e riscos:**

- Usuários legítimos podem ser recusados em picos.
- Exige métricas para ajustar os limites (ADR-0020).

## Relacionados

- RF01, RF03, RF17, RF20, RF21
- [Cenário C6](../../requisitos-nao-funcionais.md)
- ADR-0020

---

_Última atualização: 2026-10-22 | Rascunho para validação_
