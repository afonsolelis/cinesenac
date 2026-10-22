"""RF04 a RF07: cadastro, unicidade, edição e visualização do cliente. RNF03, RNF29, RNF32."""

import threading
from concurrent.futures import ThreadPoolExecutor

from tests.helpers import ENDERECO, cadastrar_cliente, token


class TestRF04Cadastro:
    def test_cadastro_cria_conta_de_cliente(self, visitante_http):
        dados = cadastrar_cliente(visitante_http, email="bia@exemplo.com", nome="Bia", idade=25)
        assert dados["nome"] == "Bia"
        assert dados["email"] == "bia@exemplo.com"
        assert dados["idade"] == 25
        assert dados["endereco"]["cidade"] == "São Paulo"
        assert "senha" not in dados and "senha_hash" not in dados

    def test_idade_invalida_retorna_422_com_campo(self, visitante_http):
        resposta = visitante_http.post(
            "/v1/clientes",
            json={"email": "x@exemplo.com", "senha": "senha-forte-123", "nome": "X", "idade": -1,
                  "endereco": ENDERECO},
            headers=token(visitante_http),
        )
        assert resposta.status_code == 422
        assert resposta.json()["codigo"] == "validacao"
        assert "idade" in resposta.json()["campos"]

    def test_endereco_incompleto_retorna_422(self, visitante_http):
        endereco = dict(ENDERECO)
        del endereco["cidade"]
        resposta = visitante_http.post(
            "/v1/clientes",
            json={"email": "x@exemplo.com", "senha": "senha-forte-123", "nome": "X", "idade": 20,
                  "endereco": endereco},
            headers=token(visitante_http),
        )
        assert resposta.status_code == 422
        assert any("cidade" in campo for campo in resposta.json()["campos"])


class TestRF05EmailUnico:
    def test_email_duplicado_retorna_409(self, visitante_http):
        cadastrar_cliente(visitante_http, email="dup@exemplo.com")
        resposta = visitante_http.post(
            "/v1/clientes",
            json={"email": "dup@exemplo.com", "senha": "senha-forte-123", "nome": "Outra", "idade": 40,
                  "endereco": ENDERECO},
            headers=token(visitante_http),
        )
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "email_duplicado"

    def test_cadastros_simultaneos_com_mesmo_email_criam_uma_conta(self, app):
        """RNF03: a unicidade vem do banco, não da checagem prévia."""
        from app.servicos.clientes import cadastrar_cliente as cadastrar
        from app.erros import ErroDominio

        endereco = dict(ENDERECO)
        barreira = threading.Barrier(12)

        def tentar(indice):
            barreira.wait()
            with app.state.sessionmaker() as db:
                try:
                    cadastrar(
                        db,
                        email="corrida@exemplo.com",
                        senha="senha-forte-123",
                        nome=f"Cliente {indice}",
                        idade=30,
                        endereco=endereco,
                    )
                    return "criado"
                except ErroDominio as erro:
                    return erro.codigo

        with ThreadPoolExecutor(max_workers=12) as pool:
            resultados = list(pool.map(tentar, range(12)))

        assert resultados.count("criado") == 1
        assert resultados.count("email_duplicado") == 11


class TestRF06Edicao:
    def test_cliente_edita_o_proprio_cadastro(self, cliente_http):
        cliente_id = cliente_http.get("/v1/sessao").json()["usuario"]["cliente_id"]
        resposta = cliente_http.patch(
            f"/v1/clientes/{cliente_id}",
            json={"idade": 31},
            headers=token(cliente_http),
        )
        assert resposta.status_code == 200
        assert resposta.json()["idade"] == 31

    def test_edicao_para_email_ja_usado_retorna_409(self, cliente_http, visitante_http):
        cadastrar_cliente(visitante_http, email="ocupado@exemplo.com")
        cliente_id = cliente_http.get("/v1/sessao").json()["usuario"]["cliente_id"]
        resposta = cliente_http.patch(
            f"/v1/clientes/{cliente_id}",
            json={"email": "ocupado@exemplo.com"},
            headers=token(cliente_http),
        )
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "email_duplicado"


class TestRF07Visualizacao:
    def test_cliente_visualiza_o_proprio_cadastro(self, cliente_http):
        cliente_id = cliente_http.get("/v1/sessao").json()["usuario"]["cliente_id"]
        resposta = cliente_http.get(f"/v1/clientes/{cliente_id}")
        assert resposta.status_code == 200
        assert resposta.json()["email"] == "ana@exemplo.com"

    def test_cliente_nao_ve_cadastro_de_outro(self, cliente_http, visitante_http):
        outro = cadastrar_cliente(visitante_http, email="outro@exemplo.com")
        resposta = cliente_http.get(f"/v1/clientes/{outro['id']}")
        assert resposta.status_code == 403
        assert resposta.json()["codigo"] == "sem_permissao"

    def test_cliente_nao_edita_cadastro_de_outro(self, cliente_http, visitante_http):
        outro = cadastrar_cliente(visitante_http, email="outro2@exemplo.com")
        resposta = cliente_http.patch(
            f"/v1/clientes/{outro['id']}",
            json={"idade": 99},
            headers=token(cliente_http),
        )
        assert resposta.status_code == 403

    def test_admin_visualiza_cadastro_de_cliente(self, admin_http, cliente_http):
        cliente_id = cliente_http.get("/v1/sessao").json()["usuario"]["cliente_id"]
        assert admin_http.get(f"/v1/clientes/{cliente_id}").status_code == 200
