"""RF08 a RF13: catálogo de filmes e salas. RNF13, RNF29, RNF31."""

from tests.helpers import cadastrar_filme, cadastrar_sala, criar_sessao, reservar, token


class TestRF08CadastroFilme:
    def test_gestor_cadastra_filme(self, gestor_http):
        filme = cadastrar_filme(gestor_http, titulo="O Sertão")
        assert filme["titulo"] == "O Sertão"
        assert filme["nacionalidade"] == "NACIONAL"
        assert filme["faixa_etaria"] == "LIVRE"

    def test_cliente_nao_cadastra_filme(self, cliente_http):
        resposta = cliente_http.post(
            "/v1/filmes",
            json={"titulo": "X"},
            headers=token(cliente_http),
        )
        assert resposta.status_code == 403

    def test_cartaz_com_esquema_javascript_e_recusado(self, gestor_http):
        resposta = gestor_http.post(
            "/v1/filmes",
            json={
                "titulo": "Perigoso",
                "duracao_minutos": 90,
                "genero": "Terror",
                "sinopse": "x",
                "cartaz_url": "javascript:alert(1)",
                "faixa_etaria": "LIVRE",
                "elenco": "x",
                "nacionalidade": "NACIONAL",
            },
            headers=token(gestor_http),
        )
        assert resposta.status_code == 422
        assert "cartaz_url" in resposta.json()["campos"]

    def test_cartaz_https_e_aceito(self, gestor_http):
        filme = cadastrar_filme(gestor_http, cartaz_url="https://img.exemplo.com/a.png")
        assert filme["cartaz_url"] == "https://img.exemplo.com/a.png"

    def test_faixa_etaria_fora_do_dominio_retorna_422(self, gestor_http):
        resposta = gestor_http.post(
            "/v1/filmes",
            json={
                "titulo": "X",
                "duracao_minutos": 90,
                "genero": "Drama",
                "sinopse": "x",
                "cartaz_url": "https://img.exemplo.com/a.png",
                "faixa_etaria": "CINQUENTA_ANOS",
                "elenco": "x",
                "nacionalidade": "NACIONAL",
            },
            headers=token(gestor_http),
        )
        assert resposta.status_code == 422
        assert "faixa_etaria" in resposta.json()["campos"]


class TestRF09EdicaoExclusaoFilme:
    def test_gestor_edita_filme(self, gestor_http):
        filme = cadastrar_filme(gestor_http)
        resposta = gestor_http.patch(
            f"/v1/filmes/{filme['id']}",
            json={"titulo": "Novo Título"},
            headers=token(gestor_http),
        )
        assert resposta.status_code == 200
        assert resposta.json()["titulo"] == "Novo Título"

    def test_gestor_exclui_filme_sem_sessoes(self, gestor_http):
        filme = cadastrar_filme(gestor_http)
        resposta = gestor_http.delete(f"/v1/filmes/{filme['id']}", headers=token(gestor_http))
        assert resposta.status_code == 204
        lista = gestor_http.get("/v1/filmes").json()["itens"]
        assert all(item["id"] != filme["id"] for item in lista)

    def test_exclusao_de_filme_com_sessoes_e_recusada(self, gestor_http):
        filme = cadastrar_filme(gestor_http)
        sala = cadastrar_sala(gestor_http)
        criar_sessao(gestor_http, filme["id"], sala["id"])
        resposta = gestor_http.delete(f"/v1/filmes/{filme['id']}", headers=token(gestor_http))
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "filme_com_sessoes"


class TestRF10ListagemFilmes:
    def test_busca_filtra_por_titulo(self, gestor_http):
        cadastrar_filme(gestor_http, titulo="Domingo Infinito")
        cadastrar_filme(gestor_http, titulo="Madrugada")
        resposta = gestor_http.get("/v1/filmes", params={"q": "Dom"})
        titulos = [item["titulo"] for item in resposta.json()["itens"]]
        assert titulos == ["Domingo Infinito"]

    def test_listagem_sem_busca_traz_todos(self, gestor_http):
        cadastrar_filme(gestor_http, titulo="A")
        cadastrar_filme(gestor_http, titulo="B")
        assert len(gestor_http.get("/v1/filmes").json()["itens"]) == 2


