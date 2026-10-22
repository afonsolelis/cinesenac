"""Fixture do cenário BDD: um Mundo novo por cenário, com banco temporário próprio."""

import pytest

from tests.bdd.mundo import Mundo


@pytest.fixture
def mundo(tmp_path, monkeypatch):
    return Mundo(tmp_path, monkeypatch)
