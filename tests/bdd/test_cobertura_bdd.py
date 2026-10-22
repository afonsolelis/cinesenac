"""Garante que cada teste pytest tem um cenário Gherkin equivalente, e vice-versa.

Cada cenário declara os testes que cobre numa linha '# Equivale a: <node ids>'.
Os node ids são lidos por AST, sem importar os módulos de teste.
"""

import ast
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def _testes_existentes() -> set[str]:
    ids: set[str] = set()
    for arquivo in sorted((RAIZ / "tests").glob("test_*.py")):
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        for no in arvore.body:
            if isinstance(no, ast.FunctionDef) and no.name.startswith("test_"):
                ids.add(f"tests/{arquivo.name}::{no.name}")
            elif isinstance(no, ast.ClassDef) and no.name.startswith("Test"):
                for sub in no.body:
                    if isinstance(sub, ast.FunctionDef) and sub.name.startswith("test_"):
                        ids.add(f"tests/{arquivo.name}::{no.name}::{sub.name}")
    return ids


def _testes_cobertos_por_bdd() -> set[str]:
    ids: set[str] = set()
    for arquivo in sorted((RAIZ / "features").glob("*.feature")):
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            if linha.strip().startswith("# Equivale a:"):
                ids |= {item.strip() for item in linha.split(":", 1)[1].split(",") if item.strip()}
    return ids


def test_todo_teste_existente_tem_cenario_bdd():
    assert _testes_existentes() - _testes_cobertos_por_bdd() == set()


def test_todo_mapeamento_aponta_para_teste_existente():
    assert _testes_cobertos_por_bdd() - _testes_existentes() == set()
