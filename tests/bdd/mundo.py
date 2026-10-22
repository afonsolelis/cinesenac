"""Estado de cada cenário BDD: atores HTTP, respostas, identificadores e objetos sob teste.

Cada cenário recebe um Mundo novo, com banco próprio em diretório temporário.
Os atores são clientes HTTP separados, cada um com seu próprio cookie de sessão.
"""

import json
import re
from datetime import datetime

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.servicos.usuarios import criar_usuario
from tests.helpers import (
    ADMIN_EMAIL, ADMIN_SENHA, CLIENTE_EMAIL, CLIENTE_SENHA, GESTOR_EMAIL, GESTOR_SENHA,
    cadastrar_cliente, cadastrar_filme, cadastrar_sala, criar_sessao, login, token,
)

METODOS_COM_CSRF = {"POST", "PUT", "PATCH", "DELETE"}
DATA_BASE = "2026-11-02"


def data_hora(texto: str) -> datetime:
    """Aceita 'HH:MM' (dia 2026-11-02) ou ISO completo."""
    if re.fullmatch(r"\d{2}:\d{2}", texto):
        return datetime.fromisoformat(f"{DATA_BASE}T{texto}:00")
    return datetime.fromisoformat(texto)


def chave_sessao(alias: str) -> str:
    return f"sessao:{alias}"


