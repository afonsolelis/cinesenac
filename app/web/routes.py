"""Páginas server-rendered com Jinja2 (ADR-0017). Usam os mesmos serviços da API."""

import hashlib
import json
import uuid
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app import permissoes as p
from app.api.deps import abrir_sessao, csrf_token, encerrar_sessao, exigir, get_db, usuario_atual, verificar_csrf
from app.api.schemas import ClienteIn, FilmeIn, SessaoIn
from app.dominio.regras import rotulo_acessivel
from app.erros import ErroDominio, sem_permissao
from app.servicos import admin, catalogo, clientes, programacao, reservas
from app.servicos.autenticacao import entrar

DIRETORIO = Path(__file__).parent
TEMPLATES = Jinja2Templates(directory=DIRETORIO / "templates")
ROTA_POR_PERFIL = {"admin": "/admin", "gestor": "/gestor", "cliente": "/minhas-reservas"}


def moeda(valor) -> str:
    return "R$ " + f"{Decimal(str(valor)):.2f}".replace(".", ",")


def data_hora(valor: str) -> str:
    return str(valor).replace("T", " às ")


TEMPLATES.env.filters["moeda"] = moeda
TEMPLATES.env.filters["data_hora"] = data_hora
TEMPLATES.env.globals["rotulo_acessivel"] = rotulo_acessivel

router = APIRouter()


def _render(request: Request, db, nome: str, status: int = 200, **contexto):
    usuario = usuario_atual(request, db)
    dados = {"usuario": usuario, "csrf_token": csrf_token(request), **contexto}
    return TEMPLATES.TemplateResponse(request, nome, dados, status_code=status)


def renderizar_erro(request: Request, status: int, codigo: str, mensagem: str):
    return TEMPLATES.TemplateResponse(
        request, "erro.html",
        {"usuario": None, "csrf_token": "", "status": status, "codigo": codigo, "mensagem": mensagem},
        status_code=status,
    )


def _ip(request: Request) -> str:
    return request.client.host if request.client else "desconhecido"


def _hash_pedido(sessao_id: int, assentos: list[str]) -> str:
    canonico = json.dumps({"sessao_id": sessao_id, "assentos": assentos}, sort_keys=True)
    return hashlib.sha256(canonico.encode()).hexdigest()


# ---------- público ----------

@router.get("/")
def raiz():
    return RedirectResponse("/programacao", status_code=303)


@router.get("/programacao")
def pagina_programacao(request: Request, db=Depends(get_db)):
    itens, _ = programacao.programacao_publica(db, request.app.state.cache, {})
    return _render(request, db, "programacao.html", itens=itens)


@router.get("/entrar")
def pagina_entrar(request: Request, db=Depends(get_db)):
    return _render(request, db, "entrar.html", erro=None, email="")


@router.post("/entrar")
def entrar_pelo_formulario(request: Request, email: str = Form(...), senha: str = Form(...),
                           csrf: str = Form(alias="csrf_token"), db=Depends(get_db)):
    verificar_csrf(request, csrf)
    try:
        usuario = entrar(db, request.app.state.limitador, email=email, senha=senha, ip=_ip(request))
    except ErroDominio as erro:
        return _render(request, db, "entrar.html", status=erro.status, erro=erro.mensagem, email=email)
    abrir_sessao(request, usuario)
    return RedirectResponse(ROTA_POR_PERFIL[usuario.perfil], status_code=303)


@router.post("/sair")
def sair(request: Request, csrf: str = Form(alias="csrf_token")):
    verificar_csrf(request, csrf)
    encerrar_sessao(request)
    return RedirectResponse("/programacao", status_code=303)


@router.get("/cadastro")
def pagina_cadastro(request: Request, db=Depends(get_db)):
    return _render(request, db, "cadastro.html", erro=None)


