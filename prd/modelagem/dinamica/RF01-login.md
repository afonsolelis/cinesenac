# RF01 — Login por perfil

**Requisito:** login de Admin, Gestor e Cliente com e-mail e senha, exibindo o painel conforme o perfil.
**Personas:** Todas.
**RNFs realizados:** [RNF28](../../requisitos-nao-funcionais.md) (autenticação segura), [RNF30](../../requisitos-nao-funcionais.md) (força bruta).
**Entidades:** Usuario, Perfil, Cliente ([classes](../estatica/classes.md)).

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor U as Usuário
    participant FE as Frontend
    participant LIM as Limitador de tentativas
    participant API as API
    participant DB as Banco relacional

    U->>FE: Informa e-mail e senha
    FE->>API: POST /autenticacao
    API->>LIM: Verifica tentativas por e-mail e IP
    alt Acima do limite
        LIM-->>API: Bloqueado
        API-->>FE: 429 Muitas tentativas
        FE-->>U: Aguarde antes de tentar de novo
    else Dentro do limite
        API->>DB: Busca usuário ativo por e-mail
        DB-->>API: Usuário e hash da senha
        alt Senha confere
            API->>API: Verifica hash adaptativo
            API-->>FE: Sessão com perfil (cookie HttpOnly)
            FE-->>U: Exibe painel do perfil
        else Credenciais inválidas
            API->>LIM: Registra falha
            API-->>FE: 401 Não autorizado
            FE-->>U: Mensagem genérica de erro
        end
    end
```

## Notas de RNF

- **RNF28:** a senha é comparada por hash adaptativo, nunca em texto claro. A sessão é emitida com expiração por inatividade.
- **RNF30:** o limitador conta falhas por e-mail e por IP. Acima do limite, a API responde 429 sem consultar o banco.
- A mensagem de erro é genérica, para não revelar se o e-mail existe.
