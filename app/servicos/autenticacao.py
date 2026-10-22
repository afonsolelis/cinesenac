"""Entrada com limite de tentativas (RF01, RNF30). Usada pela API e pelas páginas."""

from app.erros import ErroDominio
from app.servicos.usuarios import autenticar

MENSAGEM_CREDENCIAIS = "E-mail ou senha inválidos."
MENSAGEM_LIMITE = "Muitas tentativas. Aguarde alguns minutos e tente novamente."


def entrar(db, limitador, *, email: str, senha: str, ip: str):
    chaves = [f"email:{email.lower()}", f"ip:{ip}"]
    if any(limitador.bloqueado(chave) for chave in chaves):
        raise ErroDominio(429, "muitas_tentativas", MENSAGEM_LIMITE)
    usuario = autenticar(db, email=email, senha=senha)
    if usuario is None:
        for chave in chaves:
            limitador.registrar_falha(chave)
        raise ErroDominio(401, "credenciais_invalidas", MENSAGEM_CREDENCIAIS)
    limitador.registrar_sucesso(chaves[0])
    return usuario
