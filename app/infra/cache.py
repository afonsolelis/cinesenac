"""Cache de leitura com TTL, atrás de interface (ADR-0007, RNF14)."""

import threading
import time
from collections.abc import Callable


class CacheTTL:
    def __init__(self, ttl_segundos: float, relogio: Callable[[], float] = time.monotonic):
        self.ttl_segundos = ttl_segundos
        self._relogio = relogio
        self._dados: dict[str, tuple[float, object]] = {}
        self._trava = threading.Lock()

    def obter(self, chave: str):
        with self._trava:
            entrada = self._dados.get(chave)
            if entrada is None:
                return None
            expira_em, valor = entrada
            if self._relogio() >= expira_em:
                del self._dados[chave]
                return None
            return valor

    def definir(self, chave: str, valor) -> None:
        with self._trava:
            self._dados[chave] = (self._relogio() + self.ttl_segundos, valor)

    def limpar(self) -> None:
        with self._trava:
            self._dados.clear()
