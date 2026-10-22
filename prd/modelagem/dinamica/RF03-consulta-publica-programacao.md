# RF03 — Consulta pública da programação

**Requisito:** usuários não autenticados consultam filmes em cartaz e sessões disponíveis.
**Personas:** Visitante.
**RNFs realizados:** [RNF06](../../requisitos-nao-funcionais.md) (latência de leitura), [RNF08](../../requisitos-nao-funcionais.md) (vazão), [RNF09](../../requisitos-nao-funcionais.md) (LCP), [RNF11](../../requisitos-nao-funcionais.md) (CLS), [RNF12](../../requisitos-nao-funcionais.md) (bundle), [RNF13](../../requisitos-nao-funcionais.md) (imagens), [RNF14](../../requisitos-nao-funcionais.md) (cache), [RNF27](../../requisitos-nao-funcionais.md) (degradação).
**Entidades:** Filme, Sala, Sessao ([classes](../estatica/classes.md)).

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor V as Visitante
    participant FE as Frontend
    participant CDN as Distribuição de conteúdo
    participant CACHE as Cache de leitura
    participant API as API
    participant DB as Banco relacional

    V->>FE: Abre a programação
    FE->>CDN: GET programação pública
    alt Resposta em cache dentro do TTL
        CDN-->>FE: 200 Programação
    else Sem cache válido
        CDN->>API: Encaminha leitura
        API->>CACHE: Consulta chave da programação
        alt Chave presente
            CACHE-->>API: Programação
        else Chave ausente
            API->>DB: Consulta sessões e filmes publicados
            DB-->>API: Resultados
            API->>CACHE: Grava com TTL de 30 s
        end
        alt Sistema saturado
            API-->>CDN: 503 com Retry-After
            CDN-->>FE: 503 com Retry-After
            FE-->>V: Tente novamente em instantes
        else Dentro da capacidade
            API-->>CDN: 200 Programação
            CDN-->>FE: 200 Programação
        end
    end
    FE-->>V: Exibe filmes e sessões com imagens sob demanda
```

## Notas de RNF

- **RNF14:** a leitura pública passa por cache com TTL de 30 s. Isso tira a maior parte da carga de C1 do banco.
- **RNF06 e RNF08:** a leitura do cache é a caminho rápido que sustenta a carga de 10.000 usuários.
- **RNF27:** em saturação, a resposta traz `Retry-After` e a interface mostra mensagem, sem tela em branco.
- **RNF09, RNF11, RNF12 e RNF13:** tratados no frontend, com imagens de tamanho responsivo e carregamento preguiçoso.
