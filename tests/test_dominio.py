"""Regras de domínio puras, sem HTTP nem banco (ADR-0001, RNF34)."""

from datetime import datetime, timedelta

import pytest

from app.dominio.regras import (
    cota_nacional_atendida,
    gerar_codigos_assentos,
    intervalos_se_sobrepoem,
    rotulo_acessivel,
)


INICIO = datetime(2026, 11, 2, 19, 0)


class TestRF15Sobreposicao:
    def test_sessoes_adjacentes_nao_conflitam(self):
        # Intervalo [19h, 21h) e [21h, 22h) não se cruzam.
        assert intervalos_se_sobrepoem(INICIO, 120, INICIO + timedelta(hours=2), 60) is False

    def test_sessoes_que_se_cruzam_conflitam(self):
        assert intervalos_se_sobrepoem(INICIO, 120, INICIO + timedelta(hours=1), 60) is True

    def test_sessao_contida_em_outra_conflita(self):
        assert intervalos_se_sobrepoem(INICIO, 180, INICIO + timedelta(minutes=30), 30) is True

    def test_mesmo_horario_conflita(self):
        assert intervalos_se_sobrepoem(INICIO, 120, INICIO, 120) is True

    def test_sessao_anterior_adjacente_nao_conflita(self):
        assert intervalos_se_sobrepoem(INICIO, 120, INICIO - timedelta(hours=1), 60) is False


class TestRF11Assentos:
    def test_gera_codigos_de_A1_ate_An(self):
        assert gerar_codigos_assentos(3) == ["A1", "A2", "A3"]

    def test_quantidade_zero_nao_gera_assentos(self):
        with pytest.raises(ValueError):
            gerar_codigos_assentos(0)


class TestRN04CotaNacional:
    def test_cota_atendida_com_ao_menos_um_nacional(self):
        assert cota_nacional_atendida(["INTERNACIONAL", "NACIONAL"]) is True

    def test_cota_pendente_sem_nacional(self):
        assert cota_nacional_atendida(["INTERNACIONAL"]) is False

    def test_cota_pendente_sem_sessoes(self):
        assert cota_nacional_atendida([]) is False


class TestRNF19RotuloAcessivel:
    def test_rotulo_de_assento_livre(self):
        assert rotulo_acessivel("B7", "livre") == "Fila B, assento 7, livre"

    def test_rotulo_de_assento_ocupado(self):
        assert rotulo_acessivel("A1", "ocupado") == "Fila A, assento 1, ocupado"
