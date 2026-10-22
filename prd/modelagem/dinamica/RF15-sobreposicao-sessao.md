# RF15 — Sobreposição de sessão na sala

**Requisito:** validar que a nova sessão não se sobrepõe a outra sessão da mesma sala.
**Personas:** Gestor, Admin.
**RNFs realizados:** [RNF04](../../requisitos-nao-funcionais.md) (sem sobreposição sob concorrência), [RNF20](../../requisitos-nao-funcionais.md) (mensagem de conflito), [RNF34](../../requisitos-nao-funcionais.md) (regra em camada testável).
**Entidades:** Sessao, Sala ([classes](../estatica/classes.md)).

## Diagrama de sequência

Dois gestores cadastram sessões sobrepostas na mesma sala ao mesmo tempo. O bloqueio por sala garante que apenas uma passe.

```mermaid
sequenceDiagram
    actor G1 as Gestor A
    actor G2 as Gestor B
    participant API as API
    participant DB as Banco relacional

    par Duas sessões sobrepostas na mesma sala
        G1->>API: POST /sessoes sala 1 das 19h às 21h
        API->>DB: Inicia transação
        API->>DB: Bloqueia a sala 1
    and
        G2->>API: POST /sessoes sala 1 das 20h às 22h
        API->>DB: Inicia transação
        API->>DB: Aguarda bloqueio da sala 1
    end
    API->>DB: Consulta sessões da sala 1 que se cruzam com 19h às 21h
    DB-->>API: Nenhuma sobreposição
    API->>DB: Insere sessão do Gestor A
    API->>DB: Confirma transação
    API-->>G1: 201 Sessão cadastrada
    DB-->>API: Bloqueio liberado
    API->>DB: Consulta sessões da sala 1 que se cruzam com 20h às 22h
    DB-->>API: Sessão das 19h às 21h encontrada
    API->>DB: Desfaz transação
    API-->>G2: 409 Conflito de horário na sala
```

## Notas de RNF

- **RNF04:** o bloqueio por sala serializa as verificações. Sem ele, as duas consultas veriam a sala livre e as duas sessões seriam gravadas.
- **Intervalo:** a sobreposição usa `[início, início + duração)`, então uma sessão que termina às 21h e outra que começa às 21h não conflitam.
- **RNF20:** o 409 informa o horário da sessão que causou o conflito.
- **RNF34:** a comparação de intervalos fica em serviço de programação testável sem a interface.
