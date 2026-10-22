"""Cadastro do cliente (RF04 a RF07, RF05 e RNF03)."""

from sqlalchemy import select

from app.erros import ErroDominio, nao_encontrado
from app.models import Cliente, Usuario
from app.servicos import auditoria
from app.servicos.usuarios import criar_usuario, validar_email

CAMPOS_ENDERECO = ("logradouro", "numero", "complemento", "bairro", "cidade", "estado", "cep")


def cadastrar_cliente(
    db, *, email, senha, nome, idade, endereco: dict, autor_id=None, commit: bool = True
) -> Cliente:
    usuario = criar_usuario(db, email=email, senha=senha, perfil="cliente", commit=False)
    cliente = Cliente(
        usuario=usuario,
        nome=nome,
        idade=idade,
        logradouro=endereco["logradouro"],
        numero=endereco["numero"],
        complemento=endereco.get("complemento"),
        bairro=endereco["bairro"],
        cidade=endereco["cidade"],
        estado=endereco["estado"],
        cep=endereco["cep"],
    )
    db.add(cliente)
    if autor_id is not None:
        auditoria.registrar(db, autor_id=autor_id, acao="usuario.criar", alvo=f"cliente:{usuario.email}")
    _confirmar(db, commit)
    return cliente


def obter_cliente(db, cliente_id: int) -> Cliente:
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise nao_encontrado("Cadastro")
    return cliente


def atualizar_cliente(db, cliente_id: int, *, email=None, idade=None, endereco=None) -> Cliente:
    cliente = obter_cliente(db, cliente_id)
    if email is not None and email != cliente.usuario.email:
        validar_email(email)
        outro = db.scalar(select(Usuario).where(Usuario.email == email))
        if outro is not None:
            raise ErroDominio(409, "email_duplicado", "Este e-mail já está cadastrado.", ["email"])
        cliente.usuario.email = email
    if idade is not None:
        cliente.idade = idade
    if endereco is not None:
        for campo in CAMPOS_ENDERECO:
            if campo in endereco:
                setattr(cliente, campo, endereco[campo])
    db.commit()
    return cliente


def serializar_cliente(cliente: Cliente) -> dict:
    return {
        "id": cliente.id,
        "usuario_id": cliente.usuario_id,
        "email": cliente.usuario.email,
        "nome": cliente.nome,
        "idade": cliente.idade,
        "endereco": {campo: getattr(cliente, campo) for campo in CAMPOS_ENDERECO},
    }


def _confirmar(db, commit: bool) -> None:
    if commit:
        db.commit()
    else:
        db.flush()
