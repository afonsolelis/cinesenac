# ADR-0001: Estilo monólito modular em camadas com regras de negócio isoladas

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md))
**Data:** 2026-10-22
**Tática arquitetural:** Modificabilidade: encapsular e separar responsabilidades em camadas
**RNFs:** [RNF34](../../requisitos-nao-funcionais.md), [RNF37](../../requisitos-nao-funcionais.md), [RNF35](../../requisitos-nao-funcionais.md)
**RFs:** RF08, RF09, RF10, RF11, RF12, RF13, RF15, RF18, RF19, RF20, RF21, RF22, RF23, RF24, RF29; transversais aos demais RFs
**Personas:** Todas (equipe de desenvolvimento)

---

## Contexto

O CineSenac tem um domínio pequeno (catálogo, programação e reservas), uma equipe pequena e um único driver de escala concentrado na leitura pública e na disputa de assentos. Os RNFs exigem que as regras RN01 a RN04 sejam testáveis sem a interface (RNF34) e que os componentes de frontend sejam isolados (RNF37). Não há requisito que justifique distribuir o sistema em serviços independentes neste momento.

## Decisão

Adotar um **monólito modular em camadas**, com uma única unidade de implantação e módulos internos por contexto (cadastro, catálogo, programação, reservas, administração, auditoria).

As camadas são:

1. **Apresentação:** rotas e serialização. Não contém regra de negócio.
2. **Aplicação:** casos de uso. Orquestra a transação e a autorização.
3. **Domínio:** regras RN01 a RN04, cálculo de sobreposição de intervalos e cota nacional. Não depende de HTTP nem de biblioteca de banco.
4. **Persistência:** acesso ao banco por interfaces de repositório, chamadas somente pela camada de aplicação.

Dependências apontam só para dentro. A camada de domínio é testada sem subir a aplicação.

## Alternativas consideradas

- Regras na camada de rotas: mais rápido de escrever, mas acopla a regra à interface e impede testá-la isolada.
- Regras no frontend: inseguro, porque a API ficaria sem a garantia (RNF29, RF19).
- Microsserviços por entidade: custo operacional e de consistência distribuída sem driver de escala que o justifique.

## Consequências

**Positivas:**

- Regras de negócio testáveis isoladamente (RNF34).
- Módulos por contexto facilitam trocar ou dividir partes no futuro.
- Uma única implantação simplifica transações entre cadastro, sessão e reserva.

**Negativas e riscos:**

- Mais arquivos e indireção do que um CRUD simples.
- Disciplina de revisão necessária para não vazar regra para a camada de apresentação.

## Relacionados

- [Componentes](../../modelagem/estatica/componentes.md)
- [Classes](../../modelagem/estatica/classes.md)
- RF15, RF18, RF19, RF24 (regras no domínio)

---

_Última atualização: 2026-10-22 | Rascunho para validação_
