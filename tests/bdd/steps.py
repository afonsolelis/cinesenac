"""Definições de passos Gherkin (pytest-bdd). Expressões regulares ancoradas, sem ambiguidade."""

import json
import threading
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, then, when

from app.cli import criar_admin_inicial
from app.config import Settings
from app.dominio.regras import (
    cota_nacional_atendida, gerar_codigos_assentos, intervalos_se_sobrepoem, rotulo_acessivel,
)
from app.erros import ErroDominio
from app.infra.admissao import ControleAdmissao
from app.infra.cache import CacheTTL
from app.infra.limitacao import LimitadorTentativas
from app.infra.seguranca import gerar_hash_senha, verificar_senha
from app.servicos.clientes import cadastrar_cliente as servico_cadastrar
from app.servicos.reservas import reservar_assentos
from tests.bdd.mundo import chave_sessao, data_hora
from tests.helpers import ENDERECO, GESTOR_SENHA, CLIENTE_SENHA, cadastrar_cliente, login, token

ATOR = r"(?P<ator>admin|gestor|cliente|outro cliente|visitante)"


def _n(texto):
    return int(texto)


def _literal(texto):
    return json.loads(texto)


# ======================================================================================
# GIVEN: pré-condições
# ======================================================================================

@given(parsers.re(r"^que o sistema está em execução$"))
def dado_sistema_em_execucao(mundo):
    assert mundo.app is not None


@given(parsers.re(r"^que o (?P<ator>admin|gestor|cliente|outro cliente) está autenticado$"))
def dado_ator_autenticado(mundo, ator):
    mundo.ator(ator)


@given(parsers.re(r"^que o visitante acessa o sistema$"))
def dado_visitante(mundo):
    mundo.ator("visitante")


@given(parsers.re(r'^que existe um gestor "(?P<email>[^"]+)"$'))
def dado_existe_gestor(mundo, email):
    mundo.criar_gestor(email, GESTOR_SENHA)


@given(parsers.re(r'^que existe um cliente com e-mail "(?P<email>[^"]+)"$'))
def dado_existe_cliente(mundo, email):
    registro = cadastrar_cliente(mundo.ator("visitante"), email=email)
    mundo.ids[f"cliente:{email}"] = registro["id"]


@given(parsers.re(r'^que a conta "(?P<email>[^"]+)" foi desativada pelo admin$'))
def dado_conta_desativada(mundo, email):
    admin_http = mundo.ator("admin")
    resposta = admin_http.patch(f"/v1/usuarios/{mundo.id_usuario(email)}", json={"ativo": False},
                                headers=token(admin_http))
    assert resposta.status_code == 200, resposta.text


@given(parsers.re(r'^que o visitante errou a senha de "(?P<email>[^"]+)" (?P<n>\d+) vezes$'))
def dado_senha_errada_varias_vezes(mundo, email, n):
    for _ in range(_n(n)):
        resposta = mundo.requisitar("visitante", "POST", "/v1/autenticacao",
                                    corpo=json.dumps({"email": email, "senha": "errada-123456"}))
        assert resposta.status_code == 401


@given(parsers.re(r'^que existe um filme "(?P<titulo>[^"]+)"$'))
def dado_existe_filme(mundo, titulo):
    mundo.filme(titulo)


@given(parsers.re(r'^que existe um filme internacional "(?P<titulo>[^"]+)"$'))
def dado_existe_filme_internacional(mundo, titulo):
    mundo.filme(titulo, nacionalidade="INTERNACIONAL")


@given(parsers.re(r'^que existe uma sala "(?P<nome>[^"]+)" com (?P<n>\d+) assentos$'))
def dado_existe_sala(mundo, nome, n):
    mundo.sala(nome, _n(n))


@given(parsers.re(
    r'^que existe uma sessão "(?P<alias>[^"]+)" do filme "(?P<titulo>[^"]+)" na sala "(?P<sala>[^"]+)" '
    r'em "(?P<inicio>[^"]+)" com (?P<duracao>\d+) minutos e valor "(?P<valor>[^"]+)"$'))
def dado_existe_sessao(mundo, alias, titulo, sala, inicio, duracao, valor):
    mundo.sessao(alias, titulo, sala, inicio, _n(duracao), valor)


