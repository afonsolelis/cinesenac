# ADR-0004: Bloqueio por recurso de domínio para sobreposição de intervalos

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Concorrência: controlar o acesso a recursos com bloqueio (locking) por sala e por cliente
**RNFs:** [RNF02](../../requisitos-nao-funcionais.md), [RNF04](../../requisitos-nao-funcionais.md), [RNF34](../../requisitos-nao-funcionais.md)
**RFs:** RF14, RF15, RF16, RF18, RF19, RF21, RF22, RF23, RF24
**Personas:** Gestor, Cliente

---

## Contexto

A sobreposição de sessões na sala e de reservas do cliente compara intervalos de tempo, não valores iguais. Uma restrição única não expressa essa regra. Duas transações simultâneas podem cada uma ver o intervalo livre e gravar sobreposição. RNF04 e RNF02 exigem zero sobreposição.

## Decisão

Antes de verificar a sobreposição, a transação **bloqueia o recurso que governa a regra**:

- **Sessão** (RF15): bloqueio da sala.
- **Reserva** (RF24): bloqueio das reservas do cliente.

Operações sobre salas diferentes, ou sobre clientes diferentes, não se bloqueiam. Quando uma operação precisa de mais de um bloqueio, eles são adquiridos sempre na mesma ordem (identificador crescente), para evitar impasse.

Se o banco oferecer restrição de exclusão de intervalos, ela pode complementar o bloqueio. A escolha fica para a decisão de implementação.

## Alternativas consideradas

- Isolamento serializável global: correto, mas afeta todo o sistema e reduz vazão.
- Controle otimista com versão: exige retentativa em cada conflito; a complexidade não compensa para este caso.
- Fila única de comandos: serializa até operações independentes.

## Consequências

**Positivas:**

- Correção garantida para intervalos.
- Contenção limitada ao recurso afetado.

**Negativas e riscos:**

- Uma sala com muitas operações simultâneas fica serializada (aceitável: são poucas por sala).
- Ordem de aquisição precisa ser respeitada em todo o código.

## Relacionados

- RF15, RF24
- [Componentes: Programação e Reservas](../../modelagem/estatica/componentes.md)
- ADR-0003
- ADR-0005

---

_Última atualização: 2026-10-22 | Rascunho para validação_
