# RF17 — Consulta da programação com filtros

**Requisito:** consultar a programação filtrando por sala, filme ou período.
**Personas:** Visitante, Cliente, Gestor, Admin.
**RNFs realizados:** [RNF06](../../requisitos-nao-funcionais.md) (latência), [RNF08](../../requisitos-nao-funcionais.md) (vazão), [RNF09](../../requisitos-nao-funcionais.md) (LCP), [RNF11](../../requisitos-nao-funcionais.md) (CLS), [RNF12](../../requisitos-nao-funcionais.md) (bundle), [RNF14](../../requisitos-nao-funcionais.md) (cache), [RNF27](../../requisitos-nao-funcionais.md) (degradação).
**Entidades:** Sessao, Filme, Sala ([classes](../estatica/classes.md)).

## Diagrama de sequência

Os filtros entram na chave de cache, então cada combinação de filtros tem sua própria entrada com TTL.

```mermaid
sequenceDiagram
    actor U as Usuário
    participant FE as Frontend
    participant CDN as Distribuição de conteúdo
    participant CACHE as Cache de leitura
    participant API as API
    participant DB as Banco relacional

    U->>FE: Escolhe sala, filme ou período
    FE->>CDN: GET programação com filtros
    alt Resposta em cache para estes filtros
        CDN-->>FE: 200 Programação filtrada
    else Sem cache válido
        CDN->>API: Encaminha leitura com filtros
        API->>CACHE: Consulta chave dos filtros
        alt Chave presente
            CACHE-->>API: Programação
        else Chave ausente
            API->>DB: Consulta sessões pelos filtros
            DB-->>API: Resultados
            API->>CACHE: Grava com TTL de 30 s
        end
        alt Sistema saturado
            API-->>CDN: 503 com Retry-After
            CDN-->>FE: 503 com Retry-After
            FE-->>U: Tente novamente em instantes
        else Dentro da capacidade
            API-->>CDN: 200 Programação filtrada
            CDN-->>FE: 200 Programação filtrada
        end
    end
    FE-->>U: Exibe as sessões filtradas
```

## Notas de RNF

- **RNF14:** a chave de cache inclui os filtros. O TTL de 30 s limita a defasagem da programação.
- **RNF27:** em saturação, a resposta traz `Retry-After` e a interface mostra mensagem.
- Usuários autenticados seguem o mesmo caminho. Nenhuma informação pessoal entra na resposta pública.
- **RNF06:** a leitura filtrada usa índices por sala, filme e período, para manter a resposta abaixo de 300 ms.
- **RNF08:** o cache absorve a repetição de filtros comuns, reduzindo a carga sobre o banco.
- **RNF09, RNF11 e RNF12:** tratados no frontend, como em [RF03](RF03-consulta-publica-programacao.md).
