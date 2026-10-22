# RF11 — Cadastro de sala

**Requisito:** cadastrar sala com quantidade de assentos, horário de funcionamento e especificação técnica.
**Personas:** Gestor, Admin.
**RNFs realizados:** [RNF22](../../requisitos-nao-funcionais.md) (validação), [RNF37](../../requisitos-nao-funcionais.md) (componente de formulário), [RNF41](../../requisitos-nao-funcionais.md) (esquema e migrações).
**Entidades:** Sala, Assento ([classes](../estatica/classes.md)).

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor G as Gestor
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional

    G->>FE: Preenche quantidade de assentos, horário e especificação
    FE->>FE: Valida campos obrigatórios antes do envio
    FE->>API: POST /salas
    API->>AUTZ: Confirma perfil Gestor ou Admin
    alt Perfil sem permissão
        AUTZ-->>API: Negado
        API-->>FE: 403 Sem permissão
    else Perfil autorizado
        API->>API: Valida quantidade e horário de funcionamento
        alt Dados inválidos
            API-->>FE: 400 Erros por campo
            FE-->>G: Destaca os campos com erro
        else Dados válidos
            API->>DB: Inicia transação
            API->>DB: Insere sala
            API->>DB: Gera assentos de A1 até o total informado
            alt Falha na geração de assentos
                DB-->>API: Erro
                API->>DB: Desfaz a transação
                API-->>FE: 500 Sala não criada
            else Sala e assentos gravados
                API->>DB: Confirma transação
                API-->>FE: 201 Sala cadastrada
                FE-->>G: Atualiza a lista de salas
            end
        end
    end
```

## Notas de RNF

- **RNF41:** a sala e seus assentos são criados na mesma transação. Não existe sala sem assentos.
- **RNF22:** o formulário valida antes do envio, e a API valida de novo.
- Os assentos são gerados por código único dentro da sala, o que sustenta a restrição `(sala, codigo)` de [classes](../estatica/classes.md).
- **RNF37:** o formulário de sala é componente reutilizável, com testes próprios.
