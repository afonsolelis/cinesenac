"""Trilha de auditoria (RNF33, ADR-0015). Gravada na mesma transação da ação."""

from app.models import RegistroAuditoria


def registrar(db, *, autor_id, acao: str, alvo: str, detalhes: str = "") -> None:
    """Adiciona o registro à sessão atual. Quem chama é responsável pelo commit."""
    db.add(RegistroAuditoria(autor_id=autor_id, acao=acao, alvo=alvo, detalhes=detalhes))