@router.post("/cadastro")
def cadastrar_pelo_formulario(request: Request, nome: str = Form(""), email: str = Form(""),
                              idade: str = Form(""), senha: str = Form(""), logradouro: str = Form(""),
                              numero: str = Form(""), complemento: str = Form(""), bairro: str = Form(""),
                              cidade: str = Form(""), estado: str = Form(""), cep: str = Form(""),
                              csrf: str = Form(alias="csrf_token"), db=Depends(get_db)):
    verificar_csrf(request, csrf)
    try:
        dados = ClienteIn(
            nome=nome, email=email, idade=idade or 0, senha=senha,
            endereco={"logradouro": logradouro, "numero": numero, "complemento": complemento or None,
                      "bairro": bairro, "cidade": cidade, "estado": estado, "cep": cep},
        )
    except ValidationError:
        return _render(request, db, "cadastro.html", status=422,
                       erro="Dados inválidos. Revise o formulário.")
    try:
        cliente = clientes.cadastrar_cliente(
            db, email=dados.email, senha=dados.senha, nome=dados.nome, idade=dados.idade,
            endereco=dados.endereco.model_dump(),
        )
    except ErroDominio as erro:
        return _render(request, db, "cadastro.html", status=erro.status, erro=erro.mensagem)
    abrir_sessao(request, cliente.usuario)
    return RedirectResponse("/minhas-reservas", status_code=303)


# ---------- cliente ----------

@router.get("/sessoes/{sessao_id}")
def pagina_sessao(sessao_id: int, request: Request, usuario=Depends(exigir(p.RESERVAS_CRIAR)), db=Depends(get_db)):
    mapa = reservas.mapa(db, sessao_id)
    return _render(request, db, "sessao.html", mapa=mapa, chave=uuid.uuid4().hex, erro=None)


@router.post("/sessoes/{sessao_id}/reservas")
def reservar_pelo_formulario(sessao_id: int, request: Request,
                             assentos: list[str] = Form(default=[]), chave: str = Form(...),
                             csrf: str = Form(alias="csrf_token"),
                             usuario=Depends(exigir(p.RESERVAS_CRIAR)), db=Depends(get_db)):
    verificar_csrf(request, csrf)
    if usuario.cliente is None:
        raise sem_permissao()
    try:
        if not assentos:
            raise ErroDominio(422, "validacao", "Escolha ao menos um assento.", ["assentos"])
        confirmacao = reservas.reservar_assentos(
            db, cliente_id=usuario.cliente.id, sessao_id=sessao_id, codigos=assentos,
            chave=chave, corpo_hash=_hash_pedido(sessao_id, assentos),
        )
    except ErroDominio as erro:
        mapa = reservas.mapa(db, sessao_id)
        return _render(request, db, "sessao.html", status=erro.status, mapa=mapa,
                       chave=uuid.uuid4().hex, erro=erro.mensagem)
    return _render(request, db, "reserva_confirmada.html", reserva=confirmacao)


@router.get("/minhas-reservas")
def pagina_minhas_reservas(request: Request, usuario=Depends(exigir(p.RESERVAS_CRIAR)), db=Depends(get_db)):
    itens = reservas.minhas_reservas(db, usuario.cliente.id if usuario.cliente else None)
    return _render(request, db, "minhas_reservas.html", itens=itens)


@router.get("/minha-conta")
def pagina_minha_conta(request: Request, usuario=Depends(exigir(p.CADASTRO_PROPRIO)), db=Depends(get_db)):
    if usuario.cliente is None:
        raise sem_permissao()
    cliente = clientes.serializar_cliente(clientes.obter_cliente(db, usuario.cliente.id))
    return _render(request, db, "minha_conta.html", cliente=cliente)


# ---------- gestor ----------

def _painel_gestor(request: Request, db, *, erro=None, aviso=None, dia: date | None = None, status=200):
    dia = dia or date.today()
    return _render(
        request, db, "gestor.html", status=status, erro=erro, aviso=aviso,
        dia=dia, cota=programacao.cota_nacional(db, dia),
        filmes=catalogo.listar_filmes(db), salas=catalogo.listar_salas(db),
        sessoes=programacao.listar_sessoes(db, {}, somente_publicadas=False),
    )


@router.get("/gestor")
def pagina_gestor(request: Request, dia: date | None = Query(default=None),
                  aviso: str | None = None, usuario=Depends(exigir(p.PROGRAMACAO)), db=Depends(get_db)):
    return _painel_gestor(request, db, dia=dia, aviso=aviso)


