"""RF20 a RF26 e RF30: mapa, reserva, conflitos, confirmação, minhas reservas, cancelamento pelo admin.

Cobre também RNF01 (integridade sob concorrência), RNF02 (conflito sob concorrência),
RNF24 (idempotência), RNF25 (atomicidade).
"""

import threading
from concurrent.futures import ThreadPoolExecutor

from tests.helpers import (
    cadastrar_cliente,
    cadastrar_filme,
    cadastrar_sala,
    criar_sessao,
    publicar_dia,
    reservar,
    token,
)


def _sessao_publicada(gestor, inicio="2026-11-02T19:00:00", duracao=120, sala=None):
    filme = cadastrar_filme(gestor)
    sala = sala or cadastrar_sala(gestor, nome="Sala 1", qtd_assentos=5)
    sessao = criar_sessao(gestor, filme["id"], sala["id"], inicio=inicio, duracao=duracao).json()
    publicar_dia(gestor, inicio[:10])
    return sessao, sala


def _cliente_id(cliente):
    return cliente.get("/v1/sessao").json()["usuario"]["cliente_id"]


class TestRF20Mapa:
    def test_mapa_mostra_assentos_livres_e_ocupados(self, gestor_http, cliente_http, cliente_http_b):
        sessao, _ = _sessao_publicada(gestor_http)
        mapa = cliente_http.get(f"/v1/sessoes/{sessao['id']}/assentos").json()
        assert [a["codigo"] for a in mapa["assentos"]] == ["A1", "A2", "A3", "A4", "A5"]
        assert all(a["ocupado"] is False for a in mapa["assentos"])

        assert reservar(cliente_http_b, sessao["id"], ["A1"]).status_code == 201
        mapa = cliente_http.get(f"/v1/sessoes/{sessao['id']}/assentos").json()
        ocupacao = {a["codigo"]: a["ocupado"] for a in mapa["assentos"]}
        assert ocupacao["A1"] is True
        assert ocupacao["A2"] is False

    def test_mapa_exige_cliente_logado(self, gestor_http, visitante_http):
        sessao, _ = _sessao_publicada(gestor_http)
        assert visitante_http.get(f"/v1/sessoes/{sessao['id']}/assentos").status_code == 401

    def test_mapa_nao_mostra_assento_recem_reservado_como_livre(self, gestor_http, cliente_http, cliente_http_b):
        """RNF14: o mapa não usa cache de programação."""
        sessao, _ = _sessao_publicada(gestor_http)
        cliente_http.get(f"/v1/sessoes/{sessao['id']}/assentos")
        reservar(cliente_http_b, sessao["id"], ["A2"])
        mapa = cliente_http.get(f"/v1/sessoes/{sessao['id']}/assentos").json()
        assert next(a for a in mapa["assentos"] if a["codigo"] == "A2")["ocupado"] is True


class TestRF21RF22Reserva:
    def test_reserva_de_varios_assentos_grava_todos(self, gestor_http, cliente_http):
        sessao, _ = _sessao_publicada(gestor_http)
        resposta = reservar(cliente_http, sessao["id"], ["A1", "A2"])
        assert resposta.status_code == 201
        corpo = resposta.json()
        assert [r["assento"] for r in corpo["reservas"]] == ["A1", "A2"]
        assert corpo["valor_total"] == "50.00"

    def test_reenvio_com_mesma_chave_nao_duplica(self, gestor_http, cliente_http):
        """RNF24: o mesmo pedido enviado duas vezes gera uma única reserva."""
        sessao, _ = _sessao_publicada(gestor_http)
        chave = "chave-fixa-do-pedido-1"
        primeira = reservar(cliente_http, sessao["id"], ["A1", "A2"], chave=chave)
        segunda = reservar(cliente_http, sessao["id"], ["A1", "A2"], chave=chave)
        assert primeira.status_code == 201
        assert segunda.status_code == 201
        assert primeira.json()["reservas"] == segunda.json()["reservas"]
        assert len(cliente_http.get("/v1/minhas-reservas").json()["itens"]) == 2

    def test_mesma_chave_com_corpo_diferente_retorna_422(self, gestor_http, cliente_http):
        sessao, _ = _sessao_publicada(gestor_http)
        chave = "chave-reutilizada"
        assert reservar(cliente_http, sessao["id"], ["A1"], chave=chave).status_code == 201
        resposta = reservar(cliente_http, sessao["id"], ["A2"], chave=chave)
        assert resposta.status_code == 422
        assert resposta.json()["codigo"] == "idempotencia_conflito"

    def test_cabecalho_idempotency_key_e_obrigatorio(self, gestor_http, cliente_http):
        sessao, _ = _sessao_publicada(gestor_http)
        resposta = cliente_http.post(
            "/v1/reservas",
            json={"sessao_id": sessao["id"], "assentos": ["A1"]},
            headers=token(cliente_http),
        )
        assert resposta.status_code == 422
        assert resposta.json()["codigo"] == "cabecalho_obrigatorio"

    def test_lista_vazia_de_assentos_retorna_422(self, gestor_http, cliente_http):
        sessao, _ = _sessao_publicada(gestor_http)
        resposta = reservar(cliente_http, sessao["id"], [])
        assert resposta.status_code == 422
        assert "assentos" in resposta.json()["campos"]

    def test_sessao_cancelada_nao_aceita_reserva(self, gestor_http, cliente_http):
        sessao, _ = _sessao_publicada(gestor_http)
        gestor_http.post(f"/v1/sessoes/{sessao['id']}/cancelamento", headers=token(gestor_http))
        resposta = reservar(cliente_http, sessao["id"], ["A1"])
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "sessao_cancelada"


