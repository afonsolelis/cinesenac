"""Programação: sessões, sobreposição, cota nacional e publicação (RF03, RF14 a RF19, RN04)."""

import json
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func, select

from app.dominio.regras import cota_nacional_atendida, intervalos_se_sobrepoem
from app.erros import ErroDominio, nao_encontrado
from app.models import DiaProgramacao, Filme, Reserva, Sala, Sessao
from app.servicos import auditoria

PREFIXO_CACHE = "programacao:"


def criar_sessao(db, *, filme_id, sala_id, data_hora_inicio, duracao_minutos, valor_ingresso):
    filme = db.get(Filme, filme_id)
    if filme is None:
        raise nao_encontrado("Filme")
    sala = db.get(Sala, sala_id)
    if sala is None:
        raise nao_encontrado("Sala")
    _verificar_sobreposicao(db, sala_id, data_hora_inicio, duracao_minutos)
    sessao = Sessao(
        filme_id=filme_id,
        sala_id=sala_id,
        data_hora_inicio=data_hora_inicio,
        duracao_minutos=duracao_minutos,
        valor_ingresso=Decimal(valor_ingresso),
    )
    db.add(sessao)
    db.flush()
    avisos = []
    if not cota_nacional_atendida(_nacionalidades_do_dia(db, data_hora_inicio.date())):
        avisos.append("cota_nacional_pendente")
    db.commit()
    return sessao, avisos


def atualizar_sessao(db, sessao_id: int, alteracoes: dict) -> Sessao:
    sessao = obter_sessao(db, sessao_id)
    if sessao.cancelada:
        raise ErroDominio(409, "sessao_cancelada", "Sessão cancelada não pode ser alterada.")
    inicio = alteracoes.get("data_hora_inicio", sessao.data_hora_inicio)
    duracao = alteracoes.get("duracao_minutos", sessao.duracao_minutos)
    _verificar_sobreposicao(db, sessao.sala_id, inicio, duracao, excluir_id=sessao.id)
    for campo, valor in alteracoes.items():
        if campo == "valor_ingresso":
            valor = Decimal(valor)
        setattr(sessao, campo, valor)
    db.commit()
    return sessao


def cancelar_sessao(db, sessao_id: int, autor_id: int) -> Sessao:
    sessao = obter_sessao(db, sessao_id)
    if db.scalar(select(func.count(Reserva.id)).where(Reserva.sessao_id == sessao_id)):
        raise ErroDominio(409, "sessao_com_reservas", "A sessão possui reservas e não pode ser cancelada.")
    sessao.cancelada = True
    auditoria.registrar(db, autor_id=autor_id, acao="sessao.cancelar", alvo=f"sessao:{sessao.id}")
    db.commit()
    return sessao


def obter_sessao(db, sessao_id: int) -> Sessao:
    sessao = db.get(Sessao, sessao_id)
    if sessao is None:
        raise nao_encontrado("Sessão")
    return sessao


def cota_nacional(db, dia: date) -> dict:
    nacionalidades = _nacionalidades_do_dia(db, dia)
    return {
        "data": dia.isoformat(),
        "atendida": cota_nacional_atendida(nacionalidades),
        "sessoes_nacionais": nacionalidades.count("NACIONAL"),
    }


def publicar_dia(db, dia: date, autor_id: int) -> dict:
    if not cota_nacional_atendida(_nacionalidades_do_dia(db, dia)):
        raise ErroDominio(422, "cota_nacional_nao_atendida",
                          "A programação do dia precisa de ao menos uma sessão de filme nacional (RN04).")
    if db.get(DiaProgramacao, dia) is None:
        db.add(DiaProgramacao(data=dia))
    auditoria.registrar(db, autor_id=autor_id, acao="programacao.publicar", alvo=f"dia:{dia.isoformat()}")
    db.commit()
    return {"data": dia.isoformat(), "publicado": True}


def listar_sessoes(db, filtros: dict, somente_publicadas: bool) -> list[dict]:
    consulta = select(Sessao).where(Sessao.cancelada.is_(False)).order_by(Sessao.data_hora_inicio)
    if filtros.get("sala_id"):
        consulta = consulta.where(Sessao.sala_id == filtros["sala_id"])
    if filtros.get("filme_id"):
        consulta = consulta.where(Sessao.filme_id == filtros["filme_id"])
    if filtros.get("inicio"):
        consulta = consulta.where(Sessao.data_hora_inicio >= datetime.combine(filtros["inicio"], time.min))
    if filtros.get("fim"):
        consulta = consulta.where(Sessao.data_hora_inicio < datetime.combine(filtros["fim"] + timedelta(days=1), time.min))
    sessoes = list(db.scalars(consulta))
    if somente_publicadas:
        publicados = set(db.scalars(select(DiaProgramacao.data)))
        sessoes = [s for s in sessoes if s.data_hora_inicio.date() in publicados]
    return [serializar_sessao(s) for s in sessoes]


def programacao_publica(db, cache, filtros: dict) -> tuple[list[dict], bool]:
    """Devolve (itens, veio_do_cache). Só dias publicados (RF03). Cache de TTL (ADR-0007)."""
    chave = PREFIXO_CACHE + json.dumps(_filtros_serializaveis(filtros), sort_keys=True)
    existente = cache.obter(chave)
    if existente is not None:
        return existente, True
    itens = listar_sessoes(db, filtros, somente_publicadas=True)
    cache.definir(chave, itens)
    return itens, False


def serializar_sessao(sessao: Sessao) -> dict:
    return {
        "id": sessao.id,
        "filme_id": sessao.filme_id,
        "sala_id": sessao.sala_id,
        "data_hora_inicio": sessao.data_hora_inicio.isoformat(timespec="seconds"),
        "duracao_minutos": sessao.duracao_minutos,
        "valor_ingresso": f"{Decimal(sessao.valor_ingresso):.2f}",
        "cancelada": sessao.cancelada,
        "filme": {"id": sessao.filme.id, "titulo": sessao.filme.titulo,
                  "nacionalidade": sessao.filme.nacionalidade},
        "sala": {"id": sessao.sala.id, "nome": sessao.sala.nome},
    }


def _nacionalidades_do_dia(db, dia: date) -> list[str]:
    inicio = datetime.combine(dia, time.min)
    consulta = (
        select(Filme.nacionalidade)
        .join(Sessao, Sessao.filme_id == Filme.id)
        .where(Sessao.cancelada.is_(False))
        .where(Sessao.data_hora_inicio >= inicio)
        .where(Sessao.data_hora_inicio < inicio + timedelta(days=1))
    )
    return list(db.scalars(consulta))


def _verificar_sobreposicao(db, sala_id, inicio, duracao, excluir_id=None) -> None:
    consulta = select(Sessao).where(Sessao.sala_id == sala_id, Sessao.cancelada.is_(False))
    for existente in db.scalars(consulta):
        if excluir_id is not None and existente.id == excluir_id:
            continue
        if intervalos_se_sobrepoem(inicio, duracao, existente.data_hora_inicio, existente.duracao_minutos):
            raise ErroDominio(409, "conflito_horario_sala",
                              "Já existe sessão nesta sala em horário que se sobrepõe.")


def _filtros_serializaveis(filtros: dict) -> dict:
    return {k: (v.isoformat() if isinstance(v, date) else v) for k, v in filtros.items() if v is not None}