@router.post("/gestor/filmes")
def cadastrar_filme_pelo_formulario(request: Request, titulo: str = Form(""), duracao_minutos: str = Form(""),
                                    genero: str = Form(""), sinopse: str = Form(""), cartaz_url: str = Form(""),
                                    faixa_etaria: str = Form(""), elenco: str = Form(""),
                                    nacionalidade: str = Form(""), csrf: str = Form(alias="csrf_token"),
                                    usuario=Depends(exigir(p.CATALOGO)), db=Depends(get_db)):
    verificar_csrf(request, csrf)
    try:
        dados = FilmeIn(titulo=titulo, duracao_minutos=duracao_minutos or 0, genero=genero, sinopse=sinopse,
                        cartaz_url=cartaz_url, faixa_etaria=faixa_etaria, elenco=elenco,
                        nacionalidade=nacionalidade).model_dump()
        catalogo.criar_filme(db, dados, autor_id=usuario.id)
    except (ValidationError, ErroDominio):
        return _painel_gestor(request, db, erro="Dados do filme inválidos. Revise o formulário.", status=422)
    return RedirectResponse("/gestor", status_code=303)


@router.post("/gestor/sessoes")
def cadastrar_sessao_pelo_formulario(request: Request, filme_id: int = Form(...), sala_id: int = Form(...),
                                     data_hora_inicio: str = Form(...), duracao_minutos: int = Form(...),
                                     valor_ingresso: str = Form(...), csrf: str = Form(alias="csrf_token"),
                                     usuario=Depends(exigir(p.PROGRAMACAO)), db=Depends(get_db)):
    verificar_csrf(request, csrf)
    try:
        dados = SessaoIn(filme_id=filme_id, sala_id=sala_id,
                         data_hora_inicio=datetime.fromisoformat(data_hora_inicio),
                         duracao_minutos=duracao_minutos, valor_ingresso=valor_ingresso)
        _, avisos = programacao.criar_sessao(
            db, filme_id=dados.filme_id, sala_id=dados.sala_id, data_hora_inicio=dados.data_hora_inicio,
            duracao_minutos=dados.duracao_minutos, valor_ingresso=str(dados.valor_ingresso),
        )
    except ValidationError:
        return _painel_gestor(request, db, erro="Dados da sessão inválidos.", status=422)
    except ErroDominio as erro:
        return _painel_gestor(request, db, erro=erro.mensagem, status=erro.status)
    destino = "/gestor?aviso=cota_nacional_pendente" if avisos else "/gestor"
    return RedirectResponse(destino, status_code=303)


@router.post("/gestor/publicar")
def publicar_pelo_formulario(request: Request, dia: date = Form(...), csrf: str = Form(alias="csrf_token"),
                             usuario=Depends(exigir(p.PROGRAMACAO)), db=Depends(get_db)):
    verificar_csrf(request, csrf)
    try:
        programacao.publicar_dia(db, dia, autor_id=usuario.id)
    except ErroDominio as erro:
        return _painel_gestor(request, db, erro=erro.mensagem, dia=dia, status=erro.status)
    return RedirectResponse(f"/gestor?dia={dia.isoformat()}", status_code=303)


# ---------- admin ----------

def _painel_admin(request: Request, db, *, erro=None, status=200):
    return _render(
        request, db, "admin.html", status=status, erro=erro,
        resumo=admin.dashboard(db), usuarios=admin.listar_usuarios(db),
        auditoria=admin.listar_auditoria(db, limite=20),
    )


@router.get("/admin")
def pagina_admin(request: Request, usuario=Depends(exigir(p.DASHBOARD)), db=Depends(get_db)):
    return _painel_admin(request, db)


@router.post("/admin/usuarios")
def criar_gestor_pelo_formulario(request: Request, email: str = Form(...), senha: str = Form(...),
                                 csrf: str = Form(alias="csrf_token"),
                                 usuario=Depends(exigir(p.USUARIOS)), db=Depends(get_db)):
    verificar_csrf(request, csrf)
    try:
        admin.criar_conta(db, email=email, senha=senha, perfil="gestor", cliente=None, autor_id=usuario.id)
    except ErroDominio as erro:
        return _painel_admin(request, db, erro=erro.mensagem, status=erro.status)
    return RedirectResponse("/admin", status_code=303)


@router.post("/admin/usuarios/{usuario_id}/ativo")
def alterar_ativo_pelo_formulario(usuario_id: int, request: Request, ativo: str = Form(...),
                                  csrf: str = Form(alias="csrf_token"),
                                  usuario=Depends(exigir(p.USUARIOS)), db=Depends(get_db)):
    verificar_csrf(request, csrf)
    admin.definir_ativo(db, usuario_id, ativo == "true", autor_id=usuario.id)
    return RedirectResponse("/admin", status_code=303)
