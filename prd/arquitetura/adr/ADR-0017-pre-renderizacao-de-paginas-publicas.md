# ADR-0017: Pré-renderização das páginas públicas e aplicação por rota para áreas autenticadas

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Desempenho do frontend: pré-renderização e divisão de código por rota
**RNFs:** [RNF09](../../requisitos-nao-funcionais.md), [RNF11](../../requisitos-nao-funcionais.md), [RNF12](../../requisitos-nao-funcionais.md), [RNF14](../../requisitos-nao-funcionais.md), [RNF15](../../requisitos-nao-funcionais.md), [RNF16](../../requisitos-nao-funcionais.md)
**RFs:** RF03, RF17, RF20, RF26; transversais aos demais RFs
**Personas:** Visitante, Cliente

---

## Contexto

O público chega pela vitrine, em rede móvel, e precisa ver a programação antes de qualquer script carregar (RNF09). As áreas autenticadas são usadas por poucos perfis e não têm o mesmo requisito de primeira pintura. Esta é a decisão D1 do documento de RNF.

## Decisão

- **Páginas públicas** (programação, filmes, mapa de assentos sem dados pessoais) são pré-renderizadas ou renderizadas no servidor, com cache (ADR-0007 e ADR-0008).
- **Áreas autenticadas** (área do cliente, painel do gestor, painel do admin) são aplicações de página única, carregadas por rota.
- O código é dividido por rota, e cada rota carrega só o que usa (RNF12).
- A escolha de tecnologia concreta fica para o aceite do @architect.

## Alternativas consideradas

- SPA para tudo: primeira pintura lenta na vitrine.
- SSR para tudo: carga de servidor nas áreas autenticadas sem ganho de desempenho.

## Consequências

**Positivas:**

- LCP e cache melhores no público.
- Carga de servidor concentrada onde há ganho.

**Negativas e riscos:**

- Duas estratégias de renderização para manter.
- Mapa de assentos precisa lidar com dados que mudam (ADR-0018).

## Relacionados

- [Decisão D1](../../requisitos-nao-funcionais.md)
- ADR-0008
- ADR-0018

---

_Última atualização: 2026-10-22 | Rascunho para validação_