@given(parsers.re(r'^que o dia "(?P<dia>[^"]+)" está publicado$'))
def dado_dia_publicado(mundo, dia):
    resposta = mundo.requisitar("gestor", "POST", f"/v1/programacao/{dia}/publicacao")
    assert resposta.status_code == 200, resposta.text


@given(parsers.re(r'^que o (?P<ator>cliente|outro cliente) reservou "(?P<assentos>[^"]+)" na sessão "(?P<alias>[^"]+)"$'))
def dado_cliente_reservou(mundo, ator, assentos, alias):
    resposta = mundo.reservar_como(ator, alias, assentos.split(", "))
    assert resposta.status_code == 201, resposta.text


@given(parsers.re(r'^que a sessão "(?P<alias>[^"]+)" foi cancelada$'))
def dado_sessao_cancelada(mundo, alias):
    resposta = mundo.requisitar("gestor", "POST", f"/v1/sessoes/{{id:{chave_sessao(alias)}}}/cancelamento")
    assert resposta.status_code == 200, resposta.text


@given(parsers.re(r"^que a programação pública tem cache de (?P<ttl>\d+) segundos$"))
def dado_cache_ttl(mundo, ttl):
    mundo.reconfigurar(cache_ttl_seconds=_n(ttl))


@given(parsers.re(r"^que o limite de requisições simultâneas é (?P<n>\d+)$"))
def dado_limite_simultaneas(mundo, n):
    mundo.reconfigurar(max_requisicoes_simultaneas=_n(n))


@given(parsers.re(r'^que a variável "(?P<nome>[^"]+)" vale "(?P<valor>[^"]*)"$'))
def dado_variavel(mundo, nome, valor):
    mundo.monkeypatch.setenv(nome, valor)


@given(parsers.re(r'^que a variável "(?P<nome>[^"]+)" não está definida$'))
def dado_variavel_ausente(mundo, nome):
    mundo.monkeypatch.delenv(nome, raising=False)


@when(parsers.re(rf'^o {ATOR} cancela a reserva de "(?P<assento>[^"]+)" do cliente$'))
def quando_cancela_reserva(mundo, ator, assento):
    mundo.cancelar_reserva_de(ator, assento)


@when(parsers.re(r'^o admin altera a situação da conta "(?P<email>[^"]+)" para (?P<situacao>ativada|desativada)$'))
def quando_altera_situacao(mundo, email, situacao):
    admin_http = mundo.ator("admin")
    mundo._registrar(admin_http.patch(f"/v1/usuarios/{mundo.id_conta(email)}",
                                      json={"ativo": situacao == "ativada"}, headers=token(admin_http)))


@when(parsers.re(r'^o admin exclui a conta "(?P<email>[^"]+)"$'))
def quando_exclui_conta(mundo, email):
    admin_http = mundo.ator("admin")
    mundo._registrar(admin_http.delete(f"/v1/usuarios/{mundo.id_conta(email)}", headers=token(admin_http)))


@when(parsers.re(r"^eu limpo o cache$"))
def quando_limpa_cache(mundo):
    mundo.cache.limpar()


@given(parsers.re(r"^um cache com TTL de (?P<ttl>\d+) segundos$"))
def dado_cache(mundo, ttl):
    mundo.cache = CacheTTL(ttl_segundos=_n(ttl), relogio=mundo.agora)


@given(parsers.re(r"^um limitador de (?P<max>\d+) tentativas em (?P<janela>\d+) segundos$"))
def dado_limitador(mundo, max, janela):
    mundo.limitador = LimitadorTentativas(max_tentativas=_n(max), janela_segundos=_n(janela),
                                          relogio=mundo.agora)


@given(parsers.re(r"^um controle de admissão com (?P<n>\d+) vaga$"))
def dado_admissao(mundo, n):
    mundo.controle = ControleAdmissao(max_simultaneas=_n(n))


# ======================================================================================
# WHEN: ações
# ======================================================================================

@when(parsers.re(rf'^o {ATOR} envia (?P<metodo>GET|DELETE|POST) "(?P<caminho>[^"]+)"$'))
def quando_envia_sem_corpo(mundo, ator, metodo, caminho):
    mundo.requisitar(ator, metodo, caminho)


@when(parsers.re(rf'^o {ATOR} envia GET "(?P<caminho>[^"]+)" com o cabeçalho "(?P<nome>[^"]+)" igual a "(?P<valor>[^"]+)"$'))
def quando_envia_get_com_cabecalho(mundo, ator, caminho, nome, valor):
    mundo.requisitar(ator, "GET", caminho, cabecalhos={nome: valor})


