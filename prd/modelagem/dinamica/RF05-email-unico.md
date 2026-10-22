# RF05 — E-mail único

**Requisito:** validar que o e-mail do cliente é único no sistema.
**Personas:** Cliente, Admin.
**RNFs realizados:** [RNF03](../../requisitos-nao-funcionais.md) (unicidade sob concorrência), [RNF20](../../requisitos-nao-funcionais.md) (mensagem clara de conflito).
**Entidades:** Cliente ([classes](../estatica/classes.md)).

## Diagrama de sequência

Este diagrama mostra a corrida entre dois cadastros com o mesmo e-mail. O caminho principal de cadastro está em [RF04](RF04-cadastro-cliente.md).

```mermaid
sequenceDiagram
    actor C1 as Cliente A
    actor C2 as Cliente B
    participant FE as Frontend
    participant API as API
    participant DB as Banco relacional

    par Dois cadastros simultâneos com o mesmo e-mail
        C1->>FE: Envia cadastro com e-mail X
        FE->>API: POST /clientes
        API->>DB: Insere cliente com e-mail X
    and
        C2->>FE: Envia cadastro com e-mail X
        FE->>API: POST /clientes
        API->>DB: Insere cliente com e-mail X
    end
    DB-->>API: Primeiro commit concluído
    API-->>FE: 201 Cadastro realizado
    FE-->>C1: Confirmação
    DB-->>API: Violação de unicidade no segundo
    API-->>FE: 409 E-mail já cadastrado
    FE-->>C2: Mensagem pedindo outro e-mail
```

## Notas de RNF

- **RNF03:** a restrição única do banco decide o vencedor. Não há janela entre a checagem e a inserção que permita duplicidade.
- **RNF20:** o 409 vira mensagem específica, com a ação sugerida (trocar o e-mail ou recuperar a conta).
