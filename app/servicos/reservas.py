"""Reservas de assentos (RF20 a RF26, RF30). RN01 a RN03, RNF01, RNF02, RNF24, RNF25.

Ordem das validações dentro da transação, que começa com BEGIN IMMEDIATE (ADR-0004):
1. Pedido já processado com a mesma chave (idempotência, ADR-0006).
2. Sessão existente e não cancelada.
3. Assentos existentes na sala.
4. Conflito de horário com outras reservas do cliente (RN03, RF24).
5. Assentos livres (RN01, RF23).
6. Gravação de todos os assentos, ou de nenhum (RN02, RNF25).
"""

import json
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.dominio.regras import intervalos_se_sobrepoem
from app.erros import ErroDominio, nao_encontrado, validacao
from app.models import Assento, RegistroIdempotencia, Reserva, Sessao
from app.servicos.programacao import obter_sessao, serializar_sessao


def mapa(db, sessao_id: int) -> dict:
    sessao = obter_sessao(db, sessao_id)
    ocupados = set(db.scalars(select(Reserva.assento_id).where(Reserva.sessao_id == sessao_id)))
    return {
        "sessao": serializar_sessao(sessao),
        "assentos": [
            {"codigo": a.codigo, "ocupado": a.id in ocupados}
            for a in sessao.sala.assentos
        ],
    }


def reservar_assentos(db, *, cliente_id: int, sessao_id: int, codigos: list[str], chave: str, corpo_hash: str) -> dict:
    anterior = db.scalar(
        select(RegistroIdempotencia).where(
            RegistroIdempotencia.cliente_id == cliente_id,
            RegistroIdempotencia.chave == chave,
        )
    )
    if anterior is not None:
        if anterior.hash_corpo != corpo_hash:
            raise ErroDominio(422, "idempotencia_conflito",
                              "Esta chave já foi usada com outro pedido.")
        return json.loads(anterior.corpo_json)

    sessao = obter_sessao(db, sessao_id)
    if sessao.cancelada:
        raise ErroDominio(409, "sessao_cancelada", "Esta sessão foi cancelada.")
    if len(set(codigos)) != len(codigos):
        raise validacao("Há assentos repetidos no pedido.", ["assentos"])

    assentos = {a.codigo: a for a in sessao.sala.assentos}
    inexistentes = [c for c in codigos if c not in assentos]
    if inexistentes:
        raise ErroDominio(422, "assento_inexistente",
                          f"Assento inexistente nesta sala: {', '.join(inexistentes)}.", ["assentos"])

    _verificar_conflito_do_cliente(db, cliente_id, sessao)

    ocupados = set(db.scalars(
        select(Reserva.assento_id).where(
            Reserva.sessao_id == sessao_id,
            Reserva.assento_id.in_([assentos[c].id for c in codigos]),
        )
    ))
    if ocupados:
        raise ErroDominio(409, "assento_indisponivel", "Um ou mais assentos já foram reservados.", ["assentos"])

    reservas = [Reserva(cliente_id=cliente_id, sessao_id=sessao_id, assento_id=assentos[c].id) for c in codigos]
    db.add_all(reservas)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ErroDominio(409, "assento_indisponivel", "Um ou mais assentos já foram reservados.", ["assentos"])

    corpo = _corpo_da_reserva(sessao, reservas, codigos)
    db.add(RegistroIdempotencia(
        cliente_id=cliente_id, chave=chave, hash_corpo=corpo_hash, corpo_json=json.dumps(corpo),
    ))
    db.commit()
    return corpo


def minhas_reservas(db, cliente_id: int | None) -> list[dict]:
    if cliente_id is None:
        return []
    consulta = (
        select(Reserva)
        .join(Sessao, Sessao.id == Reserva.sessao_id)
        .where(Reserva.cliente_id == cliente_id)
        .order_by(Sessao.data_hora_inicio, Reserva.id)
    )
    return [_item_reserva(r) for r in db.scalars(consulta)]


def cancelar_reserva(db, reserva_id: int, autor_id: int) -> None:
    from app.servicos import auditoria

    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise nao_encontrado("Reserva")
    auditoria.registrar(
        db,
        autor_id=autor_id,
        acao="reserva.cancelar",
        alvo=f"reserva:{reserva.id}",
        detalhes=f"cliente:{reserva.cliente_id};sessao:{reserva.sessao_id};assento:{reserva.assento_id}",
    )
    db.delete(reserva)
    db.commit()


def listar_reservas_do_cliente(db, cliente_id: int) -> list[dict]:
    return minhas_reservas(db, cliente_id)


def _verificar_conflito_do_cliente(db, cliente_id: int, sessao: Sessao) -> None:
    consulta = (
        select(Sessao)
        .join(Reserva, Reserva.sessao_id == Sessao.id)
        .where(Reserva.cliente_id == cliente_id, Sessao.cancelada.is_(False), Sessao.id != sessao.id)
    )
    for outra in db.scalars(consulta.distinct()):
        if intervalos_se_sobrepoem(sessao.data_hora_inicio, sessao.duracao_minutos,
                                   outra.data_hora_inicio, outra.duracao_minutos):
            raise ErroDominio(409, "conflito_horario_cliente",
                              "Você já tem uma reserva em sessão que se sobrepõe a esta.")


def _corpo_da_reserva(sessao: Sessao, reservas: list[Reserva], codigos: list[str]) -> dict:
    total = Decimal(sessao.valor_ingresso) * len(codigos)
    return {
        "sessao_id": sessao.id,
        "data_hora_inicio": sessao.data_hora_inicio.isoformat(timespec="seconds"),
        "filme": {"id": sessao.filme.id, "titulo": sessao.filme.titulo},
        "sala": {"id": sessao.sala.id, "nome": sessao.sala.nome},
        "reservas": [{"id": r.id, "assento": c} for r, c in zip(reservas, codigos)],
        "valor_total": f"{total:.2f}",
    }


def _item_reserva(reserva: Reserva) -> dict:
    sessao = reserva.sessao
    return {
        "id": reserva.id,
        "sessao_id": sessao.id,
        "filme": {"id": sessao.filme.id, "titulo": sessao.filme.titulo},
        "data_hora_inicio": sessao.data_hora_inicio.isoformat(timespec="seconds"),
        "assento": reserva.assento.codigo,
        "valor": f"{Decimal(sessao.valor_ingresso):.2f}",
    }