@when(parsers.re(rf'^o {ATOR} envia (?P<metodo>POST|PUT|PATCH) "(?P<caminho>[^"]+)" com os dados:$'))
def quando_envia_com_dados(mundo, ator, metodo, caminho, docstring):
    mundo.requisitar(ator, metodo, caminho, corpo=docstring)


@when(parsers.re(rf'^o {ATOR} envia POST "(?P<caminho>[^"]+)" sem token CSRF com os dados:$'))
def quando_envia_sem_csrf(mundo, ator, caminho, docstring):
    mundo.requisitar(ator, "POST", caminho, corpo=docstring, csrf=False)


@when(parsers.re(rf'^o {ATOR} envia POST "(?P<caminho>[^"]+)" com o token CSRF de outra sessão e os dados:$'))
def quando_envia_com_csrf_alheio(mundo, ator, caminho, docstring):
    alheio = token(TestClient(mundo.app))["X-CSRF-Token"]
    mundo.requisitar(ator, "POST", caminho, corpo=docstring, cabecalhos={"X-CSRF-Token": alheio}, csrf=False)


@when(parsers.re(rf'^o visitante tenta entrar com "(?P<email>[^"]+)" e senha "(?P<senha>[^"]+)"$'))
def quando_tenta_entrar(mundo, email, senha):
    mundo.requisitar("visitante", "POST", "/v1/autenticacao",
                     corpo=json.dumps({"email": email, "senha": senha}))


@when(parsers.re(rf'^o {ATOR} abre a página "(?P<caminho>[^"]+)"$'))
def quando_abre_pagina(mundo, ator, caminho):
    mundo.requisitar(ator, "GET", caminho)


@when(parsers.re(rf'^o {ATOR} envia o formulário "(?P<caminho>[^"]+)" com os campos:$'))
def quando_envia_formulario(mundo, ator, caminho, datatable):
    cabecalho, *linhas = datatable
    campos = {linha[cabecalho.index("campo")]: linha[cabecalho.index("valor")] for linha in linhas}
    mundo.enviar_formulario(ator, caminho, campos)


@when(parsers.re(rf'^o {ATOR} reserva "(?P<assentos>[^"]+)" na sessão "(?P<alias>[^"]+)" com a chave "(?P<chave>[^"]+)"$'))
def quando_reserva_com_chave(mundo, ator, assentos, alias, chave):
    cliente = mundo.ator(ator)
    resposta = cliente.post(
        "/v1/reservas",
        json={"sessao_id": mundo.ids[chave_sessao(alias)], "assentos": assentos.split(", ")},
        headers={"X-CSRF-Token": token(cliente)["X-CSRF-Token"], "Idempotency-Key": chave},
    )
    mundo._registrar(resposta)


@when(parsers.re(rf'^o {ATOR} reserva "(?P<assentos>[^"]+)" na sessão "(?P<alias>[^"]+)" sem chave de idempotência$'))
def quando_reserva_sem_chave(mundo, ator, assentos, alias):
    cliente = mundo.ator(ator)
    resposta = cliente.post(
        "/v1/reservas",
        json={"sessao_id": mundo.ids[chave_sessao(alias)], "assentos": assentos.split(", ")},
        headers={"X-CSRF-Token": token(cliente)["X-CSRF-Token"]},
    )
    mundo._registrar(resposta)


@when(parsers.re(r"^(?P<n>\d+) clientes disputam o assento \"(?P<assento>[^\"]+)\" da sessão \"(?P<alias>[^\"]+)\" ao mesmo tempo$"))
def quando_disputam_assento(mundo, n, assento, alias):
    total = _n(n)
    visitante = mundo.ator("visitante")
    ids = [cadastrar_cliente(visitante, email=f"c{i}@exemplo.com", nome=f"Cliente {i}")["id"] for i in range(total)]
    barreira = threading.Barrier(total)
    sessao_id = mundo.ids[chave_sessao(alias)]

    def tentar(cliente_id):
        barreira.wait()
        with mundo.app.state.sessionmaker() as db:
            try:
                reservar_assentos(db, cliente_id=cliente_id, sessao_id=sessao_id, codigos=[assento],
                                  chave=f"chave-{cliente_id}", corpo_hash=f"corpo-{cliente_id}")
                return "sucesso"
            except ErroDominio as erro:
                return erro.codigo

    with ThreadPoolExecutor(max_workers=total) as pool:
        mundo.resultados = list(pool.map(tentar, ids))


