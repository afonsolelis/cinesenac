# ADR-0012: Autenticação com sessão em cookie seguro e hash adaptativo de senha

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Segurança: autenticar atores (verificação de credenciais e gestão de sessão)
**RNFs:** [RNF28](../../requisitos-nao-funcionais.md), [RNF30](../../requisitos-nao-funcionais.md), [RNF31](../../requisitos-nao-funcionais.md)
**RFs:** RF01, RF04, RF06, RF08, RF09, RF27
**Personas:** Todas

---

## Contexto

Quatro perfis (Visitante, Cliente, Gestor, Admin) acessam áreas diferentes, e o login de Gestor e Admin usa credenciais próprias (RF01). Token no armazenamento do navegador fica acessível a qualquer script, o que aumenta o dano de uma falha de injeção de script.

## Decisão

- Senhas verificadas por **hash adaptativo**, nunca armazenadas em texto claro.
- Sessão emitida após login e transportada em **cookie `HttpOnly`, `Secure` e `SameSite`**. Scripts não têm acesso ao token.
- Expiração por inatividade (prazo a definir) e revogação imediata quando a conta é desativada (RF27).
- Todo o tráfego é **HTTPS**.
- Proteção contra falsificação de requisição entre sites (CSRF) para ações que alteram estado.
- Mensagem de erro de login genérica.

## Alternativas consideradas

- Token no armazenamento do navegador: acessível a scripts.
- Autenticação sem sessão revogável: não permite desativar uma conta de forma imediata.

## Consequências

**Positivas:**

- Menor superfície para roubo de credencial no navegador.
- Revogação imediata na desativação de conta.

**Negativas e riscos:**

- Proteção contra CSRF precisa ser implementada e testada.
- Renovação de sessão e expiração exigem tratamento no frontend.

## Relacionados

- RF01
- [Decisão D5](../../requisitos-nao-funcionais.md)
- ADR-0010
- ADR-0014

---

_Última atualização: 2026-10-22 | Rascunho para validação_
