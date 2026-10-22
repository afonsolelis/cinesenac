# ADR-0021: Stack de implementação inicial em Python

**Status:** Proposta (aguarda aceite do [@architect](../../../.github/agents/architect.agent.md)). Implementada em código, com 156 testes passando e imagem de contêiner verificada.
**Data:** 2026-10-22
**Tática arquitetural:** Escolha de tecnologia que materializa as ADRs 0001 a 0020, sem contrariá-las
**RNFs:** [RNF35](../../requisitos-nao-funcionais.md), [RNF39](../../requisitos-nao-funcionais.md), [RNF40](../../requisitos-nao-funcionais.md)
**RFs:** todos
**Personas:** todas

---

## Contexto

A [arquitetura](../arquitetura.md) é agnóstica de tecnologia e deixou a escolha da stack como pendência. A implementação inicial precisa de uma stack concreta para começar com testes automatizados (TDD). Esta ADR registra essa escolha e os limites conhecidos dela, para que não sejam tratados como decisão final.

## Decisão

| Componente | Escolha | ADR que materializa |
|---|---|---|
| Linguagem e runtime | Python 3.12 | ADR-0001 |
| API HTTP versionada e OpenAPI | FastAPI, prefixo `/v1` | ADR-0002 |
| Páginas server-rendered | Jinja2 | ADR-0017 |
| Persistência e ORM | SQLAlchemy 2.x | ADR-0003, ADR-0005 |
| Banco da implementação inicial | SQLite (arquivo) | ADR-0003, ADR-0004 (ver limitações) |
| Hash de senha | argon2-cffi | ADR-0012 |
| Sessão | cookie assinado (`HttpOnly`, `SameSite=Lax`, `Secure` configurável) | ADR-0009, ADR-0012 |
| Cache de leitura | cache em memória com TTL de 30 s, atrás de interface | ADR-0007 |
| Limitação de taxa | contador em memória por IP e e-mail, atrás de interface | ADR-0010 |
| Idempotência | tabela de chaves por usuário | ADR-0006 |
| Auditoria | tabela gravada na mesma transação da ação | ADR-0015 |
| Configuração | variáveis de ambiente com prefixo `CINESENAC_` | ADR-0019 |
| Testes | pytest e cliente HTTP de teste | [requisitos](../../requisitos-funcionais.md) |

## Limitações conhecidas

1. **Instância única.** O SQLite em arquivo e os contadores em memória só funcionam com uma instância da aplicação. O [ADR-0009](ADR-0009-escalonamento-horizontal-sem-estado.md) exige estado compartilhado para escalar horizontalmente. Antes de qualquer escala, o banco precisa migrar para um servidor cliente-servidor, e o cache e a limitação de taxa precisam ser compartilhados.
2. **Bloqueio de escrita global.** No SQLite, cada transação de escrita começa com `BEGIN IMMEDIATE`, que serializa todos os escritores do banco. Isso é mais grosseiro que o bloqueio por recurso da [ADR-0004](ADR-0004-bloqueio-por-recurso-de-dominio.md). A correção é preservada, mas a vazão de escrita é limitada. O bloqueio por linha volta a valer com o banco cliente-servidor.
3. **Migrações.** A [ADR-0016](ADR-0016-migracoes-de-esquema-versionadas.md) pede migrações versionadas. Nesta entrega, o esquema é criado a partir dos modelos. Migrações versionadas entram antes da primeira versão para produção.
4. **Cache e limitação em memória.** Reiniciar a aplicação zera o cache e os contadores de tentativas. Isso enfraquece a proteção contra força bruta até a próxima reinicialização.

## Alternativas consideradas

- **Django:** traz administração, migrações e sessões prontas, mas o mapa de assentos e a API versionada ficam mais verbosos e a camada de domínio tende a se misturar com os modelos.
- **Flask:** simples e conhecido, porém exige montar à mão o contrato OpenAPI e a validação de entrada que o FastAPI já oferece (ADR-0002, ADR-0014).
- **PostgreSQL desde o início:** resolve as limitações 1 e 2, mas exige um servidor para cada execução de teste. A troca fica para quando o driver de banco for definido.

## Consequências

**Positivas:**

- Testes rodam sem infraestrutura externa, o que permite TDD rápido.
- Validação de entrada e OpenAPI saem do próprio framework.
- A camada de domínio fica isolada e testável (ADR-0001).

**Negativas e riscos:**

- As limitações acima precisam ser resolvidas antes de qualquer ambiente com mais de uma instância.
- A troca de SQLite para um banco cliente-servidor exige revisar as transações de escrita e os testes de concorrência.

## Relacionados

- [Arquitetura](../arquitetura.md)
- [ADR-0001](ADR-0001-estilo-monolito-modular-em-camadas.md) a [ADR-0020](ADR-0020-observabilidade-por-rota.md)

---

_Última atualização: 2026-10-22 | Rascunho para validação_
