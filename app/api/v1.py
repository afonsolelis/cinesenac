"""API HTTP versionada /v1 (ADR-0002). Toda regra fica nos serviços; aqui só há tradução de HTTP."""

import hashlib
import json
from datetime import date

from fastapi import APIRouter, Depends, Header, Query, Request, Response
from fastapi.responses import JSONResponse

from app import permissoes as p
from app.api import deps
from app.api.deps import csrf_token, exigir, exigir_usuario, get_db, usuario_atual, verificar_csrf_api
from app.api.schemas import (
    ClienteIn, ClienteUpdate, FilmeIn, FilmeUpdate, LoginIn, PermissoesIn, ReservaIn,
    SalaIn, SalaUpdate, SessaoIn, SessaoUpdate, UsuarioIn, UsuarioUpdate,
)
from app.erros import ErroDominio, sem_permissao
from app.models import Usuario
from app.servicos import admin, catalogo, clientes, programacao, reservas
from app.servicos.autenticacao import entrar

router = APIRouter(prefix="/v1", dependencies=[Depends(verificar_csrf_api)])


def _usuario_publico(usuario: Usuario | None):
    return admin.serializar_usuario(usuario) if usuario else None


def _pode_acessar_cliente(usuario: Usuario, db, cliente_id: int) -> None:
    """RF07 e RNF29: o cliente só acessa o próprio cadastro. O admin acessa qualquer um (RNF32)."""
    if usuario.perfil == "admin":
        return
    proprio = usuario.cliente is not None and usuario.cliente.id == cliente_id
    if not proprio or p.CADASTRO_PROPRIO not in admin.permissoes_do_perfil(db, usuario.perfil):
        raise sem_permissao()


# ---------- sessão e autenticação ----------

@router.get("/sessao")
def ver_sessao(request: Request, usuario: Usuario | None = Depends(usuario_atual)):
    return {"usuario": _usuario_publico(usuario), "csrf_token": csrf_token(request)}


@router.post("/autenticacao")
def login(corpo: LoginIn, request: Request, db=Depends(get_db)):
    limitador = request.app.state.limitador
    ip = request.client.host if request.client else "desconhecido"
    usuario = entrar(db, limitador, email=corpo.email, senha=corpo.senha, ip=ip)
    deps.abrir_sessao(request, usuario)
    return {"usuario": _usuario_publico(usuario)}


@router.delete("/autenticacao", status_code=204)
def logout(request: Request):
    deps.encerrar_sessao(request)
    return Response(status_code=204)


# ---------- clientes (RF04 a RF07) ----------

@router.post("/clientes", status_code=201)
def cadastrar(corpo: ClienteIn, db=Depends(get_db)):
    cliente = clientes.cadastrar_cliente(
        db, email=corpo.email, senha=corpo.senha, nome=corpo.nome, idade=corpo.idade,
        endereco=corpo.endereco.model_dump(),
    )
    return clientes.serializar_cliente(cliente)


@router.get("/clientes/{cliente_id}")
def ver_cliente(cliente_id: int, usuario: Usuario = Depends(exigir_usuario), db=Depends(get_db)):
    _pode_acessar_cliente(usuario, db, cliente_id)
    return clientes.serializar_cliente(clientes.obter_cliente(db, cliente_id))


@router.patch("/clientes/{cliente_id}")
def editar_cliente(cliente_id: int, corpo: ClienteUpdate, usuario: Usuario = Depends(exigir_usuario),
                   db=Depends(get_db)):
    _pode_acessar_cliente(usuario, db, cliente_id)
    endereco = corpo.endereco.model_dump(exclude_unset=True) if corpo.endereco else None
    cliente = clientes.atualizar_cliente(
        db, cliente_id, email=corpo.email, idade=corpo.idade, endereco=endereco,
    )
    return clientes.serializar_cliente(cliente)


# ---------- catálogo (RF08 a RF13) ----------

@router.get("/filmes")
def listar_filmes(q: str | None = None, usuario=Depends(exigir(p.CATALOGO)), db=Depends(get_db)):
    return {"itens": [catalogo.serializar_filme(f) for f in catalogo.listar_filmes(db, q)]}


@router.post("/filmes", status_code=201)
def criar_filme(corpo: FilmeIn, usuario=Depends(exigir(p.CATALOGO)), db=Depends(get_db)):
    filme = catalogo.criar_filme(db, corpo.model_dump(), autor_id=usuario.id)
    return catalogo.serializar_filme(filme)


@router.patch("/filmes/{filme_id}")
def editar_filme(filme_id: int, corpo: FilmeUpdate, usuario=Depends(exigir(p.CATALOGO)), db=Depends(get_db)):
    filme = catalogo.atualizar_filme(db, filme_id, corpo.model_dump(exclude_unset=True), autor_id=usuario.id)
    return catalogo.serializar_filme(filme)


