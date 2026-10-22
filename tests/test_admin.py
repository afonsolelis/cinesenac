"""RF27 a RF29: contas, permissões e dashboard do Admin. RNF29, RNF32, RNF33."""

from tests.helpers import (
    ADMIN_EMAIL,
    cadastrar_cliente,
    cadastrar_filme,
    cadastrar_sala,
    criar_sessao,
    publicar_dia,
    reservar,
    token,
)


def _id_usuario(admin, email):
    usuarios = admin.get("/v1/usuarios").json()["itens"]
    return next(u["id"] for u in usuarios if u["email"] == email)


class TestRF27Contas:
    def test_admin_cria_gestor(self, admin_http):
        resposta = admin_http.post(
            "/v1/usuarios",
            json={"email": "novo.gestor@cinesenac.test", "senha": "senha-gestor-forte-123", "perfil": "gestor"},
            headers=token(admin_http),
        )
        assert resposta.status_code == 201
        assert resposta.json()["perfil"] == "gestor"
        assert "senha" not in resposta.json() and "senha_hash" not in resposta.json()

    def test_admin_cria_cliente_com_dados_de_cadastro(self, admin_http):
        from tests.helpers import ENDERECO

        resposta = admin_http.post(
            "/v1/usuarios",
            json={
                "email": "cliente.admin@exemplo.com",
                "senha": "senha-cliente-forte-123",
                "perfil": "cliente",
                "cliente": {"nome": "Caio", "idade": 40, "endereco": ENDERECO},
            },
            headers=token(admin_http),
        )
        assert resposta.status_code == 201
        assert resposta.json()["perfil"] == "cliente"
        assert resposta.json()["cliente_id"] is not None

    def test_cliente_sem_dados_de_cadastro_retorna_422(self, admin_http):
        resposta = admin_http.post(
            "/v1/usuarios",
            json={"email": "sem.dados@exemplo.com", "senha": "senha-cliente-forte-123", "perfil": "cliente"},
            headers=token(admin_http),
        )
        assert resposta.status_code == 422
        assert "cliente" in resposta.json()["campos"]

    def test_email_duplicado_em_conta_retorna_409(self, admin_http):
        resposta = admin_http.post(
            "/v1/usuarios",
            json={"email": ADMIN_EMAIL, "senha": "senha-forte-123456", "perfil": "gestor"},
            headers=token(admin_http),
        )
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "email_duplicado"

    def test_admin_desativa_conta(self, admin_http, gestor_http):
        gestor_id = _id_usuario(admin_http, "gestor@cinesenac.test")
        resposta = admin_http.patch(f"/v1/usuarios/{gestor_id}", json={"ativo": False}, headers=token(admin_http))
        assert resposta.status_code == 200
        assert resposta.json()["ativo"] is False

    def test_admin_exclui_cliente_sem_reservas(self, admin_http, visitante_http):
        cliente = cadastrar_cliente(visitante_http, email="sem.reserva@exemplo.com")
        usuario_id = _id_usuario(admin_http, "sem.reserva@exemplo.com")
        resposta = admin_http.delete(f"/v1/usuarios/{usuario_id}", headers=token(admin_http))
        assert resposta.status_code == 204
        assert admin_http.get(f"/v1/clientes/{cliente['id']}").status_code == 404

    def test_conta_com_reservas_nao_e_excluida(self, admin_http, gestor_http, cliente_http):
        filme = cadastrar_filme(gestor_http)
        sala = cadastrar_sala(gestor_http, qtd_assentos=3)
        sessao = criar_sessao(gestor_http, filme["id"], sala["id"]).json()
        publicar_dia(gestor_http)
        reservar(cliente_http, sessao["id"], ["A1"])
        usuario_id = _id_usuario(admin_http, "ana@exemplo.com")
        resposta = admin_http.delete(f"/v1/usuarios/{usuario_id}", headers=token(admin_http))
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "conta_com_reservas"

    def test_admin_nao_exclui_a_propria_conta(self, admin_http):
        usuario_id = _id_usuario(admin_http, ADMIN_EMAIL)
        resposta = admin_http.delete(f"/v1/usuarios/{usuario_id}", headers=token(admin_http))
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "operacao_nao_permitida"

    def test_acoes_de_conta_geram_auditoria(self, admin_http):
        admin_http.post(
            "/v1/usuarios",
            json={"email": "audit@cinesenac.test", "senha": "senha-forte-123456", "perfil": "gestor"},
            headers=token(admin_http),
        )
        acoes = [r["acao"] for r in admin_http.get("/v1/auditoria").json()["itens"]]
        assert "usuario.criar" in acoes

    def test_gestor_nao_gerencia_contas(self, gestor_http):
        resposta = gestor_http.get("/v1/usuarios")
        assert resposta.status_code == 403


class TestRF28Permissoes:
    def test_admin_lista_permissoes_do_perfil(self, admin_http):
        corpo = admin_http.get("/v1/perfis/gestor/permissoes").json()
        assert corpo["perfil"] == "gestor"
        assert "catalogo:gerenciar" in corpo["permissoes"]

    def test_alteracao_de_permissao_vale_imediatamente(self, admin_http, gestor_http):
        resposta = admin_http.put(
            "/v1/perfis/gestor/permissoes",
            json={"permissoes": ["programacao:gerenciar"]},
            headers=token(admin_http),
        )
        assert resposta.status_code == 200
        bloqueado = gestor_http.post(
            "/v1/filmes",
            json={"titulo": "X"},
            headers=token(gestor_http),
        )
        assert bloqueado.status_code == 403

    def test_admin_nao_remove_a_propria_permissao_de_gerir_permissoes(self, admin_http):
        resposta = admin_http.put(
            "/v1/perfis/admin/permissoes",
            json={"permissoes": ["catalogo:gerenciar"]},
            headers=token(admin_http),
        )
        assert resposta.status_code == 422
        assert resposta.json()["codigo"] == "permissao_obrigatoria"

    def test_gestor_nao_gerencia_permissoes(self, gestor_http):
        assert gestor_http.get("/v1/perfis/gestor/permissoes").status_code == 403

    def test_alteracao_de_permissoes_gera_auditoria(self, admin_http):
        admin_http.put(
            "/v1/perfis/gestor/permissoes",
            json={"permissoes": ["catalogo:gerenciar", "programacao:gerenciar"]},
            headers=token(admin_http),
        )
        acoes = [r["acao"] for r in admin_http.get("/v1/auditoria").json()["itens"]]
        assert "perfil.permissoes" in acoes


class TestRF29Dashboard:
    def test_dashboard_resume_todas_as_entidades(self, admin_http):
        corpo = admin_http.get("/v1/dashboard").json()
        for chave in ("usuarios", "filmes", "salas", "sessoes", "clientes", "reservas"):
            assert isinstance(corpo[chave], int)
        assert corpo["usuarios"] >= 1

    def test_gestor_nao_ve_dashboard(self, gestor_http):
        assert gestor_http.get("/v1/dashboard").status_code == 403

    def test_auditoria_so_para_admin(self, gestor_http):
        assert gestor_http.get("/v1/auditoria").status_code == 403


class TestProtecaoContraAutoBloqueio:
    def test_admin_nao_desativa_a_propria_conta(self, admin_http):
        usuario_id = _id_usuario(admin_http, ADMIN_EMAIL)
        resposta = admin_http.patch(f"/v1/usuarios/{usuario_id}", json={"ativo": False}, headers=token(admin_http))
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "operacao_nao_permitida"
        assert admin_http.get("/v1/sessao").json()["usuario"] is not None
