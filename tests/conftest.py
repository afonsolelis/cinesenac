"""Fixtures compartilhadas. Cada teste recebe um banco SQLite novo, em diretório temporário.

Perfis de teste:
- visitante_http: sem login (persona Visitante).
- cliente_http: logado como Cliente.
- gestor_http: logado como Gestor.
- admin_http: logado como Admin.
Cada fixture usa um TestClient próprio, portanto um cookie de sessão por perfil.
"""

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.servicos.usuarios import criar_usuario
from tests.helpers import (
    ADMIN_EMAIL,
    ADMIN_SENHA,
    CLIENTE_EMAIL,
    CLIENTE_SENHA,
    GESTOR_EMAIL,
    GESTOR_SENHA,
    cadastrar_cliente,
    login,
    token,
)


@pytest.fixture
def settings(tmp_path):
    return Settings(
        secret_key="chave-de-teste-com-tamanho-suficiente-0123456789abcdef",
        database_url=f"sqlite:///{tmp_path / 'teste.db'}",
        https_only=False,
        # TTL zero mantém os testes determinísticos. O cache real (30 s) é testado
        # em test_programacao.py, com uma aplicação própria.
        cache_ttl_seconds=0,
        login_max_tentativas=5,
        login_janela_segundos=900,
        max_requisicoes_simultaneas=200,
    )


@pytest.fixture
def app(settings):
    application = create_app(settings)
    with application.state.sessionmaker() as db:
        criar_usuario(db, email=ADMIN_EMAIL, senha=ADMIN_SENHA, perfil="admin")
    return application


@pytest.fixture
def visitante_http(app):
    return TestClient(app)


@pytest.fixture
def admin_http(app):
    client = TestClient(app)
    login(client, ADMIN_EMAIL, ADMIN_SENHA)
    return client


@pytest.fixture
def gestor_http(app, admin_http):
    resposta = admin_http.post(
        "/v1/usuarios",
        json={"email": GESTOR_EMAIL, "senha": GESTOR_SENHA, "perfil": "gestor"},
        headers=token(admin_http),
    )
    assert resposta.status_code == 201, resposta.text
    client = TestClient(app)
    login(client, GESTOR_EMAIL, GESTOR_SENHA)
    return client


@pytest.fixture
def cliente_http(app):
    client = TestClient(app)
    cadastrar_cliente(client, email=CLIENTE_EMAIL, senha=CLIENTE_SENHA)
    login(client, CLIENTE_EMAIL, CLIENTE_SENHA)
    return client


@pytest.fixture
def cliente_http_b(app):
    """Segundo cliente, para cenários de disputa entre dois clientes."""
    client = TestClient(app)
    cadastrar_cliente(client, email="bruno@exemplo.com", senha=CLIENTE_SENHA, nome="Bruno")
    login(client, "bruno@exemplo.com", CLIENTE_SENHA)
    return client
