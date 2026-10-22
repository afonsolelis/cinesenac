"""Modelo relacional. Segue prd/dbdiagram.dbml e acrescenta as entidades pendentes (ver classes.md)."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _agora():
    return datetime.now().replace(microsecond=0)


class Usuario(Base):
    """Conta de acesso. Pendente no DBML (RF01, RF27)."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[str] = mapped_column(String(20), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Incrementado na desativação: sessões antigas deixam de valer (RNF28).
    sessao_versao: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=_agora)

    cliente: Mapped["Cliente | None"] = relationship(back_populates="usuario", uselist=False)


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    idade: Mapped[int] = mapped_column(Integer, nullable=False)
    logradouro: Mapped[str] = mapped_column(String(200), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    complemento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bairro: Mapped[str] = mapped_column(String(100), nullable=False)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False)
    estado: Mapped[str] = mapped_column(String(2), nullable=False)
    cep: Mapped[str] = mapped_column(String(9), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=_agora)

    usuario: Mapped[Usuario] = relationship(back_populates="cliente")


class Filme(Base):
    __tablename__ = "filmes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    duracao_minutos: Mapped[int] = mapped_column(Integer, nullable=False)
    genero: Mapped[str] = mapped_column(String(60), nullable=False)
    sinopse: Mapped[str] = mapped_column(Text, nullable=False)
    cartaz_url: Mapped[str] = mapped_column(String(500), nullable=False)
    faixa_etaria: Mapped[str] = mapped_column(String(20), nullable=False)
    elenco: Mapped[str] = mapped_column(Text, nullable=False)
    nacionalidade: Mapped[str] = mapped_column(String(20), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=_agora)


class Sala(Base):
    __tablename__ = "salas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    qtd_assentos: Mapped[int] = mapped_column(Integer, nullable=False)
    hora_abertura: Mapped[str] = mapped_column(String(5), nullable=False)
    hora_fechamento: Mapped[str] = mapped_column(String(5), nullable=False)
    especificacao_tecnica: Mapped[str] = mapped_column(String(100), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=_agora)

    assentos: Mapped[list["Assento"]] = relationship(
        back_populates="sala", cascade="all, delete-orphan", order_by="Assento.id"
    )


class Assento(Base):
    __tablename__ = "assentos"
    __table_args__ = (UniqueConstraint("sala_id", "codigo", name="uq_assento_sala_codigo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sala_id: Mapped[int] = mapped_column(ForeignKey("salas.id"), nullable=False)
    codigo: Mapped[str] = mapped_column(String(10), nullable=False)

    sala: Mapped[Sala] = relationship(back_populates="assentos")


class Sessao(Base):
    __tablename__ = "sessoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filme_id: Mapped[int] = mapped_column(ForeignKey("filmes.id"), nullable=False)
    sala_id: Mapped[int] = mapped_column(ForeignKey("salas.id"), nullable=False)
    data_hora_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duracao_minutos: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_ingresso: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cancelada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=_agora)

    filme: Mapped[Filme] = relationship()
    sala: Mapped[Sala] = relationship()


class Reserva(Base):
    __tablename__ = "reservas"
    __table_args__ = (UniqueConstraint("sessao_id", "assento_id", name="uq_reserva_sessao_assento"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    sessao_id: Mapped[int] = mapped_column(ForeignKey("sessoes.id"), nullable=False)
    assento_id: Mapped[int] = mapped_column(ForeignKey("assentos.id"), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=_agora)

    sessao: Mapped[Sessao] = relationship()
    assento: Mapped[Assento] = relationship()
    cliente: Mapped[Cliente] = relationship()


class DiaProgramacao(Base):
    """Dia publicado da programação (RF19). Só dias publicados aparecem ao público."""

    __tablename__ = "dias_programacao"

    data: Mapped[date] = mapped_column(Date, primary_key=True)
    publicado_em: Mapped[datetime] = mapped_column(DateTime, default=_agora)


class PerfilPermissao(Base):
    """Permissões concedidas a cada perfil (RF28). Editável pelo Admin."""

    __tablename__ = "perfil_permissoes"

    perfil: Mapped[str] = mapped_column(String(20), primary_key=True)
    permissao: Mapped[str] = mapped_column(String(60), primary_key=True)


class RegistroAuditoria(Base):
    """Trilha de ações administrativas e cancelamentos (RNF33). Pendente no DBML."""

    __tablename__ = "registros_auditoria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    autor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    acao: Mapped[str] = mapped_column(String(60), nullable=False)
    alvo: Mapped[str] = mapped_column(String(120), nullable=False)
    detalhes: Mapped[str] = mapped_column(Text, default="")
    ocorrido_em: Mapped[datetime] = mapped_column(DateTime, default=_agora)


class RegistroIdempotencia(Base):
    """Resultado de um pedido de reserva, por chave (ADR-0006, RNF24)."""

    __tablename__ = "registros_idempotencia"
    __table_args__ = (UniqueConstraint("cliente_id", "chave", name="uq_idempotencia_cliente_chave"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cliente_id: Mapped[int] = mapped_column(Integer, nullable=False)
    chave: Mapped[str] = mapped_column(String(120), nullable=False)
    hash_corpo: Mapped[str] = mapped_column(String(64), nullable=False)
    corpo_json: Mapped[str] = mapped_column(Text, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=_agora)
