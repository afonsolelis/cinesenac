# RF04 — Cadastro do cliente

**Requisito:** o cliente cria a própria conta com nome, e-mail, idade e endereço.
**Personas:** Cliente.
**RNFs realizados:** [RNF03](../../requisitos-nao-funcionais.md) (unicidade sob concorrência), [RNF22](../../requisitos-nao-funcionais.md) (validação de formulário), [RNF31](../../requisitos-nao-funcionais.md) (saneamento), [RNF32](../../requisitos-nao-funcionais.md) (LGPD), [RNF41](../../requisitos-nao-funcionais.md) (migrações).
**Entidades:** Cliente, Endereco, Usuario ([classes](../estatica/classes.md)).

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor C as Cliente
    participant FE as Frontend
    participant API as API
    participant DB as Banco relacional

    C->>FE: Preenche nome, e-mail, idade e endereço
    FE->>FE: Valida campos obrigatórios antes do envio
    alt Campos inválidos
        FE-->>C: Erros exibidos nos campos, sem perder os dados
    else Campos válidos
        FE->>API: POST /clientes
        API->>API: Valida formato e sanitiza textos livres
        API->>DB: Inicia transação e insere cliente com e-mail
        alt E-mail já existe (restrição única)
            DB-->>API: Violação de unicidade
            API-->>FE: 409 E-mail já cadastrado
            FE-->>C: Pede outro e-mail
        else Inserção concluída
            DB-->>API: Cliente criado
            API-->>FE: 201 Cadastro realizado
            FE-->>C: Confirmação e acesso à área do cliente
        end
    end
```

## Notas de RNF

- **RNF03:** a unicidade do e-mail é garantida pela restrição do banco, não só pela checagem prévia. Dois cadastros simultâneos não criam duas contas.
- **RNF22:** o frontend valida antes do envio e mantém os dados digitados quando há erro.
- **RNF31:** a API sanitiza campos livres e não confia na validação do cliente.
- **RNF32:** só os dados necessários são coletados, com finalidade declarada.
- **RNF41:** a tabela de clientes e o endereço vêm de migração versionada, sem alteração manual no banco.
