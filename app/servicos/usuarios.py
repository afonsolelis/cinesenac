"""Contas de acesso: criação, verificação de credenciais (RF01, RF27, ADR-0012)."""

import re

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.erros import ErroDominio, validacao
from app.infra.seguranca import gerar_hash_senha, verificar_senha
from app.models import Usuario
from app.permissoes import PERFIS

TAMANHO_MINIMO_SENHA = 12
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_HASH_FICTICIO = gerar_hash_senha("senha-ficticia-para-tempo-constante")


def validar_email(email: str) -> None:
    if not _EMAIL.match(email or ""):
        raise validacao("E-mail inválido.", ["email"])


def validar_senha(senha: str) -> None:
    if not senha or len(senha) < TAMANHO_MINIMO_SENHA:
        raise validacao(f"A senha precisa ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres.", ["senha"])


def criar_usuario(db, *, email: str, senha: str, perfil: str, commit: bool = True) -> Usuario:
    validar_email(email)
    validar_senha(senha)
    if perfil not in PERFIS:
        raise validacao("Perfil inválido.", ["perfil"])
    if db.scalar(select(Usuario).where(Usuario.email == email)) is not None:
        raise ErroDominio(409, "email_duplicado", "Este e-mail já está cadastrado.", ["email"])
    usuario = Usuario(email=email, senha_hash=gerar_hash_senha(senha), perfil=perfil, ativo=True)
    db.add(usuario)
    try:
        db.flush()
        if commit:
            db.commit()
    except IntegrityError:
        db.rollback()
        raise ErroDominio(409, "email_duplicado", "Este e-mail já está cadastrado.", ["email"])
    return usuario


def autenticar(db, *, email: str, senha: str) -> Usuario | None:
    """Devolve o usuário se as credenciais conferem e a conta está ativa."""
    usuario = db.scalar(select(Usuario).where(Usuario.email == email))
    if usuario is None:
        verificar_senha(_HASH_FICTICIO, senha)  # tempo parecido com o de conta existente
        return None
    if not verificar_senha(usuario.senha_hash, senha) or not usuario.ativo:
        return None
    return usuario
