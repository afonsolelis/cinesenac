# RF08 — Cadastro de filme

**Requisito:** cadastrar filme com título, duração, gênero, sinopse, cartaz (URL), faixa etária, elenco e nacionalidade.
**Personas:** Gestor, Admin.
**RNFs realizados:** [RNF05](../../requisitos-nao-funcionais.md) (cota nacional, fica disponível para RF19), [RNF13](../../requisitos-nao-funcionais.md) (imagens), [RNF22](../../requisitos-nao-funcionais.md) (validação), [RNF31](../../requisitos-nao-funcionais.md) (URL e texto seguros), [RNF37](../../requisitos-nao-funcionais.md) (componente de formulário), [RNF41](../../requisitos-nao-funcionais.md) (migrações).
**Entidades:** Filme, FaixaEtaria, NacionalidadeFilme ([classes](../estatica/classes.md)).

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor G as Gestor
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional

    G->>FE: Preenche o formulário do filme
    FE->>FE: Valida campos obrigatórios e pré-visualiza o cartaz
    FE->>API: POST /filmes
    API->>AUTZ: Confirma perfil Gestor ou Admin
    alt Perfil sem permissão
        AUTZ-->>API: Negado
        API-->>FE: 403 Sem permissão
    else Perfil autorizado
        API->>API: Valida campos e aceita cartaz apenas com http ou https
        alt Dados inválidos
            API-->>FE: 400 Erros por campo
            FE-->>G: Destaca os campos com erro
        else Dados válidos
            API->>API: Sanitiza sinopse e elenco
            API->>DB: Insere filme
            DB-->>API: Filme criado
            API-->>FE: 201 Filme cadastrado
            FE-->>G: Atualiza o catálogo
        end
    end
```

## Notas de RNF

- **RNF31:** o cartaz precisa ser `http` ou `https`. Uma URL com `javascript:` é rejeitada na API, não só no frontend.
- **RNF22:** o formulário sinaliza os campos obrigatórios antes do envio. A API valida de novo.
- **RNF05:** a nacionalidade gravada aqui alimenta a cota de [RF18](RF18-indicador-cota-nacional.md) e a regra de [RF19](RF19-bloqueio-publicacao.md).
- **RNF13:** o cartaz é exibido como miniatura otimizada, com carregamento preguiçoso na lista.
- **RNF37:** o formulário do filme é componente reutilizável, com testes próprios.
- **RNF41:** os campos do filme vêm de migração versionada, derivada do DBML.
