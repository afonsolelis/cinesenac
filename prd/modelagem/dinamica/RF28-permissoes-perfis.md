# RF28 — Gestão de permissões dos perfis

**Requisito:** o Admin gerencia as permissões dos perfis de acesso.
**Personas:** Admin.
**RNFs realizados:** [RNF29](../../requisitos-nao-funcionais.md) (autorização no servidor), [RNF33](../../requisitos-nao-funcionais.md) (auditoria).
**Entidades:** Perfil, Permissao, RegistroAuditoria ([classes](../estatica/classes.md)). Todas são **pendentes**.

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor A as Admin
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional
    participant AUD as Auditoria

    A->>FE: Abre permissões de um perfil
    FE->>API: GET /perfis/{id}/permissoes
    API->>AUTZ: Confirma perfil Admin
    alt Perfil sem permissão
        AUTZ-->>API: Negado
        API-->>FE: 403 Sem permissão
    else Perfil Admin
        API->>DB: Consulta permissões do perfil
        DB-->>API: Permissões atuais
        API-->>FE: 200 Permissões
        FE-->>A: Exibe as permissões marcáveis

        A->>FE: Marca ou desmarca permissões e salva
        FE->>API: PUT /perfis/{id}/permissoes
        API->>AUTZ: Confirma perfil Admin
        API->>DB: Substitui permissões do perfil em transação
        DB-->>API: Confirmação
        API->>AUD: Registra alteração de permissões
        API-->>FE: 200 Permissões atualizadas
        FE-->>A: Confirmação
    end
```

## Notas de RNF

- **RNF29:** a alteração de permissões é a própria regra de autorização. Só o Admin a faz, e o servidor confirma em toda chamada.
- **RNF33:** a alteração grava quem mudou, o perfil, as permissões anteriores e as novas.
- Depois da alteração, a autorização de [RF02](RF02-controle-de-acesso.md) passa a usar as permissões novas, sem esperar a sessão expirar.
