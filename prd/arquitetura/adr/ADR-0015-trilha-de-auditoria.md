# ADR-0015: Trilha de auditoria gravada na mesma transação da ação administrativa

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Segurança: manter trilha de auditoria (audit trail)
**RNFs:** [RNF33](../../requisitos-nao-funcionais.md), [RNF32](../../requisitos-nao-funcionais.md)
**RFs:** RF04, RF06, RF07, RF16, RF26, RF27, RF28, RF30
**Personas:** Admin, Gestor

---

## Contexto

Ações administrativas e cancelamentos precisam ser rastreáveis: quem fez, o quê, em qual alvo e quando (RNF33). Um registro que pode ser perdido em uma queda não serve como prova.

## Decisão

Cada ação administrativa ou cancelamento grava um **registro de auditoria na mesma transação** da ação:

- autor, ação, alvo, data e hora, e origem da requisição;
- valores anteriores e novos, quando a ação altera dados;
- registros não são alterados nem apagados pela aplicação.

Se o registro falhar, a ação também é desfeita. Assim não existe alteração sem rastro.

## Alternativas consideradas

- Log em arquivo de texto: difícil de consultar e de proteger.
- Gravação assíncrona: pode perder evento em queda.

## Consequências

**Positivas:**

- Ação e registro são indivisíveis.
- Consulta direta para auditoria e para o painel do Admin.

**Negativas e riscos:**

- Volume de escrita adicional nas ações administrativas.
- Retenção e acesso ao registro precisam de política (pendência); dados pessoais no registro devem ser mínimos (LGPD).

## Relacionados

- RF16, RF27, RF28, RF30
- ADR-0013
- ADR-0005

---

_Última atualização: 2026-10-22 | Rascunho para validação_