@when(parsers.re(r'^um cliente reserva "(?P<assento>[^"]+)" nas sessões "(?P<a>[^"]+)" e "(?P<b>[^"]+)" ao mesmo tempo$'))
def quando_mesmo_cliente_disputa(mundo, assento, a, b):
    cliente_id = cadastrar_cliente(mundo.ator("visitante"), email="paralelo@exemplo.com")["id"]
    barreira = threading.Barrier(2)

    def tentar(alias):
        barreira.wait()
        with mundo.app.state.sessionmaker() as db:
            try:
                reservar_assentos(db, cliente_id=cliente_id, sessao_id=mundo.ids[chave_sessao(alias)],
                                  codigos=[assento], chave=f"chave-{alias}", corpo_hash=f"corpo-{alias}")
                return "sucesso"
            except ErroDominio as erro:
                return erro.codigo

    with ThreadPoolExecutor(max_workers=2) as pool:
        mundo.resultados = list(pool.map(tentar, [a, b]))


@when(parsers.re(r'^(?P<n>\d+) cadastros com o e-mail "(?P<email>[^"]+)" são feitos ao mesmo tempo$'))
def quando_cadastros_concorrentes(mundo, n, email):
    total = _n(n)
    barreira = threading.Barrier(total)

    def tentar(indice):
        barreira.wait()
        with mundo.app.state.sessionmaker() as db:
            try:
                servico_cadastrar(db, email=email, senha=CLIENTE_SENHA, nome=f"Cliente {indice}",
                                  idade=30, endereco=dict(ENDERECO))
                return "sucesso"
            except ErroDominio as erro:
                return erro.codigo

    with ThreadPoolExecutor(max_workers=total) as pool:
        mundo.resultados = list(pool.map(tentar, range(total)))


@when(parsers.re(r'^eu verifico se os intervalos "(?P<ia>[^"]+)" por (?P<da>\d+) minutos e "(?P<ib>[^"]+)" por (?P<db>\d+) minutos se sobrepõem$'))
def quando_verifica_sobreposicao(mundo, ia, da, ib, db):
    mundo.resultado = intervalos_se_sobrepoem(data_hora(ia), _n(da), data_hora(ib), _n(db))


@when(parsers.re(r"^eu gero os códigos de (?P<n>\d+) assentos$"))
def quando_gera_codigos(mundo, n):
    try:
        mundo.resultado = gerar_codigos_assentos(_n(n))
    except ValueError as erro:
        mundo.erro_valor = str(erro)


@when(parsers.re(r'^eu avalio a cota com as nacionalidades "(?P<lista>[^"]*)"$'))
def quando_avalia_cota(mundo, lista):
    mundo.resultado = cota_nacional_atendida(lista.split(",") if lista else [])


@when(parsers.re(r'^eu monto o rótulo do assento "(?P<codigo>[^"]+)" como "(?P<estado>[^"]+)"$'))
def quando_monta_rotulo(mundo, codigo, estado):
    mundo.resultado = rotulo_acessivel(codigo, estado)


@when(parsers.re(r'^eu guardo "(?P<valor>[^"]+)" na chave "(?P<chave>[^"]+)"$'))
def quando_guarda_cache(mundo, valor, chave):
    mundo.cache.definir(chave, valor)


@when(parsers.re(r'^eu consulto a chave "(?P<chave>[^"]+)"$'))
def quando_consulta_cache(mundo, chave):
    mundo.resultado = mundo.cache.obter(chave)


@when(parsers.re(r"^o relógio avança (?P<s>\d+) segundos$"))
def quando_relogio_avanca(mundo, s):
    mundo.tempo[0] += _n(s)


@when(parsers.re(r'^eu registro (?P<n>\d+) falhas para "(?P<chave>[^"]+)"$'))
def quando_registra_falhas(mundo, n, chave):
    for _ in range(_n(n)):
        mundo.limitador.registrar_falha(chave)


@when(parsers.re(r'^eu registro um sucesso para "(?P<chave>[^"]+)"$'))
def quando_registra_sucesso(mundo, chave):
    mundo.limitador.registrar_sucesso(chave)


