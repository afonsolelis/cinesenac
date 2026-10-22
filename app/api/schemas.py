"""Contratos de entrada da API v1 (ADR-0002, ADR-0014). A validação é feita na borda."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
HORA = r"^([01]\d|2[0-3]):[0-5]\d$"
FAIXA_ETARIA = Literal["LIVRE", "DEZ_ANOS", "DOZE_ANOS", "QUATORZE_ANOS", "DEZESSEIS_ANOS", "DEZOITO_ANOS"]
NACIONALIDADE = Literal["NACIONAL", "INTERNACIONAL"]


def _url_http(valor):
    if valor is None:
        return valor
    if not valor.startswith(("http://", "https://")):
        raise ValueError("A URL do cartaz precisa começar com http:// ou https://")
    return valor


class Endereco(BaseModel):
    logradouro: str = Field(min_length=1, max_length=200)
    numero: str = Field(min_length=1, max_length=20)
    complemento: str | None = Field(default=None, max_length=100)
    bairro: str = Field(min_length=1, max_length=100)
    cidade: str = Field(min_length=1, max_length=100)
    estado: str = Field(pattern=r"^[A-Z]{2}$")
    cep: str = Field(pattern=r"^\d{5}-?\d{3}$")


class EnderecoParcial(BaseModel):
    logradouro: str | None = Field(default=None, min_length=1, max_length=200)
    numero: str | None = Field(default=None, min_length=1, max_length=20)
    complemento: str | None = Field(default=None, max_length=100)
    bairro: str | None = Field(default=None, min_length=1, max_length=100)
    cidade: str | None = Field(default=None, min_length=1, max_length=100)
    estado: str | None = Field(default=None, pattern=r"^[A-Z]{2}$")
    cep: str | None = Field(default=None, pattern=r"^\d{5}-?\d{3}$")


class ClienteIn(BaseModel):
    email: str = Field(pattern=EMAIL, max_length=255)
    senha: str = Field(min_length=12, max_length=200)
    nome: str = Field(min_length=1, max_length=120)
    idade: int = Field(ge=1, le=120)
    endereco: Endereco


class ClienteUpdate(BaseModel):
    email: str | None = Field(default=None, pattern=EMAIL, max_length=255)
    idade: int | None = Field(default=None, ge=1, le=120)
    endereco: EnderecoParcial | None = None


class LoginIn(BaseModel):
    email: str = Field(min_length=1, max_length=255)
    senha: str = Field(min_length=1, max_length=200)


class FilmeIn(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    duracao_minutos: int = Field(ge=1, le=600)
    genero: str = Field(min_length=1, max_length=60)
    sinopse: str = Field(min_length=1, max_length=2000)
    cartaz_url: str = Field(min_length=1, max_length=500)
    faixa_etaria: FAIXA_ETARIA
    elenco: str = Field(min_length=1, max_length=2000)
    nacionalidade: NACIONALIDADE

    @field_validator("cartaz_url")
    @classmethod
    def _validar_cartaz(cls, valor):
        return _url_http(valor)


class FilmeUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=200)
    duracao_minutos: int | None = Field(default=None, ge=1, le=600)
    genero: str | None = Field(default=None, min_length=1, max_length=60)
    sinopse: str | None = Field(default=None, min_length=1, max_length=2000)
    cartaz_url: str | None = Field(default=None, min_length=1, max_length=500)
    faixa_etaria: FAIXA_ETARIA | None = None
    elenco: str | None = Field(default=None, min_length=1, max_length=2000)
    nacionalidade: NACIONALIDADE | None = None

    @field_validator("cartaz_url")
    @classmethod
    def _validar_cartaz(cls, valor):
        return _url_http(valor)


class SalaIn(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    qtd_assentos: int = Field(ge=1, le=500)
    hora_abertura: str = Field(pattern=HORA)
    hora_fechamento: str = Field(pattern=HORA)
    especificacao_tecnica: str = Field(min_length=1, max_length=100)


class SalaUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    qtd_assentos: int | None = Field(default=None, ge=1, le=500)
    hora_abertura: str | None = Field(default=None, pattern=HORA)
    hora_fechamento: str | None = Field(default=None, pattern=HORA)
    especificacao_tecnica: str | None = Field(default=None, min_length=1, max_length=100)


class SessaoIn(BaseModel):
    filme_id: int
    sala_id: int
    data_hora_inicio: datetime
    duracao_minutos: int = Field(ge=1, le=600)
    valor_ingresso: Decimal = Field(ge=0, max_digits=10, decimal_places=2)


class SessaoUpdate(BaseModel):
    data_hora_inicio: datetime | None = None
    duracao_minutos: int | None = Field(default=None, ge=1, le=600)
    valor_ingresso: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)


class ReservaIn(BaseModel):
    sessao_id: int
    assentos: list[str] = Field(min_length=1, max_length=50)


class ClienteCadastro(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    idade: int = Field(ge=1, le=120)
    endereco: Endereco


class UsuarioIn(BaseModel):
    email: str = Field(pattern=EMAIL, max_length=255)
    senha: str = Field(min_length=12, max_length=200)
    perfil: Literal["gestor", "cliente"]
    cliente: ClienteCadastro | None = None


class UsuarioUpdate(BaseModel):
    ativo: bool


class PermissoesIn(BaseModel):
    permissoes: list[str]
