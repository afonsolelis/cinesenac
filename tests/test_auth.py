"""RF01, RF02, RNF28, RNF29, RNF30 e proteção CSRF."""

from fastapi.testclient import TestClient

from tests.helpers import (
    ADMIN_EMAIL,
    ADMIN_SENHA,
    CLIENTE_EMAIL,
    CLIENTE_SENHA,
    GESTOR_EMAIL,
    GESTOR_SENHA,
    cadastrar_cliente,
    login,
    logout,
    token,
)


class TestRF01Login:
    def test_login_com_credenciais_validas_cria_sessao(self, app):
        client = TestClient(app)
        usuario = login(client, ADMIN_EMAIL, ADMIN_SENHA)
        assert usuario["perfil"] == "admin"
        assert client.get("/v1/sessao").json()["usuario"]["email"] == ADMIN_EMAIL

    def test_credenciais_invalidas_retornam_401_generico(self, app):
        client = TestClient(app)
        senha_errada = client.post(
            "/v1/autenticacao",
            json={"email": ADMIN_EMAIL, "senha": "errada-123456"},
            headers=token(client),
        )
        email_inexistente = client.post(
            "/v1/autenticacao",
            json={"email": "ninguem@exemplo.com", "senha": "errada-123456"},
            headers=token(client),
        )
        assert senha_errada.status_code == 401
        assert email_inexistente.status_code == 401
        # Mesma mensagem nos dois casos: não revela se o e-mail existe.
        assert senha_errada.json() == email_inexistente.json()
        assert senha_errada.json()["codigo"] == "credenciais_invalidas"

    def test_cookie_de_sessao_e_httponly_e_samesite(self, app):
        client = TestClient(app)
        resposta = client.post(
            "/v1/autenticacao",
            json={"email": ADMIN_EMAIL, "senha": ADMIN_SENHA},
            headers=token(client),
        )
        cookie = resposta.headers["set-cookie"].lower()
        assert "httponly" in cookie
        assert "samesite=lax" in cookie

    def test_conta_desativada_nao_entra(self, admin_http, app):
        admin_http.post(
            "/v1/usuarios",
            json={"email": GESTOR_EMAIL, "senha": GESTOR_SENHA, "perfil": "gestor"},
            headers=token(admin_http),
        )
        usuarios = admin_http.get("/v1/usuarios").json()["itens"]
        gestor_id = next(u["id"] for u in usuarios if u["email"] == GESTOR_EMAIL)
        admin_http.patch(
            f"/v1/usuarios/{gestor_id}",
            json={"ativo": False},
            headers=token(admin_http),
        )
        client = TestClient(app)
        resposta = client.post(
            "/v1/autenticacao",
            json={"email": GESTOR_EMAIL, "senha": GESTOR_SENHA},
            headers=token(client),
        )
        assert resposta.status_code == 401

    def test_logout_encerra_a_sessao(self, admin_http):
        logout(admin_http)
        assert admin_http.get("/v1/sessao").json()["usuario"] is None


class TestRNF30LimiteDeTentativas:
    def test_bloqueia_apos_tentativas_excessivas(self, app):
        client = TestClient(app)
        for _ in range(5):
            resposta = client.post(
                "/v1/autenticacao",
                json={"email": ADMIN_EMAIL, "senha": "errada-123456"},
                headers=token(client),
            )
            assert resposta.status_code == 401
        bloqueada = client.post(
            "/v1/autenticacao",
            json={"email": ADMIN_EMAIL, "senha": ADMIN_SENHA},
            headers=token(client),
        )
        assert bloqueada.status_code == 429
        assert bloqueada.json()["codigo"] == "muitas_tentativas"


class TestRF02ControleDeAcesso:
    def test_rota_protegida_sem_login_retorna_401(self, visitante_http):
        resposta = visitante_http.get("/v1/filmes")
        assert resposta.status_code == 401
        assert resposta.json()["codigo"] == "nao_autenticado"

    def test_perfil_sem_permissao_retorna_403(self, cliente_http):
        resposta = cliente_http.get("/v1/filmes")
        assert resposta.status_code == 403
        assert resposta.json()["codigo"] == "sem_permissao"

    def test_sessao_de_conta_desativada_deixa_de_valer(self, cliente_http, admin_http):
        cliente_id = cliente_http.get("/v1/sessao").json()["usuario"]["cliente_id"]
        usuario_id = cliente_http.get("/v1/sessao").json()["usuario"]["id"]
        resposta = admin_http.patch(
            f"/v1/usuarios/{usuario_id}",
            json={"ativo": False},
            headers=token(admin_http),
        )
        assert resposta.status_code == 200
        # RNF28: a sessão antiga é revogada na desativação.
        depois = cliente_http.get(f"/v1/clientes/{cliente_id}")
        assert depois.status_code == 401


class TestCSRF:
    def test_escrita_sem_token_csrf_e_recusada(self, visitante_http):
        resposta = visitante_http.post(
            "/v1/clientes",
            json={"email": "x@exemplo.com", "senha": "senha-forte-123", "nome": "X", "idade": 20,
                  "endereco": {"logradouro": "R", "numero": "1", "bairro": "B", "cidade": "C",
                               "estado": "SP", "cep": "01000-000"}},
        )
        assert resposta.status_code == 403
        assert resposta.json()["codigo"] == "csrf_invalido"

    def test_token_de_outra_sessao_e_recusado(self, app, visitante_http):
        outra = TestClient(app)
        token_alheio = outra.get("/v1/sessao").json()["csrf_token"]
        resposta = visitante_http.post(
            "/v1/autenticacao",
            json={"email": ADMIN_EMAIL, "senha": ADMIN_SENHA},
            headers={"X-CSRF-Token": token_alheio},
        )
        assert resposta.status_code == 403
