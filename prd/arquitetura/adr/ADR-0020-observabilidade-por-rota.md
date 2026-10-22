# ADR-0020: Observabilidade por rota com métricas, logs estruturados e rastreamento

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Monitoramento: detectar e diagnosticar falhas (monitor e registro de eventos)
**RNFs:** [RNF38](../../requisitos-nao-funcionais.md), [RNF36](../../requisitos-nao-funcionais.md), [RNF23](../../requisitos-nao-funcionais.md)
**RFs:** RF29; transversais aos demais RFs
**Personas:** Admin

---

## Contexto

Os cenários C1 a C6 só têm valor se for possível explicar onde a latência ou o erro aparecem. O Admin precisa acompanhar a integridade do sistema (objetivo da persona Admin), e RNF23 exige medir disponibilidade.

## Decisão

- **Métricas** por rota: latência (p50, p95, p99), taxa de erro por código, saturação e contagem de 409, 429 e 503.
- **Logs estruturados** com identificador de requisição, sem dados pessoais (RNF32).
- **Rastreamento** de requisição entre componentes, opcional no escopo inicial.
- **Alertas** nos limites definidos em RNF06 e RNF23.
- O painel do Admin (RF29) mostra o resumo, e o detalhamento fica nas ferramentas de observabilidade.

## Alternativas consideradas

- Só logs: difícil de agregar e de medir percentis.
- Monitoramento apenas externo: mostra que está lento, mas não a causa.

## Consequências

**Positivas:**

- Diagnóstico de C1 a C6 com dados por rota.
- Base para ajustar limites (ADR-0010).

**Negativas e riscos:**

- Custo de armazenamento e de processamento de métricas.
- Cuidado para não registrar dados pessoais nos logs.

## Relacionados

- RF29
- ADR-0010
- ADR-0011

---

_Última atualização: 2026-10-22 | Rascunho para validação_
