# CineSenac — Sistema de Gestão de Sessões de Cinema

Sistema para gestão de sessões de cinema com três perfis de acesso: **Admin do Sistema**, **Gestor** e **Cliente**.

## Visão Geral

O CineSenac permite o cadastro e a administração de filmes, salas e sessões de cinema, além do gerenciamento do cadastro de clientes.

## Personas

| Persona | Descrição | Documento |
|---|---|---|
| Admin do Sistema | Acesso completo a todos os fluxos do sistema | [prd/personas/admin-sistema.md](prd/personas/admin-sistema.md) |
| Gestor | Cadastra salas, filmes e sessões | [prd/personas/gestor.md](prd/personas/gestor.md) |
| Cliente | Realiza o próprio cadastro (endereço, idade, e-mail) e reserva assentos em sessões | [prd/personas/cliente.md](prd/personas/cliente.md) |

## Modelagem de Dados

O modelo relacional está em [prd/dbdiagram.dbml](prd/dbdiagram.dbml), no formato DBML. Para visualizar o diagrama, importe o arquivo em [dbdiagram.io](https://dbdiagram.io/d).

**Entidades:** clientes (com endereço), filmes, salas, assentos, sessoes, reservas

## Requisitos Funcionais

Os requisitos funcionais estão documentados em [prd/requisitos-funcionais.md](prd/requisitos-funcionais.md), com matriz de rastreabilidade para as regras de negócio (RN01–RN04).

## Estrutura do Projeto

```
cinesenac/
├── README.md
├── tutorial.md
└── prd/
    ├── dbdiagram.dbml
    ├── requisitos-funcionais.md
    └── personas/
        ├── admin-sistema.md
        ├── gestor.md
        └── cliente.md
```

## Roadmap

- [x] Definição de personas e objetivos
- [x] Requisitos funcionais
- [x] Modelagem de dados
- [ ] Fluxos de navegação
- [ ] Desenvolvimento
