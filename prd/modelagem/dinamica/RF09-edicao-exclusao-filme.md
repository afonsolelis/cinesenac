# RF09 — Edição e exclusão de filme

**Requisito:** editar e excluir filmes do catálogo.
**Personas:** Gestor, Admin.
**RNFs realizados:** [RNF13](../../requisitos-nao-funcionais.md) (imagens), [RNF29](../../requisitos-nao-funcionais.md) (autorização), [RNF31](../../requisitos-nao-funcionais.md) (URL e texto seguros), [RNF37](../../requisitos-nao-funcionais.md) (componente de formulário).
**Entidades:** Filme, Sessao ([classes](../estatica/classes.md)).

## Diagrama de sequência

A exclusão de filme que já tem sessões vinculadas ainda não tem regra definida no RF09. O diagrama marca esse ponto como **a definir**.

```mermaid
sequenceDiagram
    actor G as Gestor
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional

    G->>FE: Abre um filme e altera dados ou pede exclusão
    FE->>API: PATCH /filmes/{id} ou DELETE /filmes/{id}
    API->>AUTZ: Confirma perfil Gestor ou Admin
    alt Perfil sem permissão
        AUTZ-->>API: Negado
        API-->>FE: 403 Sem permissão
    else Perfil autorizado
        API->>API: Valida campos e aceita cartaz apenas com http ou https
        alt Edição
            API->>DB: Atualiza filme
            DB-->>API: Filme atualizado
            API-->>FE: 200 Filme atualizado
        else Exclusão
            API->>DB: Consulta sessões vinculadas ao filme
            DB-->>API: Quantidade de sessões
            alt Sem sessões vinculadas
                API->>DB: Remove filme
                API-->>FE: 200 Filme excluído
            else Com sessões vinculadas
                Note over API,DB: Regra a definir (bloquear ou cancelar sessões)
                API-->>FE: 409 Filme possui sessões
            end
        end
        FE-->>G: Atualiza o catálogo
    end
```

## Notas de RNF

- **RNF29:** a rota de exclusão tem a mesma checagem de perfil que a de criação.
- **RNF31:** a edição de cartaz e sinopse passa pelas mesmas validações de [RF08](RF08-cadastro-filme.md).
- **Pendência:** definir se exclusão com sessões vinculadas bloqueia a operação ou cancela as sessões. Isso afeta [RF16](RF16-edicao-cancelamento-sessao.md) e [RNF33](../../requisitos-nao-funcionais.md).
- **RNF13:** a troca de cartaz segue as mesmas regras de imagem do cadastro.
- **RNF37:** o formulário de edição é o mesmo componente do cadastro.
