"""Permissões do sistema e perfis padrão (RF02, RF28, ADR-0013)."""

CADASTRO_PROPRIO = "cadastro:proprio"
RESERVAS_CRIAR = "reservas:criar"
RESERVAS_GERENCIAR = "reservas:gerenciar"
CATALOGO = "catalogo:gerenciar"
PROGRAMACAO = "programacao:gerenciar"
USUARIOS = "usuarios:gerenciar"
PERMISSOES = "permissoes:gerenciar"
DASHBOARD = "dashboard:ver"
AUDITORIA = "auditoria:ver"

TODAS = [
    CADASTRO_PROPRIO, RESERVAS_CRIAR, RESERVAS_GERENCIAR, CATALOGO, PROGRAMACAO,
    USUARIOS, PERMISSOES, DASHBOARD, AUDITORIA,
]

PERFIS = ("admin", "gestor", "cliente")

PADRAO = {
    "admin": list(TODAS),
    "gestor": [CATALOGO, PROGRAMACAO],
    "cliente": [CADASTRO_PROPRIO, RESERVAS_CRIAR],
}

# Permissões que o perfil admin não pode perder, para não se trancar para fora.
OBRIGATORIAS_ADMIN = [PERMISSOES]
