"""Comandos de operação. Cria o primeiro administrador, já que a API exige um admin autenticado."""

import argparse
import getpass
import sys

from app.config import Settings
from app.erros import ErroDominio
from app.main import create_app
from app.servicos.usuarios import criar_usuario


def criar_admin_inicial(sessionmaker, email: str, senha: str):
    with sessionmaker() as db:
        return criar_usuario(db, email=email, senha=senha, perfil="admin")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="cinesenac")
    sub = parser.add_subparsers(dest="comando", required=True)
    admin = sub.add_parser("criar-admin", help="cria o primeiro administrador")
    admin.add_argument("--email", required=True)
    args = parser.parse_args(argv)

    senha = getpass.getpass("Senha do administrador: ")
    application = create_app(Settings.from_env())
    try:
        criar_admin_inicial(application.state.sessionmaker, args.email, senha)
    except ErroDominio as erro:
        print(f"Erro: {erro.mensagem}", file=sys.stderr)
        return 1
    print(f"Administrador criado: {args.email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
