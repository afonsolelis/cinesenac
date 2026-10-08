# Fluxos — Diagramas UML de Sequência (Mermaid)

Documentação dos principais fluxos do CineSenac em UML de sequência, renderizada com [Mermaid](https://mermaid.js.org). Os fluxos cobrem os requisitos funcionais ([requisitos-funcionais.md](requisitos-funcionais.md)) e as regras de negócio RN01–RN04.

**Participantes padrão:**

- `U` — Usuário (ator da persona)
- `FE` — Frontend
- `API` — Backend/API
- `DB` — Banco de Dados

## 1. Autenticação (RF01, RF02)

```mermaid
sequenceDiagram
    actor U as Usuário
    participant FE as Frontend
    participant API as Backend/API
    participant DB as Banco de Dados

    U->>FE: Acessa a tela de login
    U->>FE: Informa e-mail e senha
    FE->>API: POST /login (email, senha)
    API->>DB: Busca usuário por e-mail
    DB-->>API: Registro do usuário

    alt Credenciais válidas
        API-->>FE: Token de sessão + perfil (Admin, Gestor ou Cliente)
        FE-->>U: Exibe painel conforme o perfil
    else Credenciais inválidas
        API-->>FE: 401 - Não autorizado
        FE-->>U: Exibe mensagem de erro
    end
```

## 2. Cadastro do cliente (RF04, RF05)

```mermaid
sequenceDiagram
    actor C as Cliente
    participant FE as Frontend
    participant API as Backend/API
    participant DB as Banco de Dados

    C->>FE: Abre o formulário de cadastro
    C->>FE: Preenche nome, e-mail, idade e endereço
    FE->>API: POST /clientes (dados do formulário)
    API->>DB: Verifica se o e-mail já existe

    alt E-mail já cadastrado (RF05)
        API-->>FE: 409 - E-mail duplicado
        FE-->>C: Solicita outro e-mail
    else E-mail disponível
        API->>DB: INSERT clientes (com endereço incorporado)
        DB-->>API: Cliente criado
        API-->>FE: 201 - Cadastro realizado
        FE-->>C: Exibe confirmação
    end
```

## 3. Cadastro de filme (RF08)

```mermaid
sequenceDiagram
    actor G as Gestor
    participant FE as Frontend
    participant API as Backend/API
    participant DB as Banco de Dados

    G->>FE: Abre o formulário de filme
    G->>FE: Preenche título, duração, gênero, sinopse, cartaz (URL), faixa etária, elenco e nacionalidade
    FE->>API: POST /filmes
    API->>API: Valida campos obrigatórios

    alt Dados válidos
        API->>DB: INSERT filmes
        DB-->>API: Filme criado
        API-->>FE: 201 - Filme cadastrado
        FE-->>G: Atualiza o catálogo
    else Dados inválidos
        API-->>FE: 400 - Erro de validação
        FE-->>G: Destaca os campos com erro
    end
```

## 4. Cadastro de sala (RF11, RF13)

```mermaid
sequenceDiagram
    actor G as Gestor
    participant FE as Frontend
    participant API as Backend/API
    participant DB as Banco de Dados

    G->>FE: Abre o formulário de sala
    G->>FE: Preenche nome, quantidade de assentos, horário de funcionamento e especificação técnica
    FE->>API: POST /salas
    API->>DB: INSERT salas
    API->>DB: Gera os assentos da sala (A1..An)
    DB-->>API: Sala e assentos criados
    API-->>FE: 201 - Sala cadastrada
    FE-->>G: Atualiza a lista de salas
```

## 5. Cadastro de sessão (RF14, RF15, RN04)

```mermaid
sequenceDiagram
    actor G as Gestor
    participant FE as Frontend
    participant API as Backend/API
    participant DB as Banco de Dados

    G->>FE: Abre o formulário de sessão
    G->>FE: Seleciona filme e sala, define data/hora, duração e valor do ingresso
    FE->>API: POST /sessoes
    API->>DB: Consulta sessões da mesma sala no período

    alt Há sobreposição de horário na sala (RF15)
        API-->>FE: 409 - Conflito de horário
        FE-->>G: Exibe erro e sugere outro horário
    else Sem sobreposição
        API->>DB: INSERT sessoes
        DB-->>API: Sessão criada
        API->>DB: Verifica cota de filme nacional do dia (RN04)

        alt Dia sem sessão de filme nacional
            API-->>FE: Aviso - programação do dia não publicável (RN04)
            FE-->>G: Exibe alerta da cota nacional
        else Cota atendida
            API-->>FE: 201 - Sessão cadastrada
            FE-->>G: Atualiza o calendário da programação
        end
    end
```

## 6. Reserva de assentos (RF20–RF25, RN01–RN03)

```mermaid
sequenceDiagram
    actor C as Cliente
    participant FE as Frontend
    participant API as Backend/API
    participant DB as Banco de Dados

    C->>FE: Seleciona a sessão desejada
    FE->>API: GET /sessoes/{id}/assentos
    API->>DB: Consulta assentos e reservas da sessão
    DB-->>API: Situação de cada assento (livre/ocupado)
    API-->>FE: Mapa de assentos
    FE-->>C: Exibe mapa (RN01 - ocupados bloqueados)
    C->>FE: Seleciona um ou mais assentos livres (RN02)
    FE->>API: POST /reservas (lista de assentos)
    API->>DB: Revalida disponibilidade dos assentos

    alt Assento ocupado entretanto (RN01)
        API-->>FE: 409 - Assento indisponível
        FE-->>C: Solicita nova escolha
    else Cliente já tem sessão conflitante (RN03)
        API-->>FE: 409 - Conflito de horário com outra reserva
        FE-->>C: Bloqueia e informa a reserva existente
    else Validações ok
        API->>DB: INSERT reservas (uma por assento)
        DB-->>API: Reservas criadas
        API-->>FE: 201 - Reserva confirmada
        FE-->>C: Exibe confirmação com sessão, assentos e valor (RF25)
    end
```

## 7. Consulta das próprias reservas (RF26)

```mermaid
sequenceDiagram
    actor C as Cliente
    participant FE as Frontend
    participant API as Backend/API
    participant DB as Banco de Dados

    C->>FE: Acessa "Minhas reservas"
    FE->>API: GET /clientes/{id}/reservas
    API->>DB: Consulta reservas do cliente autenticado
    DB-->>API: Lista de reservas (sessão, assentos, valor)
    API-->>FE: 200 - Lista de reservas
    FE-->>C: Exibe as reservas
```

## 8. Gestão de usuários (Admin) (RF27, RF30)

```mermaid
sequenceDiagram
    actor A as Admin
    participant FE as Frontend
    participant API as Backend/API
    participant DB as Banco de Dados

    A->>FE: Acessa a gestão de usuários
    FE->>API: GET /usuarios
    API->>DB: Lista Gestores e Clientes
    DB-->>API: Usuários
    API-->>FE: 200 - Usuários
    FE-->>A: Exibe a lista de usuários

    A->>FE: Cria, edita, ativa/desativa ou exclui um usuário
    FE->>API: POST/PATCH/DELETE /usuarios/{id}
    API->>API: Verifica permissões do perfil Admin
    API->>DB: Aplica a alteração
    DB-->>API: Confirmação
    API-->>FE: 200 - Usuário atualizado
    FE-->>A: Atualiza a lista

    opt Cancelamento de reserva (RF30)
        A->>FE: Cancela a reserva de um cliente
        FE->>API: DELETE /reservas/{id}
        API->>DB: Remove a reserva e libera o assento
        DB-->>API: Confirmação
        API-->>FE: 200 - Reserva cancelada
        FE-->>A: Atualiza as reservas
    end
```

## Cobertura

| Fluxo | Requisitos | Regras de negócio |
|---|---|---|
| 1. Autenticação | RF01, RF02 | — |
| 2. Cadastro do cliente | RF04, RF05 | — |
| 3. Cadastro de filme | RF08 | RN04 (nacionalidade) |
| 4. Cadastro de sala | RF11, RF13 | — |
| 5. Cadastro de sessão | RF14, RF15 | RN04 |
| 6. Reserva de assentos | RF20–RF25 | RN01, RN02, RN03 |
| 7. Minhas reservas | RF26 | — |
| 8. Gestão de usuários | RF27, RF30 | — |
