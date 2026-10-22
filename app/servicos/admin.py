"""Administração: contas, permissões, dashboard e auditoria (RF27 a RF29, RF28, RNF33)."""

from sqlalchemy import func, select

from app.erros import ErroDominio, nao_encontrado, validacao
from app.models import (
    Cliente, Filme, PerfilPermissao, RegistroAuditoria, RegistroIdempotencia, Reserva, Sala, Sessao, Usuario,
)
from app import permissoes as p
from app.servicos import auditoria
from app.servicos.clientes import cadastrar_cliente
from app.servicos.usuarios import criar_usuario


def garantir_permissoes_padrao(db) -> None:
    """Preenche as permissões padrão de cada perfil que ainda não tem nenhuma (RF28)."""
    for perfil in p.PERFIS:
        if db.scalar(select(func.count(PerfilPermissao.permissao)).where(PerfilPermissao.perfil == perfil)) == 0:
            db.add_all(PerfilPermissao(perfil=perfil, permissao=c) for c in p.PADRAO[perfil])
    db.commit()


def permissoes_do_perfil(db, perfil: str | None) -> set[str]:
    if perfil is None:
        return set()
    return set(db.scalars(select(PerfilPermissao.permissao).where(PerfilPermissao.perfil == perfil)))


def listar_usuarios(db) -> list[dict]:
    return [serializar_usuario(u) for u in db.scalars(select(Usuario).order_by(Usuario.id))]


def criar_conta(db, *, email, senha, perfil, cliente: dict | None, autor_id: int) -> dict:
    if perfil == "cliente":
        if not cliente:
            raise validacao("Dados de cadastro do cliente são obrigatórios.", ["cliente"])
        registro = cadastrar_cliente(
            db, email=email, senha=senha, nome=cliente["nome"], idade=cliente["idade"],
            endereco=cliente["endereco"], autor_id=autor_id, commit=True,
        )
        return serializar_usuario(registro.usuario)
    usuario = criar_usuario(db, email=email, senha=senha, perfil=perfil, commit=False)
    auditoria.registrar(db, autor_id=autor_id, acao="usuario.criar", alvo=f"usuario:{usuario.email}")
    db.commit()
    return serializar_usuario(usuario)


def definir_ativo(db, usuario_id: int, ativo: bool, autor_id: int) -> dict:
    if usuario_id == autor_id and not ativo:
        raise ErroDominio(409, "operacao_nao_permitida", "Você não pode desativar a própria conta.")
    usuario = _obter_usuario(db, usuario_id)
    usuario.ativo = ativo
    if not ativo:
        # Invalida as sessões existentes desta conta (RNF28).
        usuario.sessao_versao += 1
    auditoria.registrar(db, autor_id=autor_id, acao="usuario.ativar" if ativo else "usuario.desativar",
                        alvo=f"usuario:{usuario.id}")
    db.commit()
    return serializar_usuario(usuario)


def excluir_conta(db, usuario_id: int, autor_id: int) -> None:
    if usuario_id == autor_id:
        raise ErroDominio(409, "operacao_nao_permitida", "Você não pode excluir a própria conta.")
    usuario = _obter_usuario(db, usuario_id)
    cliente = usuario.cliente
    if cliente is not None:
        if db.scalar(select(func.count(Reserva.id)).where(Reserva.cliente_id == cliente.id)):
            raise ErroDominio(409, "conta_com_reservas",
                              "A conta possui reservas. Desative-a em vez de excluir.")
        db.query(RegistroIdempotencia).filter(RegistroIdempotencia.cliente_id == cliente.id).delete()
        db.delete(cliente)
    alvo = f"usuario:{usuario.email}"
    db.delete(usuario)
    auditoria.registrar(db, autor_id=autor_id, acao="usuario.excluir", alvo=alvo)
    db.commit()


def obter_permissoes(db, perfil: str) -> dict:
    if perfil not in p.PERFIS:
        raise nao_encontrado("Perfil")
    return {
        "perfil": perfil,
        "permissoes": sorted(permissoes_do_perfil(db, perfil)),
        "disponiveis": list(p.TODAS),
    }


def definir_permissoes(db, perfil: str, permissoes: list[str], autor_id: int) -> dict:
    if perfil not in p.PERFIS:
        raise nao_encontrado("Perfil")
    desconhecidas = [x for x in permissoes if x not in p.TODAS]
    if desconhecidas:
        raise validacao(f"Permissões desconhecidas: {', '.join(desconhecidas)}.", ["permissoes"])
    if perfil == "admin" and not set(p.OBRIGATORIAS_ADMIN) <= set(permissoes):
        raise ErroDominio(422, "permissao_obrigatoria",
                          "O perfil Admin precisa manter a permissão de gerenciar permissões.", ["permissoes"])
    db.query(PerfilPermissao).filter(PerfilPermissao.perfil == perfil).delete()
    db.add_all(PerfilPermissao(perfil=perfil, permissao=x) for x in sorted(set(permissoes)))
    auditoria.registrar(db, autor_id=autor_id, acao="perfil.permissoes", alvo=f"perfil:{perfil}",
                        detalhes=",".join(sorted(set(permissoes))))
    db.commit()
    return obter_permissoes(db, perfil)


def dashboard(db) -> dict:
    contar = lambda modelo: db.scalar(select(func.count()).select_from(modelo))  # noqa: E731
    return {
        "usuarios": contar(Usuario),
        "clientes": contar(Cliente),
        "filmes": contar(Filme),
        "salas": contar(Sala),
        "sessoes": contar(Sessao),
        "reservas": contar(Reserva),
    }


def listar_auditoria(db, limite: int = 200) -> list[dict]:
    registros = db.scalars(select(RegistroAuditoria).order_by(RegistroAuditoria.id.desc()).limit(limite))
    return [
        {"id": r.id, "autor_id": r.autor_id, "acao": r.acao, "alvo": r.alvo,
         "detalhes": r.detalhes, "ocorrido_em": r.ocorrido_em.isoformat(timespec="seconds")}
        for r in registros
    ]


def serializar_usuario(usuario: Usuario) -> dict:
    return {
        "id": usuario.id,
        "email": usuario.email,
        "perfil": usuario.perfil,
        "ativo": usuario.ativo,
        "cliente_id": usuario.cliente.id if usuario.cliente else None,
    }


def _obter_usuario(db, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise nao_encontrado("Usuário")
    return usuario
