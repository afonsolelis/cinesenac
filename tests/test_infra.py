"""Espinha dorsal de infraestrutura: configuração, cache, limitação, admissão, segurança."""

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.infra.admissao import ControleAdmissao
from app.infra.cache import CacheTTL
from app.infra.limitacao import LimitadorTentativas
from app.infra.seguranca import gerar_hash_senha, verificar_senha


class TestConfiguracao:
    def test_le_variaveis_com_prefixo_cinesenac(self, monkeypatch):
        monkeypatch.setenv("CINESENAC_SECRET_KEY", "x" * 40)
        monkeypatch.setenv("CINESENAC_DATABASE_URL", "sqlite:///./outro.db")
        monkeypatch.setenv("CINESENAC_CACHE_TTL_SEGUNDOS", "45")
        monkeypatch.setenv("CINESENAC_HTTPS_ONLY", "true")
        config = Settings.from_env()
        assert config.secret_key == "x" * 40
        assert config.database_url == "sqlite:///./outro.db"
        assert config.cache_ttl_seconds == 45
        assert config.https_only is True

    def test_valores_padrao_seguros(self, monkeypatch):
        monkeypatch.setenv("CINESENAC_SECRET_KEY", "x" * 40)
        for nome in ("CINESENAC_HTTPS_ONLY", "CINESENAC_CACHE_TTL_SEGUNDOS"):
            monkeypatch.delenv(nome, raising=False)
        config = Settings.from_env()
        assert config.https_only is False
        assert config.cache_ttl_seconds == 30
        assert config.login_max_tentativas == 5

    def test_exige_chave_secreta(self, monkeypatch):
        monkeypatch.delenv("CINESENAC_SECRET_KEY", raising=False)
        with pytest.raises(ValueError, match="CINESENAC_SECRET_KEY"):
            Settings.from_env()

    def test_recusa_chave_secreta_curta(self):
        with pytest.raises(ValueError):
            Settings(secret_key="curta")


class TestRNF14Cache:
    def test_devolve_valor_dentro_do_ttl(self):
        relogio = [0.0]
        cache = CacheTTL(ttl_segundos=30, relogio=lambda: relogio[0])
        cache.definir("programacao", ["sessao"])
        relogio[0] = 29
        assert cache.obter("programacao") == ["sessao"]

    def test_expira_apos_o_ttl(self):
        relogio = [0.0]
        cache = CacheTTL(ttl_segundos=30, relogio=lambda: relogio[0])
        cache.definir("programacao", ["sessao"])
        relogio[0] = 31
        assert cache.obter("programacao") is None

    def test_limpar_remove_todas_as_chaves(self):
        cache = CacheTTL(ttl_segundos=30, relogio=lambda: 0.0)
        cache.definir("a", 1)
        cache.limpar()
        assert cache.obter("a") is None


class TestRNF30LimitacaoDeTentativas:
    def test_bloqueia_apos_o_limite_de_falhas(self):
        limitador = LimitadorTentativas(max_tentativas=3, janela_segundos=900, relogio=lambda: 0.0)
        for _ in range(3):
            limitador.registrar_falha("ana@exemplo.com")
        assert limitador.bloqueado("ana@exemplo.com") is True

    def test_libera_apos_a_janela(self):
        relogio = [0.0]
        limitador = LimitadorTentativas(max_tentativas=2, janela_segundos=60, relogio=lambda: relogio[0])
        limitador.registrar_falha("x")
        limitador.registrar_falha("x")
        relogio[0] = 61
        assert limitador.bloqueado("x") is False

    def test_sucesso_zera_as_falhas(self):
        limitador = LimitadorTentativas(max_tentativas=2, janela_segundos=900, relogio=lambda: 0.0)
        limitador.registrar_falha("x")
        limitador.registrar_sucesso("x")
        limitador.registrar_falha("x")
        assert limitador.bloqueado("x") is False


class TestRNF27Admissao:
    def test_recusa_quando_o_limite_de_simultaneas_e_atingido(self):
        controle = ControleAdmissao(max_simultaneas=1)
        assert controle.tentar_entrar() is True
        assert controle.tentar_entrar() is False

    def test_libera_vaga_ao_sair(self):
        controle = ControleAdmissao(max_simultaneas=1)
        controle.tentar_entrar()
        controle.sair()
        assert controle.tentar_entrar() is True


