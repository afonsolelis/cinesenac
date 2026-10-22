"""Regras de negócio puras (RF11, RF15, RF18, RN03, RN04). Sem HTTP nem banco (ADR-0001)."""

from datetime import datetime, timedelta


def intervalos_se_sobrepoem(inicio_a: datetime, duracao_a: int, inicio_b: datetime, duracao_b: int) -> bool:
    """Intervalos são [início, início + duração). Sessões adjacentes não se sobrepõem (RF15)."""
    fim_a = inicio_a + timedelta(minutes=duracao_a)
    fim_b = inicio_b + timedelta(minutes=duracao_b)
    return inicio_a < fim_b and inicio_b < fim_a


def gerar_codigos_assentos(quantidade: int) -> list[str]:
    """Gera A1 até An, conforme o fluxo de cadastro de sala (RF11)."""
    if quantidade < 1:
        raise ValueError("a sala precisa de pelo menos um assento")
    return [f"A{i}" for i in range(1, quantidade + 1)]


def cota_nacional_atendida(nacionalidades: list[str]) -> bool:
    """RN04: o dia precisa de ao menos uma sessão de filme nacional."""
    return "NACIONAL" in nacionalidades


def rotulo_acessivel(codigo: str, estado: str) -> str:
    """Rótulo lido por leitor de tela para cada assento (RNF19)."""
    fila, numero = codigo[0], codigo[1:]
    return f"Fila {fila}, assento {numero}, {estado}"
