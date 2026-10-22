# ADR-0019: Empacotamento em contêineres e configuração externa ao artefato

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Portabilidade: isolar a dependência de ambiente (contêineres e configuração externa)
**RNFs:** [RNF39](../../requisitos-nao-funcionais.md), [RNF40](../../requisitos-nao-funcionais.md), [RNF36](../../requisitos-nao-funcionais.md)
**RFs:** Transversal
**Personas:** Todas (equipe e Admin)

---

## Contexto

O mesmo artefato precisa rodar em teste e em produção sem alteração, e o teste de carga precisa ser repetível (RNF36). Parâmetros como endereço do banco, segredos e limites mudam entre ambientes. O repositório já tem um modelo de variáveis (`.env.example`).

## Decisão

- A aplicação e o banco são executados a partir de **imagens versionadas**.
- A **mesma imagem** é promovida entre teste e produção.
- Configuração (endereços, segredos, limites, TTLs) vem **somente de variáveis de ambiente** ou de um gerenciador de segredos.
- Nenhum segredo fica no repositório. O modelo de variáveis (`.env.example`) documenta o que deve ser definido.

## Alternativas consideradas

- Instalação manual por ambiente: sujeita a divergência.
- Configuração compilada por ambiente: imagens diferentes para teste e produção, o que invalida o teste.

## Consequências

**Positivas:**

- Ambientes idênticos e reproduzíveis.
- Troca de provedor com mudança de configuração, não de código.

**Negativas e riscos:**

- Exige ferramental de construção e de registro de imagens.
- Gerenciamento de segredos precisa de processo definido.

## Relacionados

- [.env.example](../../../.env.example)
- ADR-0009
- ADR-0016
- ADR-0020

---

_Última atualização: 2026-10-22 | Rascunho para validação_
