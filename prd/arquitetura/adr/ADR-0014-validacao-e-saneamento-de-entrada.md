# ADR-0014: Validação e saneamento de entrada no servidor

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Segurança: limitar a exposição e validar entrada (validate input, encode output)
**RNFs:** [RNF31](../../requisitos-nao-funcionais.md), [RNF22](../../requisitos-nao-funcionais.md), [RNF03](../../requisitos-nao-funcionais.md)
**RFs:** RF04, RF05, RF06, RF08, RF09, RF11, RF14
**Personas:** Gestor, Cliente

---

## Contexto

Os formulários recebem textos livres (sinopse, elenco, nome) e uma URL de cartaz (RF08). Uma URL com esquema `javascript:` ou um texto com script injetado chegam ao navegador de outros usuários se não forem tratados.

## Decisão

- Toda entrada é **validada no servidor** antes do caso de uso: tipo, tamanho, formato e obrigatoriedade.
- URL de cartaz aceita apenas `http` e `https`. Qualquer outro esquema é rejeitado.
- Textos livres são **saneados** na entrada e **codificados** na saída.
- O frontend aplica as mesmas regras para dar feedback imediato (RNF22), usando o contrato da API (ADR-0002) como fonte.
- O ponto de entrada envia cabeçalhos de segurança, e o frontend define uma política de conteúdo (CSP).

## Alternativas consideradas

- Validar só no frontend: não protege a API.
- Confiar no mapeamento objeto-relacional para segurança: não cobre injeção de script nem URL perigosa.

## Consequências

**Positivas:**

- Defesa em profundidade: frontend, API e ponto de entrada.
- Regra de URL testada em um só lugar.

**Negativas e riscos:**

- Regras duplicadas entre frontend e servidor, mantidas pelo contrato.
- Sanear textos pode alterar a forma como o usuário digitou; exige teste visual.

## Relacionados

- RF08, RF09, RF04, RF06
- [Requisitos não funcionais: RNF31](../../requisitos-nao-funcionais.md)
- ADR-0002
- ADR-0012

---

_Última atualização: 2026-10-22 | Rascunho para validação_
