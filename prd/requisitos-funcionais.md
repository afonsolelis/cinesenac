# Requisitos Funcionais — CineSenac

Requisitos funcionais da aplicação, derivados das jornadas e dos objetivos das personas ([prd/personas](personas)).

**Convenções:** `RFxx` identifica o requisito. `RNxx` refere-se às regras de negócio declaradas nas personas (RN01–RN03 em [cliente](personas/cliente.md), RN04 em [gestor](personas/gestor.md)).

## 1. Autenticação e Controle de Acesso

| ID | Requisito | Persona |
|---|---|---|
| RF01 | A aplicação deve permitir o login de usuários (Admin, Gestor e Cliente) com e-mail e senha, exibindo o painel conforme o perfil. | Todas |
| RF02 | A aplicação deve restringir o acesso a cada funcionalidade conforme o perfil do usuário autenticado. | Todas |
| RF03 | A aplicação deve permitir que usuários não autenticados consultem a programação pública (filmes em cartaz e sessões disponíveis). | Visitante |

## 2. Cadastro do Cliente

| ID | Requisito | Persona |
|---|---|---|
| RF04 | A aplicação deve permitir que o cliente crie a própria conta informando nome, e-mail, idade e endereço (logradouro, número, complemento, bairro, cidade, estado e CEP). | Cliente |
| RF05 | A aplicação deve validar que o e-mail do cliente é único no sistema. | Cliente |
| RF06 | A aplicação deve permitir que o cliente edite os próprios dados de cadastro (endereço, idade e e-mail). | Cliente |
| RF07 | A aplicação deve permitir que o cliente visualize os próprios dados de cadastro. | Cliente |

## 3. Gestão de Filmes (Catálogo)

| ID | Requisito | Persona |
|---|---|---|
| RF08 | A aplicação deve permitir cadastrar filme com: título, duração, gênero, sinopse, cartaz (URL de imagem), faixa etária, especificação do elenco e nacionalidade. | Gestor, Admin |
| RF09 | A aplicação deve permitir editar e excluir filmes do catálogo. | Gestor, Admin |
| RF10 | A aplicação deve permitir listar e buscar filmes do catálogo. | Gestor, Admin |

## 4. Gestão de Salas

| ID | Requisito | Persona |
|---|---|---|
| RF11 | A aplicação deve permitir cadastrar sala com: quantidade de assentos, horário de funcionamento e especificação técnica. | Gestor, Admin |
| RF12 | A aplicação deve permitir editar e excluir salas. | Gestor, Admin |
| RF13 | A aplicação deve permitir listar e buscar salas. | Gestor, Admin |

## 5. Gestão de Sessões (Programação)

| ID | Requisito | Persona |
|---|---|---|
| RF14 | A aplicação deve permitir cadastrar sessão vinculando filme e sala, com data/hora de início, duração e valor do ingresso. | Gestor, Admin |
| RF15 | A aplicação deve validar que a nova sessão não se sobrepõe (em data/horário) a outra sessão da mesma sala. | Gestor, Admin |
| RF16 | A aplicação deve permitir editar e cancelar sessões. | Gestor, Admin |
| RF17 | A aplicação deve permitir consultar a programação filtrando por sala, filme ou período. | Gestor, Admin, Cliente, Visitante |
| RF18 | A aplicação deve exibir, ao Gestor, o indicador da cota de filme nacional do dia (RN04), com base na nacionalidade do filme de cada sessão. | Gestor, Admin |
| RF19 | A aplicação deve impedir a publicação da programação de um dia sem ao menos uma sessão de filme nacional (RN04). | Gestor, Admin |

## 6. Reservas (Cliente)

| ID | Requisito | Persona |
|---|---|---|
| RF20 | A aplicação deve exibir o mapa de assentos de uma sessão, diferenciando assentos livres e ocupados. | Cliente |
| RF21 | A aplicação deve permitir que o cliente selecione um ou mais assentos livres na mesma sessão (RN02). | Cliente |
| RF22 | A aplicação deve registrar a reserva de cada assento selecionado, tornando-o um assento válido e ocupado para a sessão (RN01). | Cliente |
| RF23 | A aplicação deve bloquear a seleção/reserva de um assento já ocupado por outro cliente na mesma sessão (RN01). | Cliente |
| RF24 | A aplicação deve validar, no momento da reserva, se o horário da sessão escolhida conflita (sobrepõe) com sessões já reservadas pelo mesmo cliente, bloqueando a operação (RN03). | Cliente |
| RF25 | A aplicação deve exibir ao cliente a confirmação da reserva com sessão, assentos e valor. | Cliente |
| RF26 | A aplicação deve permitir que o cliente consulte a lista das próprias reservas. | Cliente |

## 7. Administração do Sistema

| ID | Requisito | Persona |
|---|---|---|
| RF27 | A aplicação deve permitir ao Admin criar, editar, ativar/desativar e excluir contas de Gestores e Clientes. | Admin |
| RF28 | A aplicação deve permitir ao Admin gerenciar as permissões dos perfis de acesso. | Admin |
| RF29 | A aplicação deve permitir ao Admin visualizar todas as entidades do sistema (usuários, filmes, salas, sessões, clientes e reservas) em um dashboard. | Admin |
| RF30 | A aplicação deve permitir ao Admin consultar as reservas de qualquer cliente e cancelá-las, liberando os assentos. | Admin |

## Matriz de Rastreabilidade

| Regra de Negócio | Requisitos que a atendem |
|---|---|
| RN01 — Assento válido | RF20, RF22, RF23, RF30 |
| RN02 — Múltiplos assentos | RF21, RF25 |
| RN03 — Conflito de sessões | RF24, RF15 |
| RN04 — Cota de filme nacional | RF08, RF18, RF19 |
