# CineSenac — Sistema de Gestão de Sessões de Cinema

Sistema para gestão de sessões de cinema com três perfis de acesso: **Admin do Sistema**, **Gestor** e **Cliente**.

## Visão Geral

O CineSenac permite o cadastro e a administração de filmes, salas e sessões de cinema, além do gerenciamento do cadastro de clientes.

## Personas

| Persona | Descrição | Documento |
|---|---|---|
| Admin do Sistema | Acesso completo a todos os fluxos do sistema | [prd/personas/admin-sistema.md](prd/personas/admin-sistema.md) |
| Gestor | Cadastra salas, filmes e sessões | [prd/personas/gestor.md](prd/personas/gestor.md) |
| Cliente | Realiza o próprio cadastro (endereço, idade, e-mail) e reserva assentos em sessões | [prd/personas/cliente.md](prd/personas/cliente.md) |

## Modelagem de Dados

O modelo relacional está em [prd/dbdiagram.dbml](prd/dbdiagram.dbml), no formato DBML. Para visualizar o diagrama, importe o arquivo em [dbdiagram.io](https://dbdiagram.io/d).

**Entidades:** clientes (com endereço), filmes, salas, assentos, sessoes, reservas

## Requisitos Funcionais

Os requisitos funcionais estão documentados em [prd/requisitos-funcionais.md](prd/requisitos-funcionais.md), com matriz de rastreabilidade para as regras de negócio (RN01–RN04).

## Modelagens

As modelagens estão em [prd/modelagem](prd/modelagem/README.md), em duas visões:

- **Estática** ([componentes](prd/modelagem/estatica/componentes.md) e [classes](prd/modelagem/estatica/classes.md)): componentes agnósticos de tecnologia e entidades do domínio.
- **Dinâmica** ([índice](prd/modelagem/dinamica/README.md)): um diagrama de sequência por RF (RF01 a RF30), com os RNFs que cada fluxo realiza.

## Arquitetura

A arquitetura está em [prd/arquitetura/arquitetura.md](prd/arquitetura/arquitetura.md): estilo, drivers (ASRs), visão de implantação, mapa de táticas por atributo de qualidade e trade-offs. As decisões estão registradas como ADRs em [prd/arquitetura/adr](prd/arquitetura/adr/README.md), uma por tática (ADR-0001 a ADR-0020).

## Requisitos Não Funcionais

Os requisitos não funcionais (RNF01–RNF41) estão em [prd/requisitos-nao-funcionais.md](prd/requisitos-nao-funcionais.md), organizados nos oito eixos de qualidade da ISO/IEC 25010 (SWEBOK). Cada RNF está ligado aos RFs e às personas, com considerações de frontend e cenários para o teste controlado de 10.000 usuários.

## Fluxos de Sequência

Os principais fluxos do sistema estão documentados em UML de sequência (Mermaid) em [prd/fluxos-sequencia.md](prd/fluxos-sequencia.md): autenticação, cadastro do cliente, gestão de filmes/salas/sessões, reserva de assentos e administração.

## Implementação

Stack inicial, registrada na [ADR-0021](prd/arquitetura/adr/ADR-0021-stack-de-implementacao-inicial.md): Python 3.12, FastAPI (API `/v1` com OpenAPI), Jinja2 (páginas server-rendered), SQLAlchemy com SQLite e argon2 para senhas.

### Como executar

```bash
uv sync                                   # cria .venv e instala dependências
cp .env.example .env                      # defina CINESENAC_SECRET_KEY (32+ caracteres)
export CINESENAC_SECRET_KEY="..."         # ou carregue o .env no seu shell
uv run uvicorn app.main:criar_app --factory --reload
```

Primeiro administrador (a API exige um admin já autenticado):

```bash
uv run python -m app.cli criar-admin --email admin@exemplo.com
```

Em contêiner:

```bash
docker build -t cinesenac:dev .
docker run -p 8000:8000 -e CINESENAC_SECRET_KEY="..." -v cinesenac-dados:/data cinesenac:dev
```

### Testes

Duas camadas, ambas executadas pelo `pytest`:

- **Unitários e de integração** (`tests/test_*.py`): escritos antes do código (TDD). Cada teste cita o RF ou RNF que verifica.
- **BDD em Gherkin** (`features/*.feature`, executados com `pytest-bdd` a partir de `tests/bdd/`): cada cenário declara, numa linha `# Equivale a:`, os testes que descreve. `tests/bdd/test_cobertura_bdd.py` falha se um teste ficar sem cenário ou se um cenário apontar para um teste que não existe.
- **Contêiner** (`tests/container/`): sobe a imagem real com testcontainers. Requer Docker.

```bash
uv run pytest -m "not container"                     # unitários e BDD
uv run pytest -m "not container" --cov               # com cobertura
uv run python -m tests.bdd.gerar_relatorio           # relatório em prd/qualidade/
docker build -t cinesenac:dev . && CINESENAC_IMAGE=cinesenac:dev uv run pytest -m container
```

O relatório de cobertura está em [prd/qualidade/relatorio-cobertura.md](prd/qualidade/relatorio-cobertura.md). O pipeline de CI está em [.github/workflows/ci.yml](.github/workflows/ci.yml): um job roda os testes com gate de 85% de cobertura, e outro constrói a imagem e a verifica com testcontainers.

### Como a documentação guia o código

- Cada teste de regra cita o RF ou RNF que verifica.
- Concorrência (RNF01, RNF02) é testada com threads disputando o mesmo assento e os mesmos horários.
- Os cenários Gherkin repetem as verificações em linguagem de negócio, sem depender dos detalhes de implementação.
- Idempotência de reserva (RNF24), limite de tentativas (RNF30), degradação com 503 (RNF27), CSRF e cabeçalhos de segurança (RNF31) têm testes próprios.

## Estrutura do Projeto

```
cinesenac/
├── README.md
├── AGENTS.md
├── tutorial.md
├── pyproject.toml          # dependências (uv)
├── Dockerfile              # imagem da aplicação (ADR-0019)
├── .env.example            # variáveis CINESENAC_* documentadas (RNF40)
├── .aiox-core/             # framework AIOX (padrões, skills, workflows)
├── app/                    # código da aplicação
│   ├── main.py             # fábrica create_app: middlewares, rotas, erros
│   ├── config.py           # Settings a partir de CINESENAC_*
│   ├── db.py               # engine SQLite com BEGIN IMMEDIATE (ADR-0004)
│   ├── models.py           # modelo relacional (segue o DBML)
│   ├── permissoes.py       # permissões e perfis padrão (RF02, RF28)
│   ├── cli.py              # criar-admin
│   ├── dominio/regras.py   # regras puras: sobreposição, cota, assentos
│   ├── infra/              # cache TTL, limitação, admissão, senhas
│   ├── servicos/           # casos de uso (regras com efeito no banco)
│   ├── api/                # API v1: schemas, dependências, rotas
│   └── web/                # páginas Jinja2, templates e CSS
├── tests/                  # suíte TDD (pytest), BDD (pytest-bdd) e contêiner (testcontainers)
├── features/               # cenários Gherkin em português
├── .github/workflows/      # pipeline de CI (testes, cobertura, contêiner)
└── prd/                    # documentação: fonte de verdade
    ├── dbdiagram.dbml
    ├── requisitos-funcionais.md
    ├── requisitos-nao-funcionais.md
    ├── fluxos-sequencia.md
    ├── arquitetura/        # arquitetura e ADRs
    ├── modelagem/          # modelagens estáticas e dinâmicas
    └── personas/
```

## Roadmap

- [x] Definição de personas e objetivos
- [x] Requisitos funcionais
- [x] Requisitos não funcionais
- [x] Modelagem de dados
- [x] Fluxos (UML de sequência)
- [x] Modelagem estática e dinâmica
- [x] Arquitetura e ADRs (proposta)
- [x] Implementação inicial com testes (TDD)
- [ ] Desenvolvimento