class TestRF23AssentoOcupado:
    def test_assento_ocupado_por_outro_cliente_retorna_409(self, gestor_http, cliente_http, cliente_http_b):
        sessao, _ = _sessao_publicada(gestor_http)
        assert reservar(cliente_http_b, sessao["id"], ["A1"]).status_code == 201
        resposta = reservar(cliente_http, sessao["id"], ["A1"])
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "assento_indisponivel"

    def test_assento_inexistente_nao_grava_nada(self, gestor_http, cliente_http):
        """RNF25: falha de validação não deixa reserva parcial."""
        sessao, _ = _sessao_publicada(gestor_http)
        resposta = reservar(cliente_http, sessao["id"], ["A1", "Z9"])
        assert resposta.status_code == 422
        assert resposta.json()["codigo"] == "assento_inexistente"
        mapa = cliente_http.get(f"/v1/sessoes/{sessao['id']}/assentos").json()
        assert next(a for a in mapa["assentos"] if a["codigo"] == "A1")["ocupado"] is False


class TestRF24ConflitoDoCliente:
    def test_reserva_em_sessao_que_conflita_com_outra_do_cliente_retorna_409(self, gestor_http, cliente_http):
        sessao_a, sala = _sessao_publicada(gestor_http, inicio="2026-11-02T19:00:00", duracao=120)
        filme = cadastrar_filme(gestor_http, titulo="Outro")
        sessao_b = criar_sessao(gestor_http, filme["id"], cadastrar_sala(gestor_http, nome="Sala 2")["id"],
                                inicio="2026-11-02T20:00:00", duracao=60).json()
        assert reservar(cliente_http, sessao_a["id"], ["A1"]).status_code == 201
        resposta = reservar(cliente_http, sessao_b["id"], ["A1"])
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "conflito_horario_cliente"

    def test_sessoes_nao_conflitantes_podem_ser_reservadas_pelo_mesmo_cliente(self, gestor_http, cliente_http):
        sessao_a, _ = _sessao_publicada(gestor_http, inicio="2026-11-02T19:00:00", duracao=120)
        filme = cadastrar_filme(gestor_http, titulo="Outro")
        sessao_b = criar_sessao(gestor_http, filme["id"], cadastrar_sala(gestor_http, nome="Sala 2")["id"],
                                inicio="2026-11-02T21:00:00", duracao=60).json()
        assert reservar(cliente_http, sessao_a["id"], ["A1"]).status_code == 201
        assert reservar(cliente_http, sessao_b["id"], ["A1"]).status_code == 201


class TestRF25Confirmacao:
    def test_confirmacao_traz_sessao_assentos_e_valor(self, gestor_http, cliente_http):
        sessao, _ = _sessao_publicada(gestor_http)
        corpo = reservar(cliente_http, sessao["id"], ["A3"]).json()
        assert corpo["sessao_id"] == sessao["id"]
        assert corpo["data_hora_inicio"] == "2026-11-02T19:00:00"
        assert corpo["filme"]["titulo"] == "Filme Nacional"
        assert corpo["valor_total"] == "25.00"


class TestRF26MinhasReservas:
    def test_lista_apenas_as_reservas_do_proprio_cliente(self, gestor_http, cliente_http, cliente_http_b):
        sessao, _ = _sessao_publicada(gestor_http)
        reservar(cliente_http, sessao["id"], ["A1"])
        reservar(cliente_http_b, sessao["id"], ["A2"])
        itens = cliente_http.get("/v1/minhas-reservas").json()["itens"]
        assert [i["assento"] for i in itens] == ["A1"]

    def test_minhas_reservas_exige_login(self, visitante_http):
        assert visitante_http.get("/v1/minhas-reservas").status_code == 401