class TestRNF28Senhas:
    def test_hash_nao_contem_a_senha(self):
        hash_ = gerar_hash_senha("senha-forte-123")
        assert "senha-forte-123" not in hash_

    def test_verifica_senha_correta(self):
        hash_ = gerar_hash_senha("senha-forte-123")
        assert verificar_senha(hash_, "senha-forte-123") is True

    def test_recusa_senha_errada(self):
        hash_ = gerar_hash_senha("senha-forte-123")
        assert verificar_senha(hash_, "outra-senha") is False

    def test_hash_invalido_nao_verifica(self):
        assert verificar_senha("nao-e-um-hash", "qualquer") is False


class TestInfraHttp:
    def test_healthz_responde_ok(self, visitante_http):
        resposta = visitante_http.get("/healthz")
        assert resposta.status_code == 200
        assert resposta.json() == {"status": "ok"}

    def test_openapi_expoe_contrato_v1(self, visitante_http):
        caminhos = visitante_http.get("/openapi.json").json()["paths"]
        assert "/v1/reservas" in caminhos
        assert "/v1/clientes" in caminhos
        assert all(caminho.startswith(("/v1", "/healthz")) for caminho in caminhos)

    def test_requisicao_recebe_identificador(self, visitante_http):
        resposta = visitante_http.get("/healthz", headers={"X-Request-ID": "abc-123"})
        assert resposta.headers["X-Request-ID"] == "abc-123"

    def test_gera_identificador_quando_ausente(self, visitante_http):
        resposta = visitante_http.get("/healthz")
        assert len(resposta.headers["X-Request-ID"]) >= 8

    def test_recusa_com_503_e_retry_after_quando_saturado(self, tmp_path):
        from app.main import create_app

        config = Settings(
            secret_key="chave-de-teste-com-tamanho-suficiente-0123456789abcdef",
            database_url=f"sqlite:///{tmp_path / 'saturado.db'}",
            max_requisicoes_simultaneas=0,
        )
        client = TestClient(create_app(config))
        resposta = client.get("/v1/programacao")
        assert resposta.status_code == 503
        assert resposta.headers["Retry-After"]
        assert resposta.json()["codigo"] == "servico_indisponivel"

    def test_healthz_nao_e_recusado_quando_saturado(self, tmp_path):
        from app.main import create_app

        config = Settings(
            secret_key="chave-de-teste-com-tamanho-suficiente-0123456789abcdef",
            database_url=f"sqlite:///{tmp_path / 'saturado2.db'}",
            max_requisicoes_simultaneas=0,
        )
        client = TestClient(create_app(config))
        assert client.get("/healthz").status_code == 200


class TestRNF31CabecalhosDeSeguranca:
    def test_api_envia_cabecalhos_de_seguranca(self, visitante_http):
        resposta = visitante_http.get("/v1/sessao")
        assert resposta.headers["X-Content-Type-Options"] == "nosniff"
        assert resposta.headers["X-Frame-Options"] == "DENY"
        assert "default-src 'self'" in resposta.headers["Content-Security-Policy"]
        assert resposta.headers["Referrer-Policy"] == "same-origin"


class TestCli:
    def test_cria_administrador_inicial(self, settings):
        from app.cli import criar_admin_inicial
        from app.main import create_app

        application = create_app(settings)
        criar_admin_inicial(application.state.sessionmaker, "dono@cinesenac.test", "senha-dono-forte-123")
        client = TestClient(application)
        resposta = client.post(
            "/v1/autenticacao",
            json={"email": "dono@cinesenac.test", "senha": "senha-dono-forte-123"},
            headers={"X-CSRF-Token": client.get("/v1/sessao").json()["csrf_token"]},
        )
        assert resposta.status_code == 200
        assert resposta.json()["usuario"]["perfil"] == "admin"

    def test_nao_cria_admin_com_senha_fraca(self, settings):
        from app.cli import criar_admin_inicial
        from app.main import create_app
        from app.erros import ErroDominio

        application = create_app(settings)
        with pytest.raises(ErroDominio) as excinfo:
            criar_admin_inicial(application.state.sessionmaker, "dono@cinesenac.test", "curta")
        assert excinfo.value.codigo == "validacao"
