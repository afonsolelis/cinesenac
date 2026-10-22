# RF23 — Bloqueio de assento ocupado

**Requisito:** bloquear a seleção ou reserva de um assento já ocupado por outro cliente na mesma sessão (RN01).
**Personas:** Cliente.
**RNFs realizados:** [RNF01](../../requisitos-nao-funcionais.md) (integridade), [RNF20](../../requisitos-nao-funcionais.md) (mensagem clara), [RNF34](../../requisitos-nao-funcionais.md) (regra testável).
**Entidades:** Reserva, Assento, Sessao ([classes](../estatica/classes.md)).

## Diagrama de sequência

Dois clientes tentam o mesmo assento. O segundo é bloqueado pela restrição única, e o mapa é atualizado.

```mermaid
sequenceDiagram
    actor C1 as Cliente A
    actor C2 as Cliente B
    participant FE2 as Frontend do Cliente B
    participant API as API
    participant DB as Banco relacional

    par Dois clientes reservam o mesmo assento
        C1->>API: POST /reservas com assento A7
        API->>DB: Insere reserva de A7 na sessão
    and
        C2->>API: POST /reservas com assento A7
        API->>DB: Insere reserva de A7 na sessão
    end
    DB-->>API: Primeira inserção confirmada
    API-->>C1: 201 Reserva confirmada
    DB-->>API: Violação de unicidade na segunda
    API-->>FE2: 409 Assento indisponível
    FE2->>API: GET /sessoes/{id}/assentos
    API-->>FE2: 200 Mapa com A7 ocupado
    FE2-->>C2: Mensagem "o assento A7 acabou de ser reservado" e mapa atualizado
```

## Notas de RNF

- **RNF01:** o banco decide o vencedor. A segunda reserva nunca é gravada.
- **RNF20:** a mensagem diz o que aconteceu e mostra o mapa atualizado, para o cliente escolher outro assento.
- **RNF34:** a regra de disponibilidade fica em serviço de reservas testável.
