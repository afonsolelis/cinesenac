# ADR-0009: Escalonamento horizontal com instâncias da API sem estado

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Desempenho: introduzir concorrência e replicar o recurso de processamento (escalonamento horizontal, balanceamento de carga)
**RNFs:** [RNF08](../../requisitos-nao-funcionais.md), [RNF23](../../requisitos-nao-funcionais.md), [RNF36](../../requisitos-nao-funcionais.md)
**RFs:** RF03, RF17, RF20, RF21, RF22, RF29; transversais aos demais RFs
**Personas:** Todas

---

## Contexto

O cenário de carga exige cerca de 2.500 req/s em média, com picos de disputa. Uma única instância, mesmo com boa concorrência, não é a solução para disponibilidade (RNF23), e escalar verticalmente tem limite e ponto único de falha.

## Decisão

As instâncias da API **não guardam estado** entre requisições:

- sessão de usuário fica em armazenamento compartilhado ou em token assinado, validável em qualquer instância;
- permissões são carregadas por requisição ou de cache compartilhado (ADR-0013);
- estado de reserva só existe no banco.

Um balanceador de carga distribui as requisições. O número de instâncias é definido por teste de carga (RNF36), não por estimativa.

## Alternativas consideradas

- Escalar verticalmente: limite físico e ponto único de falha.
- Sessão em memória com afinidade (sticky sessions): reduz a resiliência e complica o escalonamento e a implantação.

## Consequências

**Positivas:**

- Escala e resiliência a falhas de instância.
- Implantação com substituição de instâncias sem perda de sessão.

**Negativas e riscos:**

- Cada leitura de sessão ou de permissão pode custar uma chamada ao armazenamento compartilhado.
- O armazenamento compartilhado de sessão passa a ser dependência crítica.

## Relacionados

- [Componentes: Camada de aplicação](../../modelagem/estatica/componentes.md)
- ADR-0012
- ADR-0013
- ADR-0019

---

_Última atualização: 2026-10-22 | Rascunho para validação_
