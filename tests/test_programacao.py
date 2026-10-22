"""RF03, RF14 a RF19, RF17 e RNF14 (cache), RNF05 (cota nacional), RNF33 (auditoria de cancelamento)."""

from tests.helpers import (
    cadastrar_filme,
    cadastrar_sala,
    criar_sessao,
    publicar_dia,
    reservar,
    token,
)


def _cenario(gestor, nacionalidade="NACIONAL"):
    filme = cadastrar_filme(gestor, nacionalidade=nacionalidade)
    sala = cadastrar_sala(gestor, nome="Sala 1")
    return filme, sala


class TestRF14CadastroSessao:
    def test_cadastra_sessao_sem_avisos_quando_cota_atendida(self, gestor_http):
        filme, sala = _cenario(gestor_http)
        resposta = criar_sessao(gestor_http, filme["id"], sala["id"])
        assert resposta.status_code == 201
        assert resposta.json()["avisos"] == []
        assert resposta.json()["valor_ingresso"] == "25.00"

    def test_referencia_inexistente_retorna_404(self, gestor_http):
        filme, _ = _cenario(gestor_http)
        resposta = criar_sessao(gestor_http, filme["id"], 9999)
        assert resposta.status_code == 404
        assert resposta.json()["codigo"] == "nao_encontrado"

    def test_dia_sem_filme_nacional_gera_aviso(self, gestor_http):
        filme, sala = _cenario(gestor_http, nacionalidade="INTERNACIONAL")
        resposta = criar_sessao(gestor_http, filme["id"], sala["id"])
        assert resposta.status_code == 201
        assert "cota_nacional_pendente" in resposta.json()["avisos"]


class TestRF15Sobreposicao:
    def test_sobreposicao_na_mesma_sala_retorna_409(self, gestor_http):
        filme, sala = _cenario(gestor_http)
        criar_sessao(gestor_http, filme["id"], sala["id"], inicio="2026-11-02T19:00:00", duracao=120)
        resposta = criar_sessao(gestor_http, filme["id"], sala["id"], inicio="2026-11-02T20:00:00", duracao=60)
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "conflito_horario_sala"

    def test_mesmo_horario_em_salas_diferentes_nao_conflita(self, gestor_http):
        filme, sala = _cenario(gestor_http)
        outra = cadastrar_sala(gestor_http, nome="Sala 2")
        criar_sessao(gestor_http, filme["id"], sala["id"], inicio="2026-11-02T19:00:00", duracao=120)
        resposta = criar_sessao(gestor_http, filme["id"], outra["id"], inicio="2026-11-02T19:00:00", duracao=120)
        assert resposta.status_code == 201

    def test_sessao_adjacente_na_mesma_sala_nao_conflita(self, gestor_http):
        filme, sala = _cenario(gestor_http)
        criar_sessao(gestor_http, filme["id"], sala["id"], inicio="2026-11-02T19:00:00", duracao=120)
        resposta = criar_sessao(gestor_http, filme["id"], sala["id"], inicio="2026-11-02T21:00:00", duracao=60)
        assert resposta.status_code == 201


class TestRF16EdicaoCancelamento:
    def test_altera_horario_livre(self, gestor_http):
        filme, sala = _cenario(gestor_http)
        sessao = criar_sessao(gestor_http, filme["id"], sala["id"]).json()
        resposta = gestor_http.patch(
            f"/v1/sessoes/{sessao['id']}",
            json={"data_hora_inicio": "2026-11-02T22:00:00"},
            headers=token(gestor_http),
        )
        assert resposta.status_code == 200
        assert resposta.json()["data_hora_inicio"] == "2026-11-02T22:00:00"

    def test_altera_horario_que_conflita_retorna_409(self, gestor_http):
        filme, sala = _cenario(gestor_http)
        criar_sessao(gestor_http, filme["id"], sala["id"], inicio="2026-11-02T19:00:00", duracao=120)
        outra = criar_sessao(gestor_http, filme["id"], sala["id"], inicio="2026-11-02T22:00:00", duracao=60).json()
        resposta = gestor_http.patch(
            f"/v1/sessoes/{outra['id']}",
            json={"data_hora_inicio": "2026-11-02T20:00:00"},
            headers=token(gestor_http),
        )
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "conflito_horario_sala"

    def test_cancela_sessao_sem_reservas(self, gestor_http):
        filme, sala = _cenario(gestor_http)
        sessao = criar_sessao(gestor_http, filme["id"], sala["id"]).json()
        resposta = gestor_http.post(f"/v1/sessoes/{sessao['id']}/cancelamento", headers=token(gestor_http))
        assert resposta.status_code == 200
        assert resposta.json()["cancelada"] is True

    def test_cancelamento_com_reservas_retorna_409(self, gestor_http, cliente_http):
        filme, sala = _cenario(gestor_http)
        sessao = criar_sessao(gestor_http, filme["id"], sala["id"]).json()
        publicar_dia(gestor_http)
        assert reservar(cliente_http, sessao["id"], ["A1"]).status_code == 201
        resposta = gestor_http.post(f"/v1/sessoes/{sessao['id']}/cancelamento", headers=token(gestor_http))
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "sessao_com_reservas"

    def test_cancelamento_gera_registro_de_auditoria(self, gestor_http, admin_http):
        filme, sala = _cenario(gestor_http)
        sessao = criar_sessao(gestor_http, filme["id"], sala["id"]).json()
        gestor_http.post(f"/v1/sessoes/{sessao['id']}/cancelamento", headers=token(gestor_http))
        acoes = [r["acao"] for r in admin_http.get("/v1/auditoria").json()["itens"]]
        assert "sessao.cancelar" in acoes


