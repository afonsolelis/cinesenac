# ADR-0016: Mudanças de esquema por migrações versionadas e reproduzíveis

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Manutenibilidade: reduzir o acoplamento entre código e esquema (migrações versionadas)
**RNFs:** [RNF41](../../requisitos-nao-funcionais.md), [RNF36](../../requisitos-nao-funcionais.md), [RNF39](../../requisitos-nao-funcionais.md)
**RFs:** RF04, RF08, RF11, RF14, RF22; transversais aos demais RFs
**Personas:** Equipe de desenvolvimento, Admin

---

## Contexto

O modelo de dados está em DBML (prd/dbdiagram.dbml), mas o banco de cada ambiente precisa ser criado e alterado de forma reproduzível. Alterações manuais deixam ambientes diferentes entre si e o teste de carga impossível de repetir (RNF36).

## Decisão

- O esquema é versionado em **migrações ordenadas**, aplicadas do zero em qualquer ambiente.
- O DBML é a referência de modelagem, e cada migração é revisada contra ele.
- Alterações retrocompatíveis seguem duas etapas: **expandir** (adicionar) e depois **contrair** (remover), para permitir a troca gradual da versão da aplicação.
- Migrações não são geradas automaticamente a partir do código sem revisão.

## Alternativas consideradas

- Alterações manuais no banco: não reproduzíveis.
- Sincronizar esquema a partir do código sem revisão: risco de perda de dados sem percepção.

## Consequências

**Positivas:**

- Ambientes reproduzíveis e teste de carga repetível.
- Mudanças revisáveis e reversíveis.

**Negativas e riscos:**

- Dupla manutenção: DBML e migração precisam ficar alinhados.
- Migrações de grande volume exigem janela de execução.

## Relacionados

- [dbdiagram.dbml](../../dbdiagram.dbml)
- ADR-0003
- ADR-0019

---

_Última atualização: 2026-10-22 | Rascunho para validação_
