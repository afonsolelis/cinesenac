"""Fábrica da aplicação. Monta banco, middlewares, rotas e tratadores de erro (ADR-0019, ADR-0020)."""

import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1 import router as api_router
from app.config import Settings
from app.db import criar_engine, criar_fabrica_sessoes
from app.erros import ErroDominio
from app.infra.admissao import ControleAdmissao
from app.infra.cache import CacheTTL
from app.infra.limitacao import LimitadorTentativas
from app.models import Base
from app.servicos.admin import garantir_permissoes_padrao
from app.web.routes import router as web_router

DIRETORIO = Path(__file__).parent
CSP = (
    "default-src 'self'; img-src 'self' https: data:; style-src 'self'; script-src 'self'; "
    "frame-ancestors 'none'; form-action 'self'; base-uri 'self'"
)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    engine = criar_engine(settings.database_url)
    Base.metadata.create_all(engine)  # ver ADR-0021: migrações versionadas entram antes da produção
    fabrica = criar_fabrica_sessoes(engine)
    with fabrica() as db:
        garantir_permissoes_padrao(db)

    app = FastAPI(title="CineSenac", version="1.0.0", docs_url="/docs", openapi_url="/openapi.json")
    app.state.settings = settings
    app.state.engine = engine
    app.state.sessionmaker = fabrica
    app.state.cache = CacheTTL(ttl_segundos=settings.cache_ttl_seconds)
    app.state.limitador = LimitadorTentativas(
        max_tentativas=settings.login_max_tentativas, janela_segundos=settings.login_janela_segundos,
    )
    app.state.admissao = ControleAdmissao(max_simultaneas=settings.max_requisicoes_simultaneas)

    @app.middleware("http")
    async def admissao(request: Request, call_next):
        if request.url.path == "/healthz":
            return await call_next(request)
        controle = request.app.state.admissao
        if not controle.tentar_entrar():
            return JSONResponse(
                status_code=503,
                content={"codigo": "servico_indisponivel", "mensagem": "Estamos com muitos acessos. Tente em instantes."},
                headers={"Retry-After": "1"},
            )
        try:
            return await call_next(request)
        finally:
            controle.sair()

    @app.middleware("http")
    async def cabecalhos(request: Request, call_next):
        identificador = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        resposta = await call_next(request)
        resposta.headers["X-Request-ID"] = identificador
        resposta.headers["Content-Security-Policy"] = CSP
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        resposta.headers["X-Frame-Options"] = "DENY"
        resposta.headers["Referrer-Policy"] = "same-origin"
        return resposta

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="cinesenac_sessao",
        same_site="lax",
        https_only=settings.https_only,
    )

    app.include_router(api_router)
    app.include_router(web_router, include_in_schema=False)  # o contrato OpenAPI é só a API v1
    app.mount("/static", StaticFiles(directory=DIRETORIO / "web" / "static"), name="static")

    @app.get("/healthz", include_in_schema=False)
    def healthz():
        return {"status": "ok"}

    @app.exception_handler(ErroDominio)
    async def erro_de_dominio(request: Request, exc: ErroDominio):
        if request.url.path.startswith("/v1"):
            return JSONResponse(
                status_code=exc.status,
                content={"codigo": exc.codigo, "mensagem": exc.mensagem, "campos": exc.campos},
            )
        if exc.status == 401:
            return RedirectResponse("/entrar", status_code=303)
        from app.web.routes import renderizar_erro

        return renderizar_erro(request, exc.status, exc.codigo, exc.mensagem)

    @app.exception_handler(RequestValidationError)
    async def erro_de_validacao(request: Request, exc: RequestValidationError):
        campos = [".".join(str(parte) for parte in erro["loc"][1:]) for erro in exc.errors()]
        if request.url.path.startswith("/v1"):
            return JSONResponse(
                status_code=422,
                content={"codigo": "validacao", "mensagem": "Dados inválidos.", "campos": campos},
            )
        from app.web.routes import renderizar_erro

        return renderizar_erro(request, 422, "validacao", "Dados inválidos. Revise o formulário.")

    return app


criar_app = create_app
