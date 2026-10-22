# RF12 — Edição e exclusão de sala

**Requisito:** editar e excluir salas.
**Personas:** Gestor, Admin.
**RNFs realizados:** [RNF29](../../requisitos-nao-funcionais.md) (autorização), [RNF37](../../requisitos-nao-funcionais.md) (componente de formulário).
**Entidades:** Sala, Assento, Sessao ([classes](../estatica/classes.md)).

## Diagrama de sequência

A exclusão de sala com sessões futuras ainda não tem regra definida no RF12. O diagrama marca esse ponto como **a definir**.

```mermaid
sequenceDiagram
    actor G as Gestor
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional

    G->>FE: Altera dados da sala ou pede exclusão
    FE->>API: PATCH /salas/{id} ou DELETE /salas/{id}
    API->>AUTZ: Confirma perfil Gestor ou Admin
    alt Perfil sem permissão
        AUTZ-->>API: Negado
        API-->>FE: 403 Sem permissão
    else Perfil autorizado
        alt Edição
            API->>DB: Atualiza sala
            alt Quantidade de assentos mudou
                Note over API,DB: Regra a definir para assentos já reservados
            end
            DB-->>API: Sala atualizada
            API-->>FE: 200 Sala atualizada
        else Exclusão
            API->>DB: Consulta sessões futuras da sala
            DB-->>API: Quantidade de sessões
            alt Sem sessões futuras
                API->>DB: Remove sala e assentos
                API-->>FE: 200 Sala excluída
            else Com sessões futuras
                Note over API,DB: Regra a definir (bloquear ou cancelar sessões)
                API-->>FE: 409 Sala possui sessões futuras
            end
        end
        FE-->>G: Atualiza a lista de salas
    end
```

## Notas de RNF

- **RNF29:** as rotas de edição e exclusão checam perfil no servidor.
- **Pendência:** definir o que acontece com assentos já reservados se a quantidade mudar, e com sessões futuras na exclusão. Isso afeta [RNF01](../../requisitos-nao-funcionais.md) e [RF16](RF16-edicao-cancelamento-sessao.md).
- **RNF37:** o formulário de edição é o mesmo componente do cadastro de sala.
