# RF02 — Controle de acesso por perfil

**Requisito:** restringir o acesso a cada funcionalidade conforme o perfil do usuário autenticado.
**Personas:** Todas.
**RNFs realizados:** [RNF29](../../requisitos-nao-funcionais.md) (autorização no servidor).
**Entidades:** Usuario, Perfil, Permissao ([classes](../estatica/classes.md)).

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor U as Usuário
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional

    U->>FE: Aciona uma funcionalidade
    FE->>API: Requisição com sessão
    API->>API: Valida a sessão
    alt Sessão inválida ou expirada
        API-->>FE: 401 Não autenticado
        FE-->>U: Redireciona para o login
    else Sessão válida
        API->>AUTZ: Verifica permissão da rota para o perfil
        AUTZ->>DB: Consulta permissões do perfil
        DB-->>AUTZ: Permissões
        alt Permissão concedida
            AUTZ-->>API: Autorizado
            API-->>FE: 200 Resultado
            FE-->>U: Exibe a funcionalidade
        else Permissão negada
            AUTZ-->>API: Negado
            API-->>FE: 403 Sem permissão
            FE-->>U: Mensagem de acesso negado
        end
    end
```

## Notas de RNF

- **RNF29:** a verificação acontece no servidor, em toda rota. O frontend esconder um botão não substitui essa checagem.
- A resposta 403 não revela dados da funcionalidade protegida.
