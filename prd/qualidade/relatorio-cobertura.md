# Relatório de cobertura de testes — CineSenac

**Gerado em:** 2026-10-22  
**Gerado por:** `python -m tests.bdd.gerar_relatorio` (ver [README](../../README.md#testes))

## Resumo

| Indicador | Valor |
|---|---:|
| Cobertura de linhas e ramos (`app/`) | **91.1%** |
| Linhas cobertas | 1197 de 1290 |
| Ramos cobertos | 179 de 220 |
| Testes unitários e de integração (pytest) | 156 |
| Testes com cenário Gherkin equivalente | 156 de 156 (100%) |
| Testes sem cenário BDD | 0 |
| Mapeamentos BDD apontando para teste inexistente | 0 |

A cobertura de testes é o mapeamento entre testes e cenários: cada teste existente tem
um cenário Gherkin que o descreve, e o teste `tests/bdd/test_cobertura_bdd.py` falha se
algum deles ficar sem cenário ou se um cenário apontar para um teste que não existe.

## Cobertura de código por módulo

| Módulo | Linhas | Cobertas | Ramos | Cobertura | Linhas sem cobertura |
|---|---:|---:|---:|---:|---|
| `app/__init__.py` | 0 | 0 | 0/0 | 100% | — |
| `app/api/__init__.py` | 0 | 0 | 0/0 | 100% | — |
| `app/api/deps.py` | 48 | 48 | 14/14 | 100% | — |
| `app/api/schemas.py` | 96 | 94 | 3/4 | 97% | 17, 91 |
| `app/api/v1.py` | 164 | 160 | 8/10 | 97% | 147, 148, 164, 214 |
| `app/cli.py` | 27 | 12 | 1/2 | 45% | 19, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31 … |
| `app/config.py` | 25 | 25 | 4/4 | 100% | — |
| `app/db.py` | 19 | 19 | 1/2 | 95% | — |
| `app/dominio/__init__.py` | 0 | 0 | 0/0 | 100% | — |
| `app/dominio/regras.py` | 14 | 14 | 2/2 | 100% | — |
| `app/erros.py` | 15 | 15 | 0/0 | 100% | — |
| `app/infra/__init__.py` | 0 | 0 | 0/0 | 100% | — |
| `app/infra/admissao.py` | 15 | 15 | 2/2 | 100% | — |
| `app/infra/cache.py` | 25 | 25 | 4/4 | 100% | — |
| `app/infra/limitacao.py` | 26 | 26 | 2/2 | 100% | — |
| `app/infra/seguranca.py` | 10 | 10 | 0/0 | 100% | — |
| `app/main.py` | 77 | 75 | 9/10 | 97% | 112, 114 |
| `app/models.py` | 110 | 110 | 0/0 | 100% | — |
| `app/permissoes.py` | 13 | 13 | 0/0 | 100% | — |
| `app/servicos/__init__.py` | 0 | 0 | 0/0 | 100% | — |
| `app/servicos/admin.py` | 82 | 77 | 22/30 | 88% | 25, 81, 91, 94, 140 |
| `app/servicos/auditoria.py` | 3 | 3 | 0/0 | 100% | — |
| `app/servicos/autenticacao.py` | 15 | 15 | 6/6 | 100% | — |
| `app/servicos/catalogo.py` | 97 | 92 | 25/32 | 91% | 45, 81, 99, 100, 114 |
| `app/servicos/clientes.py` | 41 | 36 | 10/18 | 78% | 50, 54, 55, 56, 76 |
| `app/servicos/programacao.py` | 100 | 96 | 33/38 | 93% | 44, 50, 69, 98 |
| `app/servicos/reservas.py` | 68 | 62 | 17/20 | 90% | 53, 76, 77, 78, 90, 105 |
| `app/servicos/usuarios.py` | 41 | 36 | 12/14 | 87% | 20, 32, 41, 42, 43 |
| `app/web/__init__.py` | 0 | 0 | 0/0 | 100% | — |
| `app/web/routes.py` | 159 | 119 | 4/6 | 75% | 98, 99, 100, 150, 153, 158, 159, 160, 203, 204, 205, 208 … |

## Lacunas conhecidas

Os módulos abaixo ficam abaixo de 85% de cobertura de linhas e ramos. As lacunas são
reais e não foram escondidas.

- `app/cli.py`
- `app/servicos/clientes.py`
- `app/web/routes.py`

Principais lacunas de `app/web/routes.py`: formulários de criação e publicação do gestor
(`/gestor/filmes`, `/gestor/sessoes`, `/gestor/publicar`), formulários do admin
(`/admin/usuarios`, `/admin/usuarios/{id}/ativo`) e os caminhos de erro desses formulários.
Os serviços de `catalogo`, `programacao`, `clientes` e `reservas` também têm ramos de
validação não exercitados por cenários. A `app/cli.py` (`main`) não tem teste porque lê a
senha do terminal.

## Testes de contêiner

Os testes em `tests/container/` sobem a imagem de contêiner com testcontainers. Eles
verificam healthcheck, vitrine com cabeçalhos de segurança, arquivos estáticos, contrato
da API e que o processo não roda como root. Não entram na cobertura de linhas, porque o
código medido roda dentro do contêiner.

## Como reproduzir

```bash
uv sync
uv run pytest -m "not container" --cov --cov-report=json:reports/coverage.json
uv run python -m tests.bdd.gerar_relatorio
```
