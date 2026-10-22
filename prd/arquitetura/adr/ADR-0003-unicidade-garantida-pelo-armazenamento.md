# ADR-0003: Unicidade garantida por restrição no armazenamento

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Integridade: impor restrições no armazenamento (enforce constraints)
**RNFs:** [RNF01](../../requisitos-nao-funcionais.md), [RNF03](../../requisitos-nao-funcionais.md), [RNF41](../../requisitos-nao-funcionais.md)
**RFs:** RF04, RF05, RF06, RF08, RF11, RF14, RF21, RF22, RF23, RF30
**Personas:** Cliente, Gestor

---

## Contexto

Checar unicidade com uma consulta antes da inserção deixa uma janela de corrida: duas requisições simultâneas veem o recurso livre e as duas gravam. Isso viola RNF01 (assento) e RNF03 (e-mail) sob os 10.000 usuários do cenário de carga.

## Decisão

A unicidade é **imposta pela restrição do banco**, não apenas pela aplicação:

- `reservas(sessao, assento)` é única (RNF01).
- `clientes(email)` é única (RNF03).
- `assentos(sala, codigo)` é única (RF11).

A aplicação mantém a checagem prévia para mensagem amigável, mas trata a violação da restrição como conflito (HTTP 409), nunca como erro técnico.

## Alternativas consideradas

- Consulta antes da inserção: corrida entre requisições simultâneas.
- Trava em memória da aplicação: não funciona com várias instâncias (ADR-0009).
- Validação só no frontend: não protege a API.

## Consequências

**Positivas:**

- Garantia independente do número de instâncias.
- Erro de concorrência vira resposta de negócio com mensagem clara (RNF20).

**Negativas e riscos:**

- Depende de o banco escolhido suportar a restrição; é requisito para qualquer banco candidato.
- A mensagem de conflito precisa ser traduzida para o usuário.

## Relacionados

- [Classes: restrições](../../modelagem/estatica/classes.md)
- RF05, RF23
- ADR-0004 (conflitos por intervalo)

---

_Última atualização: 2026-10-22 | Rascunho para validação_
