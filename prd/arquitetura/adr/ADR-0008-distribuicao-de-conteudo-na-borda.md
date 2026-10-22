# ADR-0008: Distribuição de conteúdo estático e de leitura pública na borda

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Desempenho: replicar recursos próximos ao usuário (distribuição de conteúdo)
**RNFs:** [RNF09](../../requisitos-nao-funcionais.md), [RNF13](../../requisitos-nao-funcionais.md), [RNF14](../../requisitos-nao-funcionais.md)
**RFs:** RF03, RF08, RF09, RF10, RF17, RF20
**Personas:** Visitante, Cliente

---

## Contexto

O LCP de 2,5 s no perfil 4G (RNF09) depende de arquivos estáticos e de imagens de cartaz carregados rápido, de qualquer região. Imagens de cartaz são URLs externas, e os arquivos do frontend são públicos.

## Decisão

Estáticos (scripts, estilos, fontes) e imagens de cartaz são servidos por uma **distribuição de conteúdo na borda**:

- arquivos com nome versionado por hash recebem cache de longo prazo;
- a programação pública passa pela borda, com TTL de ADR-0007;
- **rotas autenticadas nunca são cacheadas na borda**, e a resposta não depende de cookie para ser cacheável, para evitar vazamento entre usuários.

## Alternativas consideradas

- Servir tudo pela API: aumenta a carga e a latência para usuários distantes.
- Sem borda: LCP pior no público fora da região de origem.

## Consequências

**Positivas:**

- LCP e vazão melhores (RNF09 e RNF08).
- Imagens redimensionadas na borda conforme o tamanho da tela (RNF13).

**Negativas e riscos:**

- Política de invalidação por versão de arquivo precisa ser mantida.
- Erro de configuração pode cachear conteúdo pessoal; exige testes dedicados.

## Relacionados

- [Componentes: Distribuição de conteúdo](../../modelagem/estatica/componentes.md)
- ADR-0007
- ADR-0017

---

_Última atualização: 2026-10-22 | Rascunho para validação_
