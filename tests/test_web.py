"""Front end server-rendered (Jinja2, ADR-0017) e cabeçalhos de segurança (RNF31).

Cobre: programação pública, login por formulário, controle de acesso às páginas,
mapa de assentos acessível (RNF19), confirmação de reserva (RF25), escape de HTML
e cabeçalhos das páginas.
"""

import re

from tests.helpers import (
    cadastrar_filme,
    cadastrar_sala,
    criar_sessao,
    publicar_dia,
    token,
)


def _csrf_da_pagina(html):
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def _sessao_publicada(gestor, titulo="Filme Nacional"):
    filme = cadastrar_filme(gestor, titulo=titulo)
    sala = cadastrar_sala(gestor, nome="Sala 1", qtd_assentos=3)
    sessao = criar_sessao(gestor, filme["id"], sala["id"]).json()
    publicar_dia(gestor)
    return sessao


class TestProgramacaoPublica:
    def test_pagina_declara_idioma_e_viewport_para_celular(self, visitante_http):
        html = visitante_http.get("/programacao").text
        assert 'lang="pt-BR"' in html
        assert 'name="viewport"' in html
        assert "Programação" in html

    def test_mostra_filmes_publicados(self, gestor_http, visitante_http):
        _sessao_publicada(gestor_http, titulo="Filme em Cartaz")
        assert "Filme em Cartaz" in visitante_http.get("/programacao").text

    def test_escapa_html_de_titulos(self, gestor_http, visitante_http):
        _sessao_publicada(gestor_http, titulo="<b>Negrito</b>")
        html = visitante_http.get("/programacao").text
        assert "&lt;b&gt;Negrito&lt;/b&gt;" in html
        assert "<b>Negrito</b>" not in html

    def test_raiz_redireciona_para_programacao(self, visitante_http):
        resposta = visitante_http.get("/", follow_redirects=False)
        assert resposta.status_code in (302, 303, 307)
        assert resposta.headers["location"] == "/programacao"


class TestLoginPorFormulario:
    def test_formulario_de_login_tem_token_csrf(self, visitante_http):
        html = visitante_http.get("/entrar").text
        assert _csrf_da_pagina(html)

    def test_login_com_formulario_redireciona_para_a_area_do_perfil(self, app, visitante_http):
        from tests.helpers import ADMIN_EMAIL, ADMIN_SENHA

        html = visitante_http.get("/entrar").text
        resposta = visitante_http.post(
            "/entrar",
            data={"email": ADMIN_EMAIL, "senha": ADMIN_SENHA, "csrf_token": _csrf_da_pagina(html)},
            follow_redirects=False,
        )
        assert resposta.status_code == 303
        assert resposta.headers["location"] == "/admin"

    def test_login_com_senha_errada_mostra_mensagem_generica(self, visitante_http):
        html = visitante_http.get("/entrar").text
        resposta = visitante_http.post(
            "/entrar",
            data={"email": "x@exemplo.com", "senha": "errada-123456", "csrf_token": _csrf_da_pagina(html)},
        )
        assert resposta.status_code == 401
        assert "E-mail ou senha inválidos" in resposta.text


class TestControleDeAcessoDasPaginas:
    def test_area_restrita_sem_login_redireciona_para_entrar(self, visitante_http):
        resposta = visitante_http.get("/gestor", follow_redirects=False)
        assert resposta.status_code == 303
        assert resposta.headers["location"] == "/entrar"

    def test_area_de_outro_perfil_retorna_403_em_html(self, cliente_http):
        resposta = cliente_http.get("/gestor")
        assert resposta.status_code == 403
        assert "Acesso negado" in resposta.text


