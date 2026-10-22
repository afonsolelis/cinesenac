"""Dependências compartilhadas: banco, sessão, CSRF e permissões (ADR-0009, ADR-0012, ADR-0013)."""

import secrets

from fastapi import Depends, Request

from app.erros import ErroDominio, nao_autenticado, sem_permissao
from app.models import Usuario
from app.servicos.admin import permissoes_do_perfil

CHAVE_CSRF = "csrf"


def get_db(request: Request):
    with request.app.state.sessionmaker() as db:
        yield db


def csrf_token(request: Request) -> str:
    token = request.session.get(CHAVE_CSRF)
    if not token:
        token = secrets.token_urlsafe(32)
        request.session[CHAVE_CSRF] = token
    return token


def verificar_csrf(request: Request, recebido: str | None) -> None:
    esperado = request.session.get(CHAVE_CSRF)
    if not esperado or not recebido or not secrets.compare_digest(esperado, recebido):
        raise ErroDominio(403, "csrf_invalido", "Requisição recusada. Recarregue a página e tente de novo.")


def verificar_csrf_api(request: Request) -> None:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    verificar_csrf(request, request.headers.get("X-CSRF-Token"))


def abrir_sessao(request: Request, usuario: Usuario) -> None:
    request.session.clear()
    request.session.update({"uid": usuario.id, "ver": usuario.sessao_versao})
    csrf_token(request)


def encerrar_sessao(request: Request) -> None:
    request.session.clear()


def usuario_atual(request: Request, db=Depends(get_db)) -> Usuario | None:
    uid = request.session.get("uid")
    if uid is None:
        return None
    usuario = db.get(Usuario, uid)
    if usuario is None or not usuario.ativo or usuario.sessao_versao != request.session.get("ver"):
        request.session.clear()  # RNF28: sessão de conta desativada deixa de valer
        return None
    return usuario


def exigir_usuario(usuario: Usuario | None = Depends(usuario_atual)) -> Usuario:
    if usuario is None:
        raise nao_autenticado()
    return usuario


def exigir(permissao: str):
    def dependencia(usuario: Usuario = Depends(exigir_usuario), db=Depends(get_db)) -> Usuario:
        if permissao not in permissoes_do_perfil(db, usuario.perfil):
            raise sem_permissao()
        return usuario

    return dependencia