@when(parsers.re(r'^eu consulto o bloqueio de "(?P<chave>[^"]+)"$'))
def quando_consulta_bloqueio(mundo, chave):
    mundo.resultado = mundo.limitador.bloqueado(chave)


@when(parsers.re(r"^eu tento entrar$"))
def quando_tenta_entrar_admissao(mundo):
    mundo.tentativas.append(mundo.controle.tentar_entrar())


@when(parsers.re(r"^eu saio$"))
def quando_sai_admissao(mundo):
    mundo.controle.sair()


@when(parsers.re(r'^eu gero o hash da senha "(?P<senha>[^"]+)"$'))
def quando_gera_hash(mundo, senha):
    mundo.hash = gerar_hash_senha(senha)


@when(parsers.re(r'^eu verifico a senha "(?P<senha>[^"]+)" contra o hash gerado$'))
def quando_verifica_hash_gerado(mundo, senha):
    mundo.resultado = verificar_senha(mundo.hash, senha)


@when(parsers.re(r'^eu verifico a senha "(?P<senha>[^"]+)" contra o valor "(?P<valor>[^"]+)"$'))
def quando_verifica_valor(mundo, senha, valor):
    mundo.resultado = verificar_senha(valor, senha)


@when(parsers.re(r"^eu carrego a configuração do ambiente$"))
def quando_carrega_configuracao(mundo):
    try:
        mundo.configuracao = Settings.from_env()
    except ValueError as erro:
        mundo.erro_valor = str(erro)


@when(parsers.re(r'^eu crio a configuração com a chave "(?P<chave>[^"]*)"$'))
def quando_cria_configuracao(mundo, chave):
    try:
        mundo.configuracao = Settings(secret_key=chave)
    except ValueError as erro:
        mundo.erro_valor = str(erro)


@when(parsers.re(r'^eu executo a criação do administrador "(?P<email>[^"]+)" com a senha "(?P<senha>[^"]+)"$'))
def quando_cria_admin_cli(mundo, email, senha):
    try:
        criar_admin_inicial(mundo.app.state.sessionmaker, email, senha)
    except ErroDominio as erro:
        mundo.erro_dominio = erro


# ======================================================================================
# THEN: verificações
# ======================================================================================

@then(parsers.re(r"^a resposta tem status (?P<status>\d+)$"))
def entao_status(mundo, status):
    assert mundo.resposta.status_code == _n(status), mundo.resposta.text


@then(parsers.re(r'^o código de erro é "(?P<codigo>[^"]+)"$'))
def entao_codigo(mundo, codigo):
    assert mundo.resposta.json()["codigo"] == codigo, mundo.resposta.text


@then(parsers.re(r'^a mensagem de erro é "(?P<mensagem>[^"]+)"$'))
def entao_mensagem(mundo, mensagem):
    assert mundo.resposta.json()["mensagem"] == mensagem


@then(parsers.re(r'^o campo "(?P<campo>[^"]+)" é (?P<valor>.+)$'))
def entao_campo_igual(mundo, campo, valor):
    obtido = mundo.campo(mundo.resposta.json(), campo)
    assert obtido == _literal(valor), f"{campo}={obtido!r}"


@then(parsers.re(r'^o campo "(?P<campo>[^"]+)" contém "(?P<texto>[^"]+)"$'))
def entao_campo_contem(mundo, campo, texto):
    obtido = mundo.campo(mundo.resposta.json(), campo)
    if isinstance(obtido, list):
        assert any(texto == item or texto in str(item) for item in obtido), obtido
    else:
        assert texto in str(obtido), obtido


@then(parsers.re(r'^o campo "(?P<campo>[^"]+)" tem os valores "(?P<valores>[^"]*)"$'))
def entao_campo_valores(mundo, campo, valores):
    obtido = mundo.campo(mundo.resposta.json(), campo)
    esperado = valores.split(", ") if valores else []
    assert [str(v) for v in obtido] == esperado, obtido


@then(parsers.re(r'^o campo "(?P<campo>[^"]+)" tem (?P<n>\d+) itens$'))
def entao_campo_tamanho(mundo, campo, n):
    assert len(mundo.campo(mundo.resposta.json(), campo)) == _n(n)


@then(parsers.re(r'^o campo "(?P<campo>[^"]+)" está vazio$'))
def entao_campo_vazio(mundo, campo):
    assert mundo.campo(mundo.resposta.json(), campo) in ([], None, {})


