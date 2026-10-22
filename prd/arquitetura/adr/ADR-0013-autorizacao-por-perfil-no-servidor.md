# ADR-0013: Autorização por perfil e titularidade verificada no servidor

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Segurança: autorizar atores (checagem centralizada de permissão)
**RNFs:** [RNF29](../../requisitos-nao-funcionais.md), [RNF32](../../requisitos-nao-funcionais.md), [RNF33](../../requisitos-nao-funcionais.md)
**RFs:** RF02, RF04, RF06, RF07, RF09, RF12, RF16, RF26, RF27, RF28, RF30
**Personas:** Gestor, Admin, Cliente

---

## Contexto

Cada rota expõe funcionalidade de um perfil. O frontend esconder um botão não é controle de acesso. Dados de cliente só podem ser vistos pelo titular, ou pelo Admin (RNF32).

## Decisão

- Cada rota declara o perfil ou a permissão exigida.
- Uma **camada de autorização única** aplica essa regra antes do caso de uso. Não existe verificação espalhada em cada controlador.
- Dados pessoais do cliente exigem **checagem de titularidade**, além do perfil.
- Permissões de um perfil são carregadas para a requisição ou de cache compartilhado, e são invalidadas quando o Admin as altera (RF28).

## Alternativas consideradas

- Verificação em cada controlador: fácil de esquecer em uma rota nova.
- Verificação só no frontend: inseguro.

## Consequências

**Positivas:**

- Uma regra por rota, auditável.
- Alteração de permissão tem efeito imediato.

**Negativas e riscos:**

- Cache de permissões precisa de invalidação coordenada entre instâncias.
- Cada requisição paga uma leitura de permissão, ou um acerto de cache.

## Relacionados

- RF02, RF06, RF07, RF28
- ADR-0009
- ADR-0015

---

_Última atualização: 2026-10-22 | Rascunho para validação_
