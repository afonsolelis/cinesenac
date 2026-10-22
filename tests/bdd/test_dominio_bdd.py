"""Cenários Gherkin de features/dominio.feature, executados com pytest-bdd."""

from pathlib import Path

from pytest_bdd import scenarios

from tests.bdd.steps import *  # noqa: F401,F403  (definições de passos)

FEATURES = Path(__file__).resolve().parents[2] / "features"

scenarios("dominio.feature", features_base_dir=FEATURES)
