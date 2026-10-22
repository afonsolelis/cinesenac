"""Engine e sessões. No SQLite, cada transação começa com BEGIN IMMEDIATE (ADR-0004, ADR-0021).

Isso serializa os escritores do banco. É mais grosseiro que o bloqueio por recurso
da ADR-0004, mas garante a correção das regras de concorrência nesta implementação.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


def criar_engine(url: str):
    eh_sqlite = url.startswith("sqlite")
    argumentos = {"check_same_thread": False, "timeout": 30} if eh_sqlite else {}
    engine = create_engine(url, connect_args=argumentos, future=True)
    if eh_sqlite:
        @event.listens_for(engine, "connect")
        def _ajustar_conexao(conexao, _registro):
            conexao.isolation_level = None  # SQLAlchemy controla o BEGIN
            cursor = conexao.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        @event.listens_for(engine, "begin")
        def _iniciar_transacao(conexao):
            conexao.exec_driver_sql("BEGIN IMMEDIATE")
    return engine


def criar_fabrica_sessoes(engine):
    return sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
