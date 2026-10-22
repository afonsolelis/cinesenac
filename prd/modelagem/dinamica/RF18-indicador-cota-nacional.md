# RF18 — Indicador da cota nacional

**Requisito:** exibir ao Gestor o indicador da cota de filme nacional do dia (RN04).
**Personas:** Gestor, Admin.
**RNFs realizados:** [RNF05](../../requisitos-nao-funcionais.md) (cota aplicada), [RNF34](../../requisitos-nao-funcionais.md) (regra em camada testável).
**Entidades:** Sessao, Filme, NacionalidadeFilme ([classes](../estatica/classes.md)).

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor G as Gestor
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional

    G->>FE: Abre o painel de programação do dia
    FE->>API: GET /programacao/{dia}/cota-nacional
    API->>AUTZ: Confirma perfil Gestor ou Admin
    alt Perfil sem permissão
        AUTZ-->>API: Negado
        API-->>FE: 403 Sem permissão
    else Perfil autorizado
        API->>DB: Conta sessões do dia de filmes nacionais
        DB-->>API: Quantidade
        API->>API: Calcula se a cota está atendida
        API-->>FE: 200 Cota atendida ou pendente
        alt Cota pendente
            FE-->>G: Indicador de alerta com a cota do dia
        else Cota atendida
            FE-->>G: Indicador de cota atendida
        end
    end
```

## Notas de RNF

- **RNF05:** o indicador usa a mesma regra da publicação em [RF19](RF19-bloqueio-publicacao.md). Não há duas definições de cota.
- **RNF34:** a regra de cálculo fica em serviço testável, separada da interface.
- A consulta é do dia da programação, e a nacionalidade vem do cadastro do filme ([RF08](RF08-cadastro-filme.md)).
