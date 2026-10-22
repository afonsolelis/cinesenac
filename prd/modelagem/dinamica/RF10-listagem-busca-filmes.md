# RF10 — Listagem e busca de filmes

**Requisito:** listar e buscar filmes do catálogo.
**Personas:** Gestor, Admin.
**RNFs realizados:** [RNF06](../../requisitos-nao-funcionais.md) (latência de leitura), [RNF13](../../requisitos-nao-funcionais.md) (imagens), [RNF37](../../requisitos-nao-funcionais.md) (componente de listagem).
**Entidades:** Filme ([classes](../estatica/classes.md)).

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor G as Gestor
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional

    G->>FE: Digita termo de busca e filtros
    FE->>API: GET /filmes com termo e página
    API->>AUTZ: Confirma perfil Gestor ou Admin
    alt Perfil sem permissão
        AUTZ-->>API: Negado
        API-->>FE: 403 Sem permissão
    else Perfil autorizado
        API->>DB: Consulta filmes por termo, paginados
        DB-->>API: Página de filmes
        API-->>FE: 200 Lista paginada
        FE-->>G: Exibe a lista e as miniaturas sob demanda
    end
```

## Notas de RNF

- **RNF06:** a busca usa paginação, para que a resposta tenha tamanho limitado independentemente do tamanho do catálogo.
- **RNF13:** as miniaturas são carregadas conforme a lista aparece na tela.
- **RNF37:** a listagem e o campo de busca são componentes reutilizáveis, com testes próprios.
