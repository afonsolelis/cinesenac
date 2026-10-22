"""Hash adaptativo de senhas (ADR-0012, RNF28)."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

_hasher = PasswordHasher()


def gerar_hash_senha(senha: str) -> str:
    return _hasher.hash(senha)


def verificar_senha(hash_: str, senha: str) -> bool:
    try:
        return _hasher.verify(hash_, senha)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
