"""Contador de tentativas de login por chave (e-mail ou IP), em memória (ADR-0010, RNF30)."""

import threading
import time
from collections import deque
from collections.abc import Callable


class LimitadorTentativas:
    def __init__(self, max_tentativas: int, janela_segundos: float, relogio: Callable[[], float] = time.monotonic):
        self.max_tentativas = max_tentativas
        self.janela_segundos = janela_segundos
        self._relogio = relogio
        self._falhas: dict[str, deque] = {}
        self._trava = threading.Lock()

    def _recentes(self, chave: str) -> deque:
        agora = self._relogio()
        falhas = self._falhas.setdefault(chave, deque())
        while falhas and agora - falhas[0] >= self.janela_segundos:
            falhas.popleft()
        return falhas

    def bloqueado(self, chave: str) -> bool:
        with self._trava:
            return len(self._recentes(chave)) >= self.max_tentativas

    def registrar_falha(self, chave: str) -> None:
        with self._trava:
            self._recentes(chave).append(self._relogio())

    def registrar_sucesso(self, chave: str) -> None:
        with self._trava:
            self._falhas.pop(chave, None)