class Mundo:
    def __init__(self, diretorio, monkeypatch):
        self.diretorio = diretorio
        self.monkeypatch = monkeypatch
        self.reconfiguracao = {}
        self.versao_banco = 0
        self.tempo = [0.0]
        self.resultados = []
        self.tentativas = []
        self.resultado = None
        self.erro_valor = None
        self.erro_dominio = None
        self.hash = None
        self.configuracao = None
        self.cache = None
        self.limitador = None
        self.controle = None
        self.resposta = None
        self.resposta_anterior = None
        self.html = ""
        self.construir()

    # ---------- aplicação ----------

    def agora(self) -> float:
        return self.tempo[0]

    def construir(self):
        """Cria uma aplicação nova, com banco próprio. Usado na partida e em reconfigurações."""
        self.versao_banco += 1
        base = dict(
            secret_key="chave-bdd-com-tamanho-suficiente-0123456789abcdef",
            database_url=f"sqlite:///{self.diretorio / f'bdd-{self.versao_banco}.db'}",
            https_only=False,
            cache_ttl_seconds=0,
            login_max_tentativas=5,
            login_janela_segundos=900,
            max_requisicoes_simultaneas=200,
        )
        base.update(self.reconfiguracao)
        self.app = create_app(Settings(**base))
        with self.app.state.sessionmaker() as db:
            criar_usuario(db, email=ADMIN_EMAIL, senha=ADMIN_SENHA, perfil="admin")
        self.atores = {}
        self.ids = {}

    def reconfigurar(self, **alteracoes):
        self.reconfiguracao.update(alteracoes)
        self.construir()

    # ---------- atores ----------

    def ator(self, nome: str) -> TestClient:
        if nome in self.atores:
            return self.atores[nome]
        if nome == "visitante":
            cliente = TestClient(self.app)
        elif nome == "admin":
            cliente = TestClient(self.app)
            login(cliente, ADMIN_EMAIL, ADMIN_SENHA)
        elif nome == "gestor":
            self.criar_gestor(GESTOR_EMAIL, GESTOR_SENHA)
            cliente = TestClient(self.app)
            login(cliente, GESTOR_EMAIL, GESTOR_SENHA)
        elif nome == "cliente":
            cliente, usuario = self.novo_cliente(CLIENTE_EMAIL, CLIENTE_SENHA, "Ana")
            self.ids["cliente_id"] = usuario["cliente_id"]
        elif nome == "outro cliente":
            cliente, usuario = self.novo_cliente("bruno@exemplo.com", CLIENTE_SENHA, "Bruno")
            self.ids["outro_cliente_id"] = usuario["cliente_id"]
        else:
            raise KeyError(f"ator desconhecido: {nome}")
        self.atores[nome] = cliente
        return cliente

    def novo_cliente(self, email, senha, nome):
        cadastrar_cliente(TestClient(self.app), email=email, senha=senha, nome=nome)
        cliente = TestClient(self.app)
        usuario = login(cliente, email, senha)
        return cliente, usuario

    def criar_gestor(self, email, senha):
        admin = self.ator("admin")
        resposta = admin.post("/v1/usuarios", json={"email": email, "senha": senha, "perfil": "gestor"},
                              headers=token(admin))
        assert resposta.status_code == 201, resposta.text

    def id_usuario(self, email: str) -> int:
        usuarios = self.ator("admin").get("/v1/usuarios").json()["itens"]
        return next(u["id"] for u in usuarios if u["email"] == email)

    # ---------- requisições ----------

    def resolver(self, texto: str) -> str:
        """Troca {id:alias} pelo identificador guardado e {cliente_id} pelo cliente da cena."""
        texto = re.sub(r"\{id:([^}]+)\}", lambda m: str(self.buscar_id(m.group(1))), texto)
        return texto.replace("{cliente_id}", str(self.ids.get("cliente_id", "")))

    def buscar_id(self, nome: str):
        """Aceita o nome cru ou com prefixo: 'Ensaio' encontra 'sessao:Ensaio', 'filme:Ensaio' etc."""
        for chave in (nome, chave_sessao(nome), f"filme:{nome}", f"sala:{nome}"):
            if chave in self.ids:
                return self.ids[chave]
        raise KeyError(nome)

    def requisitar(self, ator, metodo, caminho, *, corpo=None, cabecalhos=None, csrf=True):
        cliente = self.ator(ator)
        cabecalhos = dict(cabecalhos or {})
        if csrf and metodo in METODOS_COM_CSRF:
            cabecalhos.setdefault("X-CSRF-Token", token(cliente)["X-CSRF-Token"])
        dados = json.loads(self.resolver(corpo)) if corpo is not None else None
        return self._registrar(cliente.request(metodo, self.resolver(caminho), json=dados, headers=cabecalhos,
                                               follow_redirects=False))

    def enviar_formulario(self, ator, caminho, campos: dict):
        cliente = self.ator(ator)
        campos = dict(campos)
        campos.setdefault("csrf_token", self.csrf_da_pagina())
        if "chave" not in campos and 'name="chave"' in self.html:
            campos["chave"] = re.search(r'name="chave" value="([^"]+)"', self.html).group(1)
        if "assentos" in campos:
            campos["assentos"] = campos["assentos"].split(",")
        return self._registrar(cliente.post(self.resolver(caminho), data=campos, follow_redirects=False))

    def _registrar(self, resposta):
        self.resposta_anterior = self.resposta
        self.resposta = resposta
        if "text/html" in resposta.headers.get("content-type", ""):
            self.html = resposta.text
        return resposta

    def csrf_da_pagina(self) -> str:
        return re.search(r'name="csrf_token" value="([^"]+)"', self.html).group(1)

    @staticmethod
    def campo(dados, caminho: str):
        """Resolve caminhos como 'usuario.perfil' e 'itens[].assento' (o [] mapeia listas)."""
        atuais = [dados]
        mapeado = False
        for parte in caminho.split("."):
            if parte.endswith("[]"):
                mapeado = True
                atuais = [item for atual in atuais for item in atual[parte[:-2]]]
            else:
                atuais = [atual[parte] for atual in atuais]
        return atuais if mapeado else atuais[0]

    # ---------- pré-condições ----------

    def filme(self, titulo, nacionalidade="NACIONAL"):
        filme = cadastrar_filme(self.ator("gestor"), titulo=titulo, nacionalidade=nacionalidade)
        self.ids[f"filme:{titulo}"] = filme["id"]

    def sala(self, nome, quantidade):
        sala = cadastrar_sala(self.ator("gestor"), nome=nome, qtd_assentos=quantidade)
        self.ids[f"sala:{nome}"] = sala["id"]

    def sessao(self, alias, titulo, sala, inicio, duracao, valor):
        resposta = criar_sessao(
            self.ator("gestor"), self.ids[f"filme:{titulo}"], self.ids[f"sala:{sala}"],
            inicio=data_hora(inicio).isoformat(), duracao=duracao, valor=valor,
        )
        assert resposta.status_code == 201, resposta.text
        self.ids[chave_sessao(alias)] = resposta.json()["id"]
        return resposta.json()

    def cancelar_reserva_de(self, ator, assento):
        """Localiza a reserva do assento na lista do cliente e a cancela como o ator informado."""
        minhas = self.ator("cliente").get("/v1/minhas-reservas").json()["itens"]
        reserva = next(r for r in minhas if r["assento"] == assento)
        return self.requisitar(ator, "DELETE", f"/v1/reservas/{reserva['id']}")

    def id_conta(self, email: str) -> int:
        return self.id_usuario(email)

    def reservar_como(self, ator, alias, assentos):
        cliente = self.ator(ator)
        cabecalhos = {"X-CSRF-Token": token(cliente)["X-CSRF-Token"],
                      "Idempotency-Key": f"chave-{alias}-{'-'.join(assentos)}"}
        return self._registrar(cliente.post(
            "/v1/reservas",
            json={"sessao_id": self.ids[chave_sessao(alias)], "assentos": assentos},
            headers=cabecalhos,
        ))