@router.delete("/filmes/{filme_id}", status_code=204)
def excluir_filme(filme_id: int, usuario=Depends(exigir(p.CATALOGO)), db=Depends(get_db)):
    catalogo.excluir_filme(db, filme_id, autor_id=usuario.id)
    return Response(status_code=204)


@router.get("/salas")
def listar_salas(q: str | None = None, usuario=Depends(exigir(p.CATALOGO)), db=Depends(get_db)):
    return {"itens": [catalogo.serializar_sala(s) for s in catalogo.listar_salas(db, q)]}


@router.post("/salas", status_code=201)
def criar_sala(corpo: SalaIn, usuario=Depends(exigir(p.CATALOGO)), db=Depends(get_db)):
    sala = catalogo.criar_sala(db, corpo.model_dump(), autor_id=usuario.id)
    return catalogo.serializar_sala(sala, com_assentos=True)


@router.get("/salas/{sala_id}")
def ver_sala(sala_id: int, usuario=Depends(exigir(p.CATALOGO)), db=Depends(get_db)):
    return catalogo.serializar_sala(catalogo.obter_sala(db, sala_id), com_assentos=True)


@router.patch("/salas/{sala_id}")
def editar_sala(sala_id: int, corpo: SalaUpdate, usuario=Depends(exigir(p.CATALOGO)), db=Depends(get_db)):
    sala = catalogo.atualizar_sala(db, sala_id, corpo.model_dump(exclude_unset=True), autor_id=usuario.id)
    return catalogo.serializar_sala(sala, com_assentos=True)


@router.delete("/salas/{sala_id}", status_code=204)
def excluir_sala(sala_id: int, usuario=Depends(exigir(p.CATALOGO)), db=Depends(get_db)):
    catalogo.excluir_sala(db, sala_id, autor_id=usuario.id)
    return Response(status_code=204)


# ---------- programação (RF03, RF14 a RF19) ----------

@router.get("/sessoes")
def listar_sessoes(sala_id: int | None = None, filme_id: int | None = None,
                   inicio: date | None = None, fim: date | None = None,
                   usuario=Depends(exigir(p.PROGRAMACAO)), db=Depends(get_db)):
    filtros = {"sala_id": sala_id, "filme_id": filme_id, "inicio": inicio, "fim": fim}
    return {"itens": programacao.listar_sessoes(db, filtros, somente_publicadas=False)}


@router.post("/sessoes", status_code=201)
def criar_sessao(corpo: SessaoIn, usuario=Depends(exigir(p.PROGRAMACAO)), db=Depends(get_db)):
    sessao, avisos = programacao.criar_sessao(
        db, filme_id=corpo.filme_id, sala_id=corpo.sala_id, data_hora_inicio=corpo.data_hora_inicio,
        duracao_minutos=corpo.duracao_minutos, valor_ingresso=str(corpo.valor_ingresso),
    )
    return {**programacao.serializar_sessao(sessao), "avisos": avisos}


@router.patch("/sessoes/{sessao_id}")
def editar_sessao(sessao_id: int, corpo: SessaoUpdate, usuario=Depends(exigir(p.PROGRAMACAO)), db=Depends(get_db)):
    alteracoes = corpo.model_dump(exclude_unset=True)
    if "valor_ingresso" in alteracoes:
        alteracoes["valor_ingresso"] = str(alteracoes["valor_ingresso"])
    sessao = programacao.atualizar_sessao(db, sessao_id, alteracoes)
    return programacao.serializar_sessao(sessao)


@router.post("/sessoes/{sessao_id}/cancelamento")
def cancelar_sessao(sessao_id: int, usuario=Depends(exigir(p.PROGRAMACAO)), db=Depends(get_db)):
    sessao = programacao.cancelar_sessao(db, sessao_id, autor_id=usuario.id)
    return {"id": sessao.id, "cancelada": sessao.cancelada}


@router.get("/programacao")
def programacao_publica(request: Request, response: Response, sala_id: int | None = None,
                        filme_id: int | None = None, inicio: date | None = None, fim: date | None = None,
                        db=Depends(get_db)):
    filtros = {"sala_id": sala_id, "filme_id": filme_id, "inicio": inicio, "fim": fim}
    itens, em_cache = programacao.programacao_publica(db, request.app.state.cache, filtros)
    response.headers["X-Cache"] = "HIT" if em_cache else "MISS"
    return {"itens": itens}


@router.get("/programacao/{dia}/cota-nacional")
def cota_nacional(dia: date, usuario=Depends(exigir(p.PROGRAMACAO)), db=Depends(get_db)):
    return programacao.cota_nacional(db, dia)