class TestRF18IndicadorCota:
    def test_indicador_fica_pendente_sem_nacional_e_atendido_com_nacional(self, gestor_http):
        filme_int, sala = _cenario(gestor_http, nacionalidade="INTERNACIONAL")
        criar_sessao(gestor_http, filme_int["id"], sala["id"])
        pendente = gestor_http.get("/v1/programacao/2026-11-02/cota-nacional").json()
        assert pendente["atendida"] is False
        assert pendente["sessoes_nacionais"] == 0

        filme_nac = cadastrar_filme(gestor_http, titulo="Nacional", nacionalidade="NACIONAL")
        criar_sessao(gestor_http, filme_nac["id"], sala["id"], inicio="2026-11-02T21:00:00")
        atendido = gestor_http.get("/v1/programacao/2026-11-02/cota-nacional").json()
        assert atendido["atendida"] is True
        assert atendido["sessoes_nacionais"] == 1


class TestRF19BloqueioPublicacao:
    def test_publicacao_bloqueada_sem_cota_nacional(self, gestor_http):
        filme, sala = _cenario(gestor_http, nacionalidade="INTERNACIONAL")
        criar_sessao(gestor_http, filme["id"], sala["id"])
        resposta = publicar_dia(gestor_http)
        assert resposta.status_code == 422
        assert resposta.json()["codigo"] == "cota_nacional_nao_atendida"

    def test_publicacao_com_cota_atendida(self, gestor_http):
        filme, sala = _cenario(gestor_http)
        criar_sessao(gestor_http, filme["id"], sala["id"])
        resposta = publicar_dia(gestor_http)
        assert resposta.status_code == 200
        assert resposta.json()["publicado"] is True


class TestRF03RF17ProgramacaoPublica:
    def test_visitante_so_ve_dias_publicados(self, gestor_http, visitante_http):
        filme, sala = _cenario(gestor_http)
        criar_sessao(gestor_http, filme["id"], sala["id"])
        assert visitante_http.get("/v1/programacao").json()["itens"] == []
        publicar_dia(gestor_http)
        itens = visitante_http.get("/v1/programacao").json()["itens"]
        assert len(itens) == 1
        assert itens[0]["filme"]["titulo"] == "Filme Nacional"

    def test_sessoes_canceladas_nao_aparecem(self, gestor_http, visitante_http):
        filme, sala = _cenario(gestor_http)
        sessao = criar_sessao(gestor_http, filme["id"], sala["id"]).json()
        publicar_dia(gestor_http)
        gestor_http.post(f"/v1/sessoes/{sessao['id']}/cancelamento", headers=token(gestor_http))
        assert visitante_http.get("/v1/programacao").json()["itens"] == []

    def test_filtra_por_sala(self, gestor_http, visitante_http):
        filme, sala = _cenario(gestor_http)
        outra = cadastrar_sala(gestor_http, nome="Sala 2")
        criar_sessao(gestor_http, filme["id"], sala["id"])
        criar_sessao(gestor_http, filme["id"], outra["id"], inicio="2026-11-02T21:00:00")
        publicar_dia(gestor_http)
        itens = visitante_http.get("/v1/programacao", params={"sala_id": outra["id"]}).json()["itens"]
        assert [i["sala"]["id"] for i in itens] == [outra["id"]]

    def test_filtra_por_periodo(self, gestor_http, visitante_http):
        filme, sala = _cenario(gestor_http)
        criar_sessao(gestor_http, filme["id"], sala["id"], inicio="2026-11-02T19:00:00")
        criar_sessao(gestor_http, filme["id"], sala["id"], inicio="2026-11-03T19:00:00")
        publicar_dia(gestor_http, "2026-11-02")
        publicar_dia(gestor_http, "2026-11-03")
        itens = visitante_http.get(
            "/v1/programacao", params={"inicio": "2026-11-03", "fim": "2026-11-03"}
        ).json()["itens"]
        assert len(itens) == 1

    def test_resposta_publica_usa_cache_dentro_do_ttl(self, tmp_path):
        """RNF14 e ADR-0007: a segunda leitura dentro do TTL vem do cache."""
        from fastapi.testclient import TestClient

        from app.config import Settings
        from app.main import create_app
        from app.servicos.usuarios import criar_usuario
        from tests.helpers import GESTOR_EMAIL, GESTOR_SENHA, login

        config = Settings(
            secret_key="chave-de-teste-com-tamanho-suficiente-0123456789abcdef",
            database_url=f"sqlite:///{tmp_path / 'cache.db'}",
            cache_ttl_seconds=30,
        )
        application = create_app(config)
        with application.state.sessionmaker() as db:
            criar_usuario(db, email=GESTOR_EMAIL, senha=GESTOR_SENHA, perfil="gestor")
        gestor = TestClient(application)
        login(gestor, GESTOR_EMAIL, GESTOR_SENHA)
        filme, sala = _cenario(gestor)
        criar_sessao(gestor, filme["id"], sala["id"])
        publicar_dia(gestor)

        visitante = TestClient(application)
        primeira = visitante.get("/v1/programacao")
        segunda = visitante.get("/v1/programacao")
        assert primeira.headers["X-Cache"] == "MISS"
        assert segunda.headers["X-Cache"] == "HIT"