@then(parsers.re(r'^o cabeçalho "(?P<nome>[^"]+)" existe$'))
def entao_cabecalho_existe(mundo, nome):
    assert mundo.resposta.headers.get(nome)


@then(parsers.re(r'^o cabeçalho "(?P<nome>[^"]+)" é "(?P<valor>[^"]+)"$'))
def entao_cabecalho_igual(mundo, nome, valor):
    assert mundo.resposta.headers[nome] == valor


@then(parsers.re(r'^o cabeçalho "(?P<nome>[^"]+)" contém "(?P<texto>[^"]+)"$'))
def entao_cabecalho_contem(mundo, nome, texto):
    # Atributos de cookie e cabeçalhos HTTP não diferenciam caixa (o Starlette escreve 'httponly').
    assert texto.lower() in mundo.resposta.headers[nome].lower()


@then(parsers.re(r'^a resposta redireciona para "(?P<caminho>[^"]+)"$'))
def entao_redireciona(mundo, caminho):
    assert mundo.resposta.status_code == 303
    assert mundo.resposta.headers["location"] == caminho


@then(parsers.re(r'^a página contém "(?P<texto>[^"]+)"$'))
def entao_pagina_contem(mundo, texto):
    assert texto in mundo.html


@then(parsers.re(r'^a página não contém "(?P<texto>[^"]+)"$'))
def entao_pagina_nao_contem(mundo, texto):
    assert texto not in mundo.html


@then(parsers.re(r'^a página tem o idioma "(?P<idioma>[^"]+)" e viewport para celular$'))
def entao_pagina_idioma(mundo, idioma):
    assert f'lang="{idioma}"' in mundo.html
    assert 'name="viewport"' in mundo.html


@then(parsers.re(r"^o cookie de sessão é HttpOnly e SameSite Lax$"))
def entao_cookie(mundo):
    cookie = mundo.resposta.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie


@then(parsers.re(r"^o corpo da resposta é igual ao da resposta anterior$"))
def entao_corpo_igual(mundo):
    assert mundo.resposta.json() == mundo.resposta_anterior.json()


@then(parsers.re(rf'^o assento "(?P<codigo>[^"]+)" da sessão "(?P<alias>[^"]+)" está (?P<estado>livre|ocupado)$'))
def entao_assento_estado(mundo, codigo, alias, estado):
    mapa = mundo.ator("cliente").get(f"/v1/sessoes/{mundo.ids[chave_sessao(alias)]}/assentos").json()
    ocupacao = {a["codigo"]: a["ocupado"] for a in mapa["assentos"]}
    assert ocupacao[codigo] == (estado == "ocupado")


@then(parsers.re(r'^o resultado da disputa tem exatamente (?P<ok>\d+) sucesso e (?P<n>\d+) "(?P<codigo>[^"]+)"$'))
def entao_resultado_disputa(mundo, ok, n, codigo):
    assert mundo.resultados.count("sucesso") == _n(ok), mundo.resultados
    assert mundo.resultados.count(codigo) == _n(n), mundo.resultados


@then(parsers.re(r"^as duas respostas têm as mesmas reservas$"))
def entao_mesmas_reservas(mundo):
    assert mundo.resposta.json()["reservas"] == mundo.resposta_anterior.json()["reservas"]


@then(parsers.re(r'^o administrador vê a ação "(?P<acao>[^"]+)" na auditoria$'))
def entao_auditoria(mundo, acao):
    acoes = [r["acao"] for r in mundo.ator("admin").get("/v1/auditoria").json()["itens"]]
    assert acao in acoes


@then(parsers.re(r'^a conta "(?P<email>[^"]+)" não existe$'))
def entao_conta_inexistente(mundo, email):
    usuarios = mundo.ator("admin").get("/v1/usuarios").json()["itens"]
    assert all(u["email"] != email for u in usuarios)


@then(parsers.re(r'^a conta "(?P<email>[^"]+)" está (?P<estado>ativa|desativada)$'))
def entao_conta_estado(mundo, email, estado):
    usuarios = mundo.ator("admin").get("/v1/usuarios").json()["itens"]
    conta = next(u for u in usuarios if u["email"] == email)
    assert conta["ativo"] == (estado == "ativa")


