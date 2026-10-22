# RF30 — Cancelamento de reserva pelo Admin

**Requisito:** o Admin consulta as reservas de qualquer cliente e cancela, liberando os assentos.
**Personas:** Admin.
**RNFs realizados:** [RNF01](../../requisitos-nao-funcionais.md) (integridade), [RNF26](../../requisitos-nao-funcionais.md) (durabilidade), [RNF29](../../requisitos-nao-funcionais.md) (autorização), [RNF33](../../requisitos-nao-funcionais.md) (auditoria).
**Entidades:** Reserva, Assento, Cliente, RegistroAuditoria ([classes](../estatica/classes.md)).

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor A as Admin
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional
    participant AUD as Auditoria

    A->>FE: Busca reservas de um cliente
    FE->>API: GET /reservas?cliente={id}
    API->>AUTZ: Confirma perfil Admin
    alt Perfil sem permissão
        AUTZ-->>API: Negado
        API-->>FE: 403 Sem permissão
    else Perfil Admin
        API->>DB: Consulta reservas do cliente
        DB-->>API: Reservas com sessão e assento
        API-->>FE: 200 Lista de reservas
        FE-->>A: Exibe as reservas do cliente

        A->>FE: Cancela uma reserva
        FE->>API: DELETE /reservas/{id}
        API->>AUTZ: Confirma perfil Admin
        API->>DB: Inicia transação
        API->>DB: Remove a reserva e libera o assento
        DB-->>API: Assento disponível de novo
        API->>DB: Confirma transação
        API->>AUD: Registra cancelamento com autor, reserva e data
        API-->>FE: 200 Reserva cancelada
        FE-->>A: Atualiza as reservas e o mapa da sessão
    end
```

## Notas de RNF

- **RNF01:** ao cancelar, o assento volta a ficar livre na mesma transação. Não há intervalo em que ele apareça ocupado e livre ao mesmo tempo.
- **RNF26:** o cancelamento só responde 200 depois do commit.
- **RNF29:** a rota exige perfil Admin no servidor.
- **RNF33:** o cancelamento grava registro de auditoria com autor, reserva, assento, cliente e data.
- O mapa de assentos ([RF20](RF20-mapa-assentos.md)) mostra o assento livre na próxima consulta, sem depender do cache.
