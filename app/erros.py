"""Erro de domínio com status HTTP e código estável (contrato em ADR-0002)."""


class ErroDominio(Exception):
    def __init__(self, status: int, codigo: str, mensagem: str, campos: list[str] | None = None):
        super().__init__(mensagem)
        self.status = status
        self.codigo = codigo
        self.mensagem = mensagem
        self.campos = campos or []


def nao_autenticado():
    return ErroDominio(401, "nao_autenticado", "Faça login para continuar.")


def sem_permissao():
    return ErroDominio(403, "sem_permissao", "Acesso negado: seu perfil não tem permissão para esta ação.")


def nao_encontrado(recurso: str):
    return ErroDominio(404, "nao_encontrado", f"{recurso} não encontrado.")


def validacao(mensagem: str, campos: list[str]):
    return ErroDominio(422, "validacao", mensagem, campos)
