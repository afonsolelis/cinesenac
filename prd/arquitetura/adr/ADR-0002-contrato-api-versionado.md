# ADR-0002: Contrato de API versionado e documentado

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Modificabilidade: manter a interface estável (versionamento e fachada de contrato)
**RNFs:** [RNF17](../../requisitos-nao-funcionais.md), [RNF15](../../requisitos-nao-funcionais.md), [RNF16](../../requisitos-nao-funcionais.md)
**RFs:** Transversal
**Personas:** Todas

---

## Contexto

O frontend (vitrine, área do cliente, painéis) e a API evoluem em paralelo. Sem contrato explícito, uma mudança na API quebra telas em produção. O cache de leitura (ADR-0007) também depende de URLs estáveis e previsíveis.

## Decisão

Expor uma **API HTTP com JSON**, com versão no caminho (ex.: `/v1`), contrato descrito em **OpenAPI**, e teste de contrato executado no build.

- Mudança compatível (campo novo opcional) entra na versão atual.
- Mudança incompatível (remoção, renomeação, mudança de tipo) cria nova versão.
- Erros seguem formato único, com código de status, código de erro de negócio e mensagem.
- Os códigos de conflito (409), regra de negócio (422) e limitação (429, 503) são os mesmos em todas as rotas.

## Alternativas consideradas

- Sem versionamento: simples, mas qualquer mudança quebra o frontend.
- GraphQL: flexível, mas complica o cache por URL (ADR-0007) e exige autorização por campo, sem ganho claro para o escopo atual.
- RPC genérico: acopla o cliente a nomes internos.

## Consequências

**Positivas:**

- Frontend e API evoluem sem bloquear uma à outra.
- URLs estáveis permitem cache na borda (ADR-0008).
- Teste de contrato no build pega quebra antes de chegar a produção.

**Negativas e riscos:**

- Manter a versão anterior durante a janela de migração.
- O contrato precisa ser mantido junto com o código.

## Relacionados

- [Requisitos funcionais](../../requisitos-funcionais.md)
- ADR-0014 (validação espelhada no contrato)
- ADR-0007 e ADR-0008 (cache por URL)

---

_Última atualização: 2026-10-22 | Rascunho para validação_
