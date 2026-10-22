"""Catálogo de filmes e salas (RF08 a RF13, RNF31)."""

from sqlalchemy import func, or_, select

from app.dominio.regras import gerar_codigos_assentos
from app.erros import ErroDominio, nao_encontrado, validacao
from app.models import Assento, Filme, Reserva, Sala, Sessao
from app.servicos import auditoria

CAMPOS_FILME = ("titulo", "duracao_minutos", "genero", "sinopse", "cartaz_url",
                "faixa_etaria", "elenco", "nacionalidade")
CAMPOS_SALA = ("nome", "qtd_assentos", "hora_abertura", "hora_fechamento", "especificacao_tecnica")


# ---------- filmes ----------

def criar_filme(db, dados: dict, autor_id: int) -> Filme:
    filme = Filme(**{campo: dados[campo] for campo in CAMPOS_FILME})
    db.add(filme)
    db.flush()
    auditoria.registrar(db, autor_id=autor_id, acao="filme.criar", alvo=f"filme:{filme.id}")
    db.commit()
    return filme


def atualizar_filme(db, filme_id: int, dados: dict, autor_id: int) -> Filme:
    filme = obter_filme(db, filme_id)
    for campo, valor in dados.items():
        setattr(filme, campo, valor)
    db.commit()
    return filme


def excluir_filme(db, filme_id: int, autor_id: int) -> None:
    filme = obter_filme(db, filme_id)
    if db.scalar(select(func.count(Sessao.id)).where(Sessao.filme_id == filme_id)):
        raise ErroDominio(409, "filme_com_sessoes", "O filme possui sessões vinculadas e não pode ser excluído.")
    db.delete(filme)
    db.commit()


def obter_filme(db, filme_id: int) -> Filme:
    filme = db.get(Filme, filme_id)
    if filme is None:
        raise nao_encontrado("Filme")
    return filme


def listar_filmes(db, q: str | None = None) -> list[Filme]:
    consulta = select(Filme).order_by(Filme.titulo)
    if q:
        padrao = f"%{q}%"
        consulta = consulta.where(or_(Filme.titulo.ilike(padrao), Filme.genero.ilike(padrao)))
    return list(db.scalars(consulta))


def serializar_filme(filme: Filme) -> dict:
    return {campo: getattr(filme, campo) for campo in ("id",) + CAMPOS_FILME}


# ---------- salas ----------

def criar_sala(db, dados: dict, autor_id: int) -> Sala:
    _validar_horario(dados["hora_abertura"], dados["hora_fechamento"])
    sala = Sala(**{campo: dados[campo] for campo in CAMPOS_SALA})
    sala.assentos = [Assento(codigo=codigo) for codigo in gerar_codigos_assentos(dados["qtd_assentos"])]
    db.add(sala)
    db.flush()
    auditoria.registrar(db, autor_id=autor_id, acao="sala.criar", alvo=f"sala:{sala.id}")
    db.commit()
    return sala


def atualizar_sala(db, sala_id: int, dados: dict, autor_id: int) -> Sala:
    sala = obter_sala(db, sala_id)
    abertura = dados.get("hora_abertura", sala.hora_abertura)
    fechamento = dados.get("hora_fechamento", sala.hora_fechamento)
    _validar_horario(abertura, fechamento)
    for campo in CAMPOS_SALA:
        if campo in dados and campo != "qtd_assentos":
            setattr(sala, campo, dados[campo])
    if "qtd_assentos" in dados and dados["qtd_assentos"] != sala.qtd_assentos:
        _redimensionar_assentos(db, sala, dados["qtd_assentos"])
        sala.qtd_assentos = dados["qtd_assentos"]
    db.commit()
    return sala


def _redimensionar_assentos(db, sala: Sala, nova_quantidade: int) -> None:
    atual = len(sala.assentos)
    if nova_quantidade > atual:
        for i in range(atual + 1, nova_quantidade + 1):
            sala.assentos.append(Assento(codigo=f"A{i}"))
        return
    removidos = [a for a in sala.assentos if int(a.codigo[1:]) > nova_quantidade]
    ids = [a.id for a in removidos]
    if ids and db.scalar(select(func.count(Reserva.id)).where(Reserva.assento_id.in_(ids))):
        raise ErroDominio(409, "assentos_reservados", "Há reservas nos assentos que seriam removidos.")
    for assento in removidos:
        sala.assentos.remove(assento)


def excluir_sala(db, sala_id: int, autor_id: int) -> None:
    sala = obter_sala(db, sala_id)
    if db.scalar(select(func.count(Sessao.id)).where(Sessao.sala_id == sala_id)):
        raise ErroDominio(409, "sala_com_sessoes", "A sala possui sessões vinculadas e não pode ser excluída.")
    db.delete(sala)
    db.commit()


def obter_sala(db, sala_id: int) -> Sala:
    sala = db.get(Sala, sala_id)
    if sala is None:
        raise nao_encontrado("Sala")
    return sala


def listar_salas(db, q: str | None = None) -> list[Sala]:
    consulta = select(Sala).order_by(Sala.nome)
    if q:
        consulta = consulta.where(Sala.nome.ilike(f"%{q}%"))
    return list(db.scalars(consulta))


def serializar_sala(sala: Sala, com_assentos: bool = False) -> dict:
    dados = {"id": sala.id, **{campo: getattr(sala, campo) for campo in CAMPOS_SALA}}
    if com_assentos:
        dados["assentos"] = [{"codigo": a.codigo} for a in sala.assentos]
    return dados


def _validar_horario(abertura: str, fechamento: str) -> None:
    if fechamento <= abertura:
        raise validacao("O horário de fechamento deve ser posterior à abertura.", ["hora_fechamento"])
