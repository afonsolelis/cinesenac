# RF26 — Minhas reservas

**Requisito:** o cliente consulta a lista das próprias reservas.
**Personas:** Cliente.
**RNFs realizados:** [RNF06](../../requisitos-nao-funcionais.md) (latência), [RNF12](../../requisitos-nao-funcionais.md) (bundle), [RNF32](../../requisitos-nao-funcionais.md) (LGPD: só as próprias reservas).
**Entidades:** Reserva, Sessao, Assento, Cliente ([classes](../estatica/classes.md)).

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor C as Cliente
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional

    C->>FE: Abre "Minhas reservas"
    FE->>API: GET /minhas-reservas
    API->>AUTZ: Confirma sessão de cliente
    alt Sessão inválida
        API-->>FE: 401 Não autenticado
        FE-->>C: Redireciona para o login
    else Sessão válida
        API->>DB: Consulta reservas do próprio cliente, com sessão e assentos
        DB-->>API: Lista de reservas
        API-->>FE: 200 Reservas do cliente
        FE-->>C: Lista com filme, horário, assentos e valor
    end
```

## Notas de RNF

- **RNF32:** a consulta usa o identificador da sessão, não um parâmetro de cliente. Não há como pedir reservas de outro cliente.
- **RNF06:** a lista é paginada se o cliente tiver muitas reservas.
- **RNF12:** a tela de reservas é carregada sob demanda, fora do pacote inicial.
