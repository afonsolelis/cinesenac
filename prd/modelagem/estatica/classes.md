# Diagrama de Classes — Entidades do CineSenac

**Tipo:** modelagem estática
**Status:** Rascunho para validação
**Relacionado:** [componentes.md](componentes.md) · [dbdiagram.dbml](../../dbdiagram.dbml) · [requisitos-funcionais.md](../../requisitos-funcionais.md)

Diagrama de classes que delimita as **entidades** do domínio. Os tipos são genéricos (`inteiro`, `texto`, `datahora`, `decimal`, `booleano`, `data`), sem tecnologia de banco ou linguagem.

Entidades marcadas com **(pendente)** não existem no [dbdiagram.dbml](../../dbdiagram.dbml) atual. São exigidas pelos RF27, RF28 e RNF33 e precisam de confirmação antes de virar tabela.

---

## Diagrama

```mermaid
classDiagram
    class Cliente {
        +id inteiro
        +nome texto
        +email texto
        +idade inteiro
        +criado_em datahora
    }

    class Endereco {
        <<Valor>>
        +logradouro texto
        +numero texto
        +complemento texto
        +bairro texto
        +cidade texto
        +estado texto
        +cep texto
    }

    class Usuario {
        <<pendente>>
        +id inteiro
        +email texto
        +senha_hash texto
        +ativo booleano
    }

    class Perfil {
        <<pendente>>
        +id inteiro
        +nome texto
    }

    class Permissao {
        <<pendente>>
        +id inteiro
        +codigo texto
    }

    class RegistroAuditoria {
        <<pendente>>
        +id inteiro
        +acao texto
        +alvo texto
        +ocorrido_em datahora
    }

    class Filme {
        +id inteiro
        +titulo texto
        +duracao_minutos inteiro
        +genero texto
        +sinopse texto
        +cartaz_url texto
        +elenco texto
        +criado_em datahora
    }

    class FaixaEtaria {
        <<enumeração>>
        LIVRE
        DEZ_ANOS
        DOZE_ANOS
        QUATORZE_ANOS
        DEZESSEIS_ANOS
        DEZOITO_ANOS
    }

    class NacionalidadeFilme {
        <<enumeração>>
        NACIONAL
        INTERNACIONAL
    }

    class Sala {
        +id inteiro
        +nome texto
        +qtd_assentos inteiro
        +hora_abertura hora
        +hora_fechamento hora
        +especificacao_tecnica texto
        +criado_em datahora
    }

    class Assento {
        +id inteiro
        +codigo texto
    }

    class Sessao {
        +id inteiro
        +data_hora_inicio datahora
        +duracao_minutos inteiro
        +valor_ingresso decimal
        +criado_em datahora
    }

    class Reserva {
        +id inteiro
        +criado_em datahora
    }

    Cliente "1" *-- "1" Endereco : possui
    Cliente "1" -- "1" Usuario : autentica-se com
    Usuario "*" -- "*" Perfil : tem
    Perfil "*" -- "*" Permissao : concede
    Usuario "1" --> "*" RegistroAuditoria : autor de

    Sala "1" *-- "*" Assento : contém
    Filme --> FaixaEtaria : classificado por
    Filme --> NacionalidadeFilme : origem
    Sessao "*" --> "1" Filme : exibe
    Sessao "*" --> "1" Sala : ocorre em

    Reserva "*" --> "1" Cliente : feita por
    Reserva "*" --> "1" Sessao : para
    Reserva "*" --> "1" Assento : ocupa
```

---

## Restrições de unicidade e integridade

| Entidade | Restrição | Regra | RFs | RNFs |
|---|---|---|---|---|
| Cliente | `email` único | Um e-mail por conta. | RF05 | RNF03 |
| Assento | `(sala, codigo)` único | Código de assento único dentro da sala. | RF11 | RNF41 |
| Sessao | Sem sobreposição na mesma `Sala` | Intervalo `[data_hora_inicio, início + duração)` não se cruza com outra sessão da sala. Validado com bloqueio por sala. | RF15 | RNF04 |
| Reserva | `(sessao, assento)` único | Um assento só é reservado uma vez por sessão. | RF23 | RNF01 |
| Reserva | Sem sobreposição por `Cliente` | Um cliente não reserva sessões com horários conflitantes. Validado com bloqueio por cliente. | RF24 | RNF02 |
| Reserva | Atomicidade | Reservas de múltiplos assentos são gravadas juntas ou não são gravadas. | RF22 | RNF25 |
| Filme | Cota nacional | Todo dia publicado precisa de ao menos uma sessão de filme `NACIONAL`. Validada na publicação. | RF18, RF19 | RNF05 |

---

## Mapeamento para o DBML atual

| Classe | Tabela no DBML | Situação |
|---|---|---|
| Cliente + Endereco | `clientes` | Endereço incorporado na mesma tabela (relação 1:1), como no DBML. |
| Filme | `filmes` | Conforme. |
| Sala | `salas` | Conforme. |
| Assento | `assentos` | Conforme. |
| Sessao | `sessoes` | Conforme. |
| Reserva | `reservas` | Conforme. |
| FaixaEtaria, NacionalidadeFilme | `enum faixa_etaria`, `enum nacionalidade_filme` | Conforme. |
| Usuario, Perfil, Permissao | Não existe | **Pendente.** Necessário para RF01, RF02, RF27 e RF28. |
| RegistroAuditoria | Não existe | **Pendente.** Necessário para RNF33. |

> Ponto de atenção: `Cliente` e `Usuario` são separados para que o login de Gestor e Admin use a mesma estrutura de credenciais. Se o time preferir que `Cliente` contenha as credenciais, a relação `1..1` deixa de existir, mas a regra de login continua a mesma.
