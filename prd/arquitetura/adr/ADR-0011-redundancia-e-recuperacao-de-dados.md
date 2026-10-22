# ADR-0011: Redundância do banco e recuperação por backup testado

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Disponibilidade: redundância ativa e recuperação por backup (recover: restore)
**RNFs:** [RNF23](../../requisitos-nao-funcionais.md), [RNF26](../../requisitos-nao-funcionais.md)
**RFs:** RF22, RF27, RF30; transversais aos demais RFs
**Personas:** Admin, Gestor

---

## Contexto

Uma reserva confirmada não pode se perder (RNF26), e o sistema precisa se manter disponível durante a janela de teste e de produção (RNF23). O banco é o único ponto que guarda estado de negócio.

## Decisão

- O banco tem **réplica** pronta para assumir em caso de falha do primário (failover).
- Há **backup periódico** com retenção definida, e a restauração é **testada** em ciclos regulares.
- A meta de RPO é de até 24 h (proposta), com RTO a definir.

A réplica é de disponibilidade. A escolha entre replicação síncrona e assíncrona fica para a decisão de implementação, com o trade-off entre perda de dados e latência explicitado.

## Alternativas consideradas

- Sem réplica: ponto único de falha.
- Replicação síncrona entre regiões: custo e complexidade desproporcionais ao escopo atual.

## Consequências

**Positivas:**

- Recuperação de falha de instância ou de banco.
- Teste de restauração prova que o backup funciona.

**Negativas e riscos:**

- Custo de réplica e de armazenamento de backup.
- A restauração precisa de procedimento documentado e de teste regular.

## Relacionados

- RNF26
- RNF23
- ADR-0009
- ADR-0016

---

_Última atualização: 2026-10-22 | Rascunho para validação_