@then(parsers.re(r'^"(?P<email>[^"]+)" consegue entrar com a senha "(?P<senha>[^"]+)"$'))
def entao_consegue_entrar(mundo, email, senha):
    cliente = TestClient(mundo.app)
    resposta = cliente.post("/v1/autenticacao", json={"email": email, "senha": senha},
                            headers={"X-CSRF-Token": token(cliente)["X-CSRF-Token"]})
    assert resposta.status_code == 200
    assert resposta.json()["usuario"]["perfil"] == "admin"


@then(parsers.re(r"^o contrato OpenAPI expõe \"(?P<caminho>[^\"]+)\"$"))
def entao_openapi_expoe(mundo, caminho):
    assert caminho in mundo.resposta.json()["paths"]


@then(parsers.re(r'^o contrato OpenAPI só expõe caminhos "(?P<a>[^"]+)" e "(?P<b>[^"]+)"$'))
def entao_openapi_so_expoe(mundo, a, b):
    assert all(c.startswith((a, b)) for c in mundo.resposta.json()["paths"])


@then(parsers.re(r'^a configuração tem (?P<campo>\w+) igual a (?P<valor>.+)$'))
def entao_configuracao(mundo, campo, valor):
    assert getattr(mundo.configuracao, campo) == _literal(valor)


@then(parsers.re(r'^ocorre um erro de valor que contém "(?P<texto>[^"]+)"$'))
def entao_erro_valor(mundo, texto):
    assert mundo.erro_valor is not None and texto in mundo.erro_valor, mundo.erro_valor


@then(parsers.re(r'^ocorre um erro de domínio com o código "(?P<codigo>[^"]+)"$'))
def entao_erro_dominio(mundo, codigo):
    assert mundo.erro_dominio is not None and mundo.erro_dominio.codigo == codigo


@then(parsers.re(r"^o resultado é (?P<valor>.+)$"))
def entao_resultado(mundo, valor):
    assert mundo.resultado == _literal(valor), mundo.resultado


@then(parsers.re(r"^a tentativa (?P<n>\d+) retorna (?P<valor>.+)$"))
def entao_tentativa(mundo, n, valor):
    assert mundo.tentativas[_n(n) - 1] == _literal(valor)


@then(parsers.re(r'^o hash não contém "(?P<senha>[^"]+)"$'))
def entao_hash_nao_contem(mundo, senha):
    assert senha not in mundo.hash


@then(parsers.re(r'^o campo "(?P<campo>[^"]+)" não existe$'))
def entao_campo_ausente(mundo, campo):
    try:
        mundo.campo(mundo.resposta.json(), campo)
    except KeyError:
        return
    raise AssertionError(f"o campo {campo} existe")


@then(parsers.re(r'^o campo "(?P<campo>[^"]+)" não é null$'))
def entao_campo_nao_null(mundo, campo):
    assert mundo.campo(mundo.resposta.json(), campo) is not None


@then(parsers.re(r'^o campo "(?P<campo>[^"]+)" é um número$'))
def entao_campo_numero(mundo, campo):
    assert isinstance(mundo.campo(mundo.resposta.json(), campo), int)


@then(parsers.re(r'^o campo "(?P<campo>[^"]+)" é maior ou igual a (?P<n>\d+)$'))
def entao_campo_minimo(mundo, campo, n):
    assert mundo.campo(mundo.resposta.json(), campo) >= _n(n)


@then(parsers.re(r'^o campo "(?P<campo>[^"]+)" não contém "(?P<texto>[^"]+)"$'))
def entao_campo_nao_contem(mundo, campo, texto):
    obtido = mundo.campo(mundo.resposta.json(), campo)
    if isinstance(obtido, list):
        assert not any(texto == item or texto in str(item) for item in obtido), obtido
    else:
        assert texto not in str(obtido), obtido


@then(parsers.re(r'^a página contém o rótulo "(?P<texto>[^"]+)"$'))
def entao_pagina_rotulo(mundo, texto):
    assert f'aria-label="{texto}"' in mundo.html


@then(parsers.re(r'^a página contém o campo "(?P<nome>[^"]+)"$'))
def entao_pagina_campo(mundo, nome):
    assert f'name="{nome}"' in mundo.html


@then(parsers.re(r'^a resposta contém a mensagem "(?P<mensagem>[^"]+)"$'))
def entao_resposta_contem(mundo, mensagem):
    assert mensagem in mundo.resposta.json()["mensagem"]
