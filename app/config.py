"""Configuração por variáveis de ambiente com prefixo CINESENAC_ (ADR-0019, RNF40)."""

import os
from dataclasses import dataclass

PREFIXO = "CINESENAC_"
TAMANHO_MINIMO_CHAVE = 32


def _bool(valor: str) -> bool:
    return valor.strip().lower() in {"1", "true", "sim", "yes"}


@dataclass(frozen=True)
class Settings:
    secret_key: str
    database_url: str = "sqlite:///./cinesenac.db"
    https_only: bool = False
    cache_ttl_seconds: int = 30
    login_max_tentativas: int = 5
    login_janela_segundos: int = 900
    max_requisicoes_simultaneas: int = 200

    def __post_init__(self):
        if len(self.secret_key) < TAMANHO_MINIMO_CHAVE:
            raise ValueError(
                f"CINESENAC_SECRET_KEY precisa ter pelo menos {TAMANHO_MINIMO_CHAVE} caracteres"
            )

    @classmethod
    def from_env(cls) -> "Settings":
        def ler(nome, padrao=None):
            return os.environ.get(PREFIXO + nome, padrao)

        chave = ler("SECRET_KEY")
        if not chave:
            raise ValueError("CINESENAC_SECRET_KEY é obrigatória e não pode ser versionada")
        return cls(
            secret_key=chave,
            database_url=ler("DATABASE_URL", "sqlite:///./cinesenac.db"),
            https_only=_bool(ler("HTTPS_ONLY", "false")),
            cache_ttl_seconds=int(ler("CACHE_TTL_SEGUNDOS", "30")),
            login_max_tentativas=int(ler("LOGIN_MAX_TENTATIVAS", "5")),
            login_janela_segundos=int(ler("LOGIN_JANELA_SEGUNDOS", "900")),
            max_requisicoes_simultaneas=int(ler("MAX_REQUISICOES_SIMULTANEAS", "200")),
        )
