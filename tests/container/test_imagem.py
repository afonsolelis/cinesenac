"""Verifica a imagem de contêiner real com testcontainers (ADR-0019, RNF39, RNF40).

Requer Docker. Sem Docker, os testes são pulados. Na CI, a imagem é construída antes
e recebida pela variável CINESENAC_IMAGE.
"""

import os
import time

import httpx
import pytest
from testcontainers.core.container import DockerContainer

IMAGEM = os.environ.get("CINESENAC_IMAGE", "cinesenac:dev")
SEGREDO = "chave-do-teste-de-contenedor-com-tamanho-suficiente-0123456789"
PORTA = 8000

pytestmark = pytest.mark.container


def _docker_disponivel() -> bool:
    try:
        import docker

        docker.from_env().ping()
        return True
    except Exception:
        return False


def _aguardar(url: str, limite_segundos: float = 60) -> None:
    fim = time.monotonic() + limite_segundos
    while time.monotonic() < fim:
        try:
            if httpx.get(f"{url}/healthz", timeout=2).status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(1)
    raise TimeoutError("o contêiner não respondeu ao healthcheck")


@pytest.fixture(scope="module")
def conteiner():
    if not _docker_disponivel():
        pytest.skip("Docker indisponível")
    contenedor = (
        DockerContainer(IMAGEM)
        .with_exposed_ports(PORTA)
        .with_env("CINESENAC_SECRET_KEY", SEGREDO)
    )
    with contenedor:
        url = f"http://{contenedor.get_container_host_ip()}:{contenedor.get_exposed_port(PORTA)}"
        _aguardar(url)
        yield contenedor, url


def test_contenedor_responde_ao_healthcheck(conteiner):
    _, url = conteiner
    resposta = httpx.get(f"{url}/healthz", timeout=5)
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_vitrine_renderiza_com_cabecalhos_de_seguranca(conteiner):
    _, url = conteiner
    resposta = httpx.get(f"{url}/programacao", timeout=5)
    assert resposta.status_code == 200
    assert 'lang="pt-BR"' in resposta.text
    assert "default-src 'self'" in resposta.headers["Content-Security-Policy"]
    assert resposta.headers["X-Frame-Options"] == "DENY"


def test_arquivos_estaticos_sao_servidos_de_dentro_do_pacote(conteiner):
    _, url = conteiner
    assert httpx.get(f"{url}/static/app.css", timeout=5).status_code == 200


def test_api_v1_esta_exposta_no_contrato(conteiner):
    _, url = conteiner
    caminhos = httpx.get(f"{url}/openapi.json", timeout=5).json()["paths"]
    assert "/v1/reservas" in caminhos


def test_processo_nao_roda_como_root(conteiner):
    contenedor, _ = conteiner
    codigo, saida = contenedor.get_wrapped_container().exec_run("id -u")
    assert codigo == 0
    assert saida.decode().strip() != "0"