class TestMapaEReservaPelaPagina:
    def test_mapa_tem_assentos_com_rotulo_acessivel(self, gestor_http, cliente_http):
        sessao = _sessao_publicada(gestor_http)
        html = cliente_http.get(f"/sessoes/{sessao['id']}").text
        assert 'aria-label="Fila A, assento 1, livre"' in html
        assert 'aria-label="Fila A, assento 3, livre"' in html

    def test_mapa_exige_login_de_cliente(self, gestor_http, visitante_http):
        sessao = _sessao_publicada(gestor_http)
        resposta = visitante_http.get(f"/sessoes/{sessao['id']}", follow_redirects=False)
        assert resposta.status_code == 303
        assert resposta.headers["location"] == "/entrar"

    def test_reserva_pelo_formulario_mostra_confirmacao_com_valor(self, gestor_http, cliente_http):
        sessao = _sessao_publicada(gestor_http)
        html = cliente_http.get(f"/sessoes/{sessao['id']}").text
        chave = re.search(r'name="chave" value="([^"]+)"', html).group(1)
        resposta = cliente_http.post(
            f"/sessoes/{sessao['id']}/reservas",
            data={"assentos": ["A1", "A2"], "chave": chave, "csrf_token": _csrf_da_pagina(html)},
        )
        assert resposta.status_code == 200
        assert "Reserva confirmada" in resposta.text
        assert "R$ 50,00" in resposta.text
        assert "A1" in resposta.text and "A2" in resposta.text

    def test_minhas_reservas_mostra_a_reserva(self, gestor_http, cliente_http):
        sessao = _sessao_publicada(gestor_http, titulo="Minha Sessão")
        html = cliente_http.get(f"/sessoes/{sessao['id']}").text
        chave = re.search(r'name="chave" value="([^"]+)"', html).group(1)
        cliente_http.post(
            f"/sessoes/{sessao['id']}/reservas",
            data={"assentos": ["A3"], "chave": chave, "csrf_token": _csrf_da_pagina(html)},
        )
        pagina = cliente_http.get("/minhas-reservas").text
        assert "Minha Sessão" in pagina
        assert "A3" in pagina


class TestPaineisDoGestorEAdmin:
    def test_painel_do_gestor_mostra_indicador_de_cota(self, gestor_http):
        html = gestor_http.get("/gestor").text
        assert "Cota de filme nacional" in html

    def test_painel_admin_mostra_dashboard(self, admin_http):
        html = admin_http.get("/admin").text
        assert "Usuários" in html and "Reservas" in html


class TestCabecalhosDeSeguranca:
    def test_paginas_enviam_csp_e_protecoes(self, visitante_http):
        resposta = visitante_http.get("/programacao")
        assert "default-src 'self'" in resposta.headers["Content-Security-Policy"]
        assert resposta.headers["X-Content-Type-Options"] == "nosniff"
        assert resposta.headers["X-Frame-Options"] == "DENY"

    def test_cookie_de_sessao_nao_vaza_para_script(self, app, visitante_http):
        from tests.helpers import ADMIN_EMAIL, ADMIN_SENHA

        html = visitante_http.get("/entrar").text
        resposta = visitante_http.post(
            "/entrar",
            data={"email": ADMIN_EMAIL, "senha": ADMIN_SENHA, "csrf_token": _csrf_da_pagina(html)},
            follow_redirects=False,
        )
        assert "httponly" in resposta.headers["set-cookie"].lower()


class TestCadastroPelaPagina:
    """RF04 pela interface: o visitante cria a conta pelo formulário e já entra."""

    DADOS = {
        "nome": "Carla", "email": "carla@exemplo.com", "idade": "28", "senha": "senha-carla-forte-123",
        "logradouro": "Av. Central", "numero": "50", "complemento": "", "bairro": "Sé",
        "cidade": "São Paulo", "estado": "SP", "cep": "01001-000",
    }

    def test_cadastro_pelo_formulario_cria_conta_e_redireciona_para_minhas_reservas(self, visitante_http):
        html = visitante_http.get("/cadastro").text
        resposta = visitante_http.post(
            "/cadastro",
            data={**self.DADOS, "csrf_token": _csrf_da_pagina(html)},
            follow_redirects=False,
        )
        assert resposta.status_code == 303
        assert resposta.headers["location"] == "/minhas-reservas"
        assert "Carla" in visitante_http.get("/minha-conta").text

    def test_cadastro_com_email_duplicado_mostra_erro(self, visitante_http, cliente_http):
        html = visitante_http.get("/cadastro").text
        resposta = visitante_http.post(
            "/cadastro",
            data={**self.DADOS, "email": "ana@exemplo.com", "csrf_token": _csrf_da_pagina(html)},
        )
        assert resposta.status_code == 409
        assert "Este e-mail já está cadastrado" in resposta.text

    def test_cadastro_com_dados_invalidos_mostra_erro_sem_criar_conta(self, visitante_http):
        html = visitante_http.get("/cadastro").text
        resposta = visitante_http.post(
            "/cadastro",
            data={**self.DADOS, "idade": "0", "csrf_token": _csrf_da_pagina(html)},
        )
        assert resposta.status_code == 422
        assert "Revise o formulário" in resposta.text


class TestMinhaContaSemCadastro:
    def test_admin_sem_cadastro_de_cliente_recebe_403_na_minha_conta(self, admin_http):
        resposta = admin_http.get("/minha-conta")
        assert resposta.status_code == 403
