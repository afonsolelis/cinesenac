"""Controle de admissão: limita requisições simultâneas e recusa o excedente (ADR-0010, RNF27)."""

import threading


class ControleAdmissao:
    def __init__(self, max_simultaneas: int):
        self.max_simultaneas = max_simultaneas
        self._em_andamento = 0
        self._trava = threading.Lock()

    def tentar_entrar(self) -> bool:
        with self._trava:
            if self._em_andamento >= self.max_simultaneas:
                return False
            self._em_andamento += 1
            return True

    def sair(self) -> None:
        with self._trava:
            self._em_andamento = max(0, self._em_andamento - 1)
