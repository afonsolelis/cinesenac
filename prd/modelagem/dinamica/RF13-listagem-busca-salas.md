# RF13 — Listagem e busca de salas

**Requisito:** listar e buscar salas.
**Personas:** Gestor, Admin.
**RNFs realizados:** [RNF06](../../requisitos-nao-funcionais.md) (latência de leitura), [RNF37](../../requisitos-nao-funcionais.md) (componente de listagem).
**Entidades:** Sala ([classes](../estatica/classes.md)).

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor G as Gestor
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional

    G->>FE: Abre a lista de salas ou digita busca
    FE->>API: GET /salas com termo e página
    API->>AUTZ: Confirma perfil Gestor ou Admin
    alt Perfil sem permissão
        AUTZ-->>API: Negado
        API-->>FE: 403 Sem permissão
    else Perfil autorizado
        API->>DB: Consulta salas por termo, paginadas
        DB-->>API: Página de salas
        API-->>FE: 200 Lista paginada
        FE-->>G: Exibe nome, capacidade e especificação
    end
```

## Notas de RNF

- **RNF06:** a lista é paginada, com resposta de tamanho limitado.
- **RNF37:** o componente de lista é o mesmo usado em [RF10](RF10-listagem-busca-filmes.md), com testes compartilhados.