class TestRF30CancelamentoPeloAdmin:
    def test_admin_lista_e_cancela_reserva_liberando_o_assento(self, gestor_http, cliente_http, admin_http):
        sessao, _ = _sessao_publicada(gestor_http)
        reserva = reservar(cliente_http, sessao["id"], ["A1"]).json()["reservas"][0]
        cliente_id = _cliente_id(cliente_http)

        lista = admin_http.get("/v1/reservas", params={"cliente_id": cliente_id}).json()["itens"]
        assert [r["id"] for r in lista] == [reserva["id"]]

        resposta = admin_http.delete(f"/v1/reservas/{reserva['id']}", headers=token(admin_http))
        assert resposta.status_code == 204

        mapa = cliente_http.get(f"/v1/sessoes/{sessao['id']}/assentos").json()
        assert next(a for a in mapa["assentos"] if a["codigo"] == "A1")["ocupado"] is False
        acoes = [r["acao"] for r in admin_http.get("/v1/auditoria").json()["itens"]]
        assert "reserva.cancelar" in acoes

    def test_gestor_nao_cancela_reserva(self, gestor_http, cliente_http):
        sessao, _ = _sessao_publicada(gestor_http)
        reserva = reservar(cliente_http, sessao["id"], ["A1"]).json()["reservas"][0]
        resposta = gestor_http.delete(f"/v1/reservas/{reserva['id']}", headers=token(gestor_http))
        assert resposta.status_code == 403


class TestRNF01RNF02Concorrencia:
    """Disputa real entre threads, usando a camada de serviço e uma sessão de banco por thread."""

    def test_somente_uma_reserva_por_assento_sob_concorrencia(self, app, gestor_http, visitante_http):
        from app.erros import ErroDominio
        from app.servicos.reservas import reservar_assentos

        sessao, _ = _sessao_publicada(gestor_http)
        clientes = [cadastrar_cliente(visitante_http, email=f"c{i}@exemplo.com")["id"] for i in range(10)]
        barreira = threading.Barrier(len(clientes))

        def tentar(cliente_id):
            barreira.wait()
            with app.state.sessionmaker() as db:
                try:
                    reservar_assentos(
                        db,
                        cliente_id=cliente_id,
                        sessao_id=sessao["id"],
                        codigos=["A1"],
                        chave=f"chave-{cliente_id}",
                        corpo_hash=f"corpo-{cliente_id}",
                    )
                    return "ok"
                except ErroDominio as erro:
                    return erro.codigo

        with ThreadPoolExecutor(max_workers=len(clientes)) as pool:
            resultados = list(pool.map(tentar, clientes))

        assert resultados.count("ok") == 1
        assert resultados.count("assento_indisponivel") == len(clientes) - 1

    def test_mesmo_cliente_nao_reserva_sessoes_sobrepostas_em_paralelo(self, app, gestor_http, visitante_http):
        from app.erros import ErroDominio
        from app.servicos.reservas import reservar_assentos

        sala_a = cadastrar_sala(gestor_http, nome="Sala A", qtd_assentos=3)
        sala_b = cadastrar_sala(gestor_http, nome="Sala B", qtd_assentos=3)
        filme = cadastrar_filme(gestor_http)
        sessao_a = criar_sessao(gestor_http, filme["id"], sala_a["id"], inicio="2026-11-02T19:00:00", duracao=120).json()
        sessao_b = criar_sessao(gestor_http, filme["id"], sala_b["id"], inicio="2026-11-02T20:00:00", duracao=120).json()
        cliente_id = cadastrar_cliente(visitante_http, email="paralelo@exemplo.com")["id"]
        barreira = threading.Barrier(2)

        def tentar(args):
            sessao_id, codigo = args
            barreira.wait()
            with app.state.sessionmaker() as db:
                try:
                    reservar_assentos(
                        db,
                        cliente_id=cliente_id,
                        sessao_id=sessao_id,
                        codigos=[codigo],
                        chave=f"chave-{sessao_id}",
                        corpo_hash=f"corpo-{sessao_id}",
                    )
                    return "ok"
                except ErroDominio as erro:
                    return erro.codigo

        with ThreadPoolExecutor(max_workers=2) as pool:
            resultados = list(pool.map(tentar, [(sessao_a["id"], "A1"), (sessao_b["id"], "A1")]))

        assert resultados.count("ok") == 1
        assert resultados.count("conflito_horario_cliente") == 1
