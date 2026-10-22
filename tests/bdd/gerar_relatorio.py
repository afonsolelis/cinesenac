"""Gera prd/qualidade/relatorio-cobertura.md a partir do coverage.json e dos cenários Gherkin.

Uso: pytest -m "not container" --cov --cov-report=json:reports/coverage.json
     python -m tests.bdd.gerar_relatorio
"""

import json
from datetime import date
from pathlib import Path

from tests.bdd.test_cobertura_bdd import RAIZ, _testes_cobertos_por_bdd, _testes_existentes


def _linhas_modulos(dados: dict) -> list[str]:
    linhas = ["| Módulo | Linhas | Cobertas | Ramos | Cobertura | Linhas sem cobertura |",
              "|---|---:|---:|---:|---:|---|"]
    for arquivo, info in sorted(dados["files"].items()):
        resumo = info["summary"]
        faltam = info["missing_lines"]
        ramos = resumo.get("num_branches", 0)
        cobertos_ramos = ramos - resumo.get("missing_branches", 0)
        percentual = resumo["percent_covered"]
        trecho = ", ".join(str(n) for n in faltam[:12]) + (" …" if len(faltam) > 12 else "")
        linhas.append(
            f"| `{arquivo}` | {resumo['num_statements']} | {resumo['covered_lines']} | "
            f"{cobertos_ramos}/{ramos} | {percentual:.0f}% | {trecho or '—'} |"
        )
    return linhas


def main() -> None:
    dados = json.loads((RAIZ / "reports" / "coverage.json").read_text(encoding="utf-8"))
    total = dados["totals"]
    existentes = _testes_existentes()
    cobertos = _testes_cobertos_por_bdd()
    unitarios = len(existentes)
    orfaos = sorted(existentes - cobertos)
    fantasmas = sorted(cobertos - existentes)
    modulos_fracos = [
        arq for arq, info in dados["files"].items() if info["summary"]["percent_covered"] < 85
    ]

    partes = [
        "# Relatório de cobertura de testes — CineSenac",
        "",
        f"**Gerado em:** {date.today().isoformat()}  ",
        "**Gerado por:** `python -m tests.bdd.gerar_relatorio` (ver [README](../../README.md#testes))",
        "",
        "## Resumo",
        "",
        "| Indicador | Valor |",
        "|---|---:|",
        f"| Cobertura de linhas e ramos (`app/`) | **{total['percent_covered']:.1f}%** |",
        f"| Linhas cobertas | {total['covered_lines']} de {total['num_statements']} |",
        f"| Ramos cobertos | {total['covered_branches']} de {total['num_branches']} |",
        f"| Testes unitários e de integração (pytest) | {unitarios} |",
        f"| Testes com cenário Gherkin equivalente | {len(existentes & cobertos)} de {unitarios} "
        f"({100 * len(existentes & cobertos) / unitarios:.0f}%) |",
        f"| Testes sem cenário BDD | {len(orfaos)} |",
        f"| Mapeamentos BDD apontando para teste inexistente | {len(fantasmas)} |",
        "",
        "A cobertura de testes é o mapeamento entre testes e cenários: cada teste existente tem",
        "um cenário Gherkin que o descreve, e o teste `tests/bdd/test_cobertura_bdd.py` falha se",
        "algum deles ficar sem cenário ou se um cenário apontar para um teste que não existe.",
        "",
        "## Cobertura de código por módulo",
        "",
        *_linhas_modulos(dados),
        "",
        "## Lacunas conhecidas",
        "",
        "Os módulos abaixo ficam abaixo de 85% de cobertura de linhas e ramos. As lacunas são",
        "reais e não foram escondidas.",
        "",
    ]
    if modulos_fracos:
        partes += [f"- `{arq}`" for arq in sorted(modulos_fracos)]
    else:
        partes.append("- Nenhuma.")
    partes += [
        "",
        "Principais lacunas de `app/web/routes.py`: formulários de criação e publicação do gestor",
        "(`/gestor/filmes`, `/gestor/sessoes`, `/gestor/publicar`), formulários do admin",
        "(`/admin/usuarios`, `/admin/usuarios/{id}/ativo`) e os caminhos de erro desses formulários.",
        "Os serviços de `catalogo`, `programacao`, `clientes` e `reservas` também têm ramos de",
        "validação não exercitados por cenários. A `app/cli.py` (`main`) não tem teste porque lê a",
        "senha do terminal.",
        "",
        "## Testes de contêiner",
        "",
        "Os testes em `tests/container/` sobem a imagem de contêiner com testcontainers. Eles",
        "verificam healthcheck, vitrine com cabeçalhos de segurança, arquivos estáticos, contrato",
        "da API e que o processo não roda como root. Não entram na cobertura de linhas, porque o",
        "código medido roda dentro do contêiner.",
        "",
        "## Como reproduzir",
        "",
        "```bash",
        "uv sync",
        'uv run pytest -m "not container" --cov --cov-report=json:reports/coverage.json',
        "uv run python -m tests.bdd.gerar_relatorio",
        "```",
        "",
    ]
    if orfaos:
        partes += ["## Testes sem cenário BDD", ""] + [f"- `{o}`" for o in orfaos] + [""]
    destino = RAIZ / "prd" / "qualidade" / "relatorio-cobertura.md"
    destino.write_text("\n".join(partes), encoding="utf-8")
    print(f"relatório escrito em {destino}")


if __name__ == "__main__":
    main()
