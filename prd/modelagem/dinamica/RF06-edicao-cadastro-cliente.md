# RF06 — Edição do cadastro do cliente

**Requisito:** o cliente edita os próprios dados de cadastro (endereço, idade e e-mail).
**Personas:** Cliente.
**RNFs realizados:** [RNF03](../../requisitos-nao-funcionais.md) (unicidade ao trocar e-mail), [RNF29](../../requisitos-nao-funcionais.md) (autorização por titularidade), [RNF31](../../requisitos-nao-funcionais.md) (saneamento), [RNF32](../../requisitos-nao-funcionais.md) (LGPD).
**Entidades:** Cliente, Endereco, Usuario ([classes](../estatica/classes.md)).

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor C as Cliente
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional

    C->>FE: Altera endereço, idade ou e-mail
    FE->>API: PATCH /clientes/{id}
    API->>AUTZ: Confirma que o cliente é o titular do cadastro
    alt Cadastro de outro titular
        AUTZ-->>API: Negado
        API-->>FE: 403 Sem permissão
        FE-->>C: Acesso negado
    else Titular confirmado
        API->>API: Valida campos e sanitiza textos
        API->>DB: Atualiza cliente em transação
        alt Novo e-mail já existe
            DB-->>API: Violação de unicidade
            API-->>FE: 409 E-mail já cadastrado
            FE-->>C: Mantém os dados e pede outro e-mail
        else Atualização concluída
            DB-->>API: Registro atualizado
            API-->>FE: 200 Cadastro atualizado
            FE-->>C: Confirmação das alterações
        end
    end
```

## Notas de RNF

- **RNF29:** o `{id}` da rota não basta. O servidor confirma que a sessão é do titular, para impedir alteração de outro cadastro.
- **RNF03:** trocar e-mail passa pela mesma restrição única do cadastro.
- **RNF32:** a exibição dos dados após a edição fica restrita ao titular.
- **RNF31:** nome, endereço e demais textos editados passam pelo mesmo saneamento do cadastro.
