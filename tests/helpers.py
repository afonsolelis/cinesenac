"""Funções auxiliares para os testes. Não contêm regra de negócio."""

import uuid

ADMIN_EMAIL = "admin@cinesenac.test"
ADMIN_SENHA = "senha-admin-forte-123"
GESTOR_EMAIL = "gestor@cinesenac.test"
GESTOR_SENHA = "senha-gestor-forte-123"
CLIENTE_EMAIL = "ana@exemplo.com"
CLIENTE_SENHA = "senha-cliente-forte-123"

ENDERECO = {
    "logradouro": "Rua das Flores",
    "numero": "100",
    "complemento": None,
    "bairro": "Centro",
    "cidade": "São Paulo",
    "estado": "SP",
    "cep": "01000-000",
}


def token(client):
    """Cabeçalho CSRF da sessão atual do cliente de teste."""
    resposta = client.get("/v1/sessao")
    return {"X-CSRF-Token": resposta.json()["csrf_token"]}


def login(client, email, senha):
    resposta = client.post(
        "/v1/autenticacao",
        json={"email": email, "senha": senha},
        headers=token(client),
    )
    assert resposta.status_code == 200, resposta.text
    return resposta.json()["usuario"]


def logout(client):
    resposta = client.delete("/v1/autenticacao", headers=token(client))
    assert resposta.status_code == 204, resposta.text


def cadastrar_cliente(client, email=CLIENTE_EMAIL, senha=CLIENTE_SENHA, nome="Ana", idade=30):
    resposta = client.post(
        "/v1/clientes",
        json={
            "email": email,
            "senha": senha,
            "nome": nome,
            "idade": idade,
            "endereco": ENDERECO,
        },
        headers=token(client),
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def cadastrar_filme(gestor, titulo="Filme Nacional", nacionalidade="NACIONAL", **extra):
    dados = {
        "titulo": titulo,
        "duracao_minutos": 120,
        "genero": "Drama",
        "sinopse": "Uma história de teste.",
        "cartaz_url": "https://img.exemplo.com/cartaz.jpg",
        "faixa_etaria": "LIVRE",
        "elenco": "Elenco de teste",
        "nacionalidade": nacionalidade,
    }
    dados.update(extra)
    resposta = gestor.post("/v1/filmes", json=dados, headers=token(gestor))
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def cadastrar_sala(gestor, nome="Sala 1", qtd_assentos=10, **extra):
    dados = {
        "nome": nome,
        "qtd_assentos": qtd_assentos,
        "hora_abertura": "14:00",
        "hora_fechamento": "23:59",
        "especificacao_tecnica": "2D",
    }
    dados.update(extra)
    resposta = gestor.post("/v1/salas", json=dados, headers=token(gestor))
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def criar_sessao(gestor, filme_id, sala_id, inicio="2026-11-02T19:00:00", duracao=120, valor="25.00"):
    return gestor.post(
        "/v1/sessoes",
        json={
            "filme_id": filme_id,
            "sala_id": sala_id,
            "data_hora_inicio": inicio,
            "duracao_minutos": duracao,
            "valor_ingresso": valor,
        },
        headers=token(gestor),
    )


def publicar_dia(gestor, dia="2026-11-02"):
    return gestor.post(f"/v1/programacao/{dia}/publicacao", headers=token(gestor))


def reservar(cliente, sessao_id, codigos, chave=None):
    """Reserva assentos. Gera uma Idempotency-Key nova quando não for informada."""
    cabecalhos = token(cliente)
    cabecalhos["Idempotency-Key"] = chave or str(uuid.uuid4())
    return cliente.post(
        "/v1/reservas",
        json={"sessao_id": sessao_id, "assentos": codigos},
        headers=cabecalhos,
    )