class TestRF11CadastroSala:
    def test_cadastro_gera_assentos_de_A1_ate_An(self, gestor_http):
        sala = cadastrar_sala(gestor_http, qtd_assentos=3)
        detalhe = gestor_http.get(f"/v1/salas/{sala['id']}").json()
        assert [a["codigo"] for a in detalhe["assentos"]] == ["A1", "A2", "A3"]

    def test_quantidade_zero_retorna_422(self, gestor_http):
        resposta = gestor_http.post(
            "/v1/salas",
            json={"nome": "X", "qtd_assentos": 0, "hora_abertura": "14:00",
                  "hora_fechamento": "23:00", "especificacao_tecnica": "2D"},
            headers=token(gestor_http),
        )
        assert resposta.status_code == 422
        assert "qtd_assentos" in resposta.json()["campos"]

    def test_fechamento_antes_da_abertura_retorna_422(self, gestor_http):
        resposta = gestor_http.post(
            "/v1/salas",
            json={"nome": "X", "qtd_assentos": 5, "hora_abertura": "22:00",
                  "hora_fechamento": "10:00", "especificacao_tecnica": "2D"},
            headers=token(gestor_http),
        )
        assert resposta.status_code == 422
        assert "hora_fechamento" in resposta.json()["campos"]


class TestRF12EdicaoExclusaoSala:
    def test_aumentar_assentos_cria_os_novos(self, gestor_http):
        sala = cadastrar_sala(gestor_http, qtd_assentos=2)
        resposta = gestor_http.patch(
            f"/v1/salas/{sala['id']}",
            json={"qtd_assentos": 4},
            headers=token(gestor_http),
        )
        assert resposta.status_code == 200
        codigos = [a["codigo"] for a in gestor_http.get(f"/v1/salas/{sala['id']}").json()["assentos"]]
        assert codigos == ["A1", "A2", "A3", "A4"]

    def test_reduzir_assentos_com_reserva_retorna_409(self, gestor_http, cliente_http):
        sala = cadastrar_sala(gestor_http, qtd_assentos=3)
        filme = cadastrar_filme(gestor_http)
        sessao = criar_sessao(gestor_http, filme["id"], sala["id"]).json()
        assert reservar(cliente_http, sessao["id"], ["A3"]).status_code == 201
        resposta = gestor_http.patch(
            f"/v1/salas/{sala['id']}",
            json={"qtd_assentos": 2},
            headers=token(gestor_http),
        )
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "assentos_reservados"

    def test_exclui_sala_sem_sessoes(self, gestor_http):
        sala = cadastrar_sala(gestor_http)
        resposta = gestor_http.delete(f"/v1/salas/{sala['id']}", headers=token(gestor_http))
        assert resposta.status_code == 204

    def test_exclusao_de_sala_com_sessoes_e_recusada(self, gestor_http):
        sala = cadastrar_sala(gestor_http)
        filme = cadastrar_filme(gestor_http)
        criar_sessao(gestor_http, filme["id"], sala["id"])
        resposta = gestor_http.delete(f"/v1/salas/{sala['id']}", headers=token(gestor_http))
        assert resposta.status_code == 409
        assert resposta.json()["codigo"] == "sala_com_sessoes"


class TestRF13ListagemSalas:
    def test_busca_de_salas_por_nome(self, gestor_http):
        cadastrar_sala(gestor_http, nome="Sala IMAX")
        cadastrar_sala(gestor_http, nome="Sala Comum")
        nomes = [s["nome"] for s in gestor_http.get("/v1/salas", params={"q": "IMAX"}).json()["itens"]]
        assert nomes == ["Sala IMAX"]
