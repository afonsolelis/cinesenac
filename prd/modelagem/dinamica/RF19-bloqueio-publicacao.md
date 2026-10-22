# RF19 — Bloqueio de publicação sem cota nacional

**Requisito:** impedir a publicação da programação de um dia sem ao menos uma sessão de filme nacional (RN04).
**Personas:** Gestor, Admin.
**RNFs realizados:** [RNF05](../../requisitos-nao-funcionais.md) (cota aplicada sempre), [RNF34](../../requisitos-nao-funcionais.md) (regra em camada testável).
**Entidades:** Sessao, Filme, NacionalidadeFilme ([classes](../estatica/classes.md)).

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor G as Gestor
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional

    G->>FE: Solicita publicação da programação do dia
    FE->>API: POST /programacao/{dia}/publicacao
    API->>AUTZ: Confirma perfil Gestor ou Admin
    alt Perfil sem permissão
        AUTZ-->>API: Negado
        API-->>FE: 403 Sem permissão
    else Perfil autorizado
        API->>DB: Conta sessões nacionais do dia
        DB-->>API: Quantidade
        alt Sem sessão nacional no dia
            API-->>FE: 422 Publicação bloqueada pela cota nacional
            FE-->>G: Alerta e sugestão de adicionar sessão nacional
        else Ao menos uma sessão nacional
            API->>DB: Marca a programação do dia como publicada
            DB-->>API: Publicação registrada
            API-->>FE: 200 Programação publicada
            FE-->>G: Confirmação de publicação
        end
    end
```

## Notas de RNF

- **RNF05:** a regra é aplicada no servidor, na publicação. O painel pode mostrar o alerta, mas não decide sozinho.
- **RNF34:** a regra de cota fica em serviço testável, o mesmo usado em [RF18](RF18-indicador-cota-nacional.md).
- Um 422 indica que a regra de negócio impediu a ação, e não que houve erro técnico.