@router.post("/programacao/{dia}/publicacao")
def publicar_dia(dia: date, usuario=Depends(exigir(p.PROGRAMACAO)), db=Depends(get_db)):
    return programacao.publicar_dia(db, dia, autor_id=usuario.id)


# ---------- reservas (RF20 a RF26, RF30) ----------

@router.get("/sessoes/{sessao_id}/assentos")
def mapa_de_assentos(sessao_id: int, usuario=Depends(exigir(p.RESERVAS_CRIAR)), db=Depends(get_db)):
    return reservas.mapa(db, sessao_id)


def _hash_pedido(corpo: ReservaIn) -> str:
    canonico = json.dumps({"sessao_id": corpo.sessao_id, "assentos": corpo.assentos}, sort_keys=True)
    return hashlib.sha256(canonico.encode()).hexdigest()


@router.post("/reservas", status_code=201)
def criar_reserva(corpo: ReservaIn, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
                  usuario=Depends(exigir(p.RESERVAS_CRIAR)), db=Depends(get_db)):
    if not idempotency_key:
        raise ErroDominio(422, "cabecalho_obrigatorio", "O cabeçalho Idempotency-Key é obrigatório.",
                          ["Idempotency-Key"])
    if usuario.cliente is None:
        raise sem_permissao()
    return reservas.reservar_assentos(
        db, cliente_id=usuario.cliente.id, sessao_id=corpo.sessao_id, codigos=corpo.assentos,
        chave=idempotency_key, corpo_hash=_hash_pedido(corpo),
    )


@router.get("/minhas-reservas")
def minhas_reservas(usuario=Depends(exigir(p.RESERVAS_CRIAR)), db=Depends(get_db)):
    cliente_id = usuario.cliente.id if usuario.cliente else None
    return {"itens": reservas.minhas_reservas(db, cliente_id)}


@router.get("/reservas")
def reservas_do_cliente(cliente_id: int = Query(), usuario=Depends(exigir(p.RESERVAS_GERENCIAR)),
                        db=Depends(get_db)):
    return {"itens": reservas.listar_reservas_do_cliente(db, cliente_id)}


@router.delete("/reservas/{reserva_id}", status_code=204)
def cancelar_reserva(reserva_id: int, usuario=Depends(exigir(p.RESERVAS_GERENCIAR)), db=Depends(get_db)):
    reservas.cancelar_reserva(db, reserva_id, autor_id=usuario.id)
    return Response(status_code=204)


# ---------- administração (RF27 a RF29) ----------

@router.get("/usuarios")
def listar_usuarios(usuario=Depends(exigir(p.USUARIOS)), db=Depends(get_db)):
    return {"itens": admin.listar_usuarios(db)}


@router.post("/usuarios", status_code=201)
def criar_usuario(corpo: UsuarioIn, usuario=Depends(exigir(p.USUARIOS)), db=Depends(get_db)):
    cliente = corpo.cliente.model_dump() if corpo.cliente else None
    return admin.criar_conta(
        db, email=corpo.email, senha=corpo.senha, perfil=corpo.perfil, cliente=cliente, autor_id=usuario.id,
    )


@router.patch("/usuarios/{usuario_id}")
def atualizar_usuario(usuario_id: int, corpo: UsuarioUpdate, usuario=Depends(exigir(p.USUARIOS)),
                      db=Depends(get_db)):
    return admin.definir_ativo(db, usuario_id, corpo.ativo, autor_id=usuario.id)


@router.delete("/usuarios/{usuario_id}", status_code=204)
def excluir_usuario(usuario_id: int, usuario=Depends(exigir(p.USUARIOS)), db=Depends(get_db)):
    admin.excluir_conta(db, usuario_id, autor_id=usuario.id)
    return Response(status_code=204)


@router.get("/perfis/{perfil}/permissoes")
def ver_permissoes(perfil: str, usuario=Depends(exigir(p.PERMISSOES)), db=Depends(get_db)):
    return admin.obter_permissoes(db, perfil)


@router.put("/perfis/{perfil}/permissoes")
def definir_permissoes(perfil: str, corpo: PermissoesIn, usuario=Depends(exigir(p.PERMISSOES)),
                       db=Depends(get_db)):
    return admin.definir_permissoes(db, perfil, corpo.permissoes, autor_id=usuario.id)


@router.get("/dashboard")
def dashboard(usuario=Depends(exigir(p.DASHBOARD)), db=Depends(get_db)):
    return admin.dashboard(db)


@router.get("/auditoria")
def auditoria(usuario=Depends(exigir(p.AUDITORIA)), db=Depends(get_db)):
    return {"itens": admin.listar_auditoria(db)}
