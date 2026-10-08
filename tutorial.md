# Tutorial — CineSenac: Construção do PRD do Zero

Este tutorial documenta, passo a passo, como construímos o Product Requirement Document (PRD) do **CineSenac** — sistema de gestão de sessões de cinema — a partir de conversas guiadas por prompts. Cada passo mostra o prompt utilizado e o artefato gerado.

## O que o sistema é

Sistema de gestão de sessões de cinema com três perfis de acesso:

- **Admin do Sistema** — acesso total a todos os fluxos
- **Gestor** — cadastra salas, filmes e sessões
- **Cliente** — cadastro próprio (endereço, idade, e-mail) e reserva de assentos

## Estrutura final gerada

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

---

## Passo 1 — Visão do produto, README e personas

### Prompt

> "Me ajude a criar um sistema de gestão de sessões de cinema que vai ter um admin de sistema que terá acesso à todos os fluxos. Um Gestor que poderá cadastrar uma sala, um filme e uma sessão. E por final teremos um cliente que terá o seu cadastro de endereço, idade, e-mail. Neste momento crie apenas o readme e inicie a pasta PRD /prd com a pasta de persona e um md para cada persona desta com os objetivos declarados"

### Resultado

- `README.md` — visão geral do projeto, tabela de personas, estrutura de pastas e roadmap
- `prd/personas/admin-sistema.md` — persona com acesso irrestrito a todos os fluxos, objetivos e permissões
- `prd/personas/gestor.md` — persona responsável por cadastrar salas, filmes e sessões
- `prd/personas/cliente.md` — persona que realiza o próprio cadastro (endereço, idade, e-mail)

**Aprendizado:** começar pelo README e pelas personas dá um vocabulário comum ao projeto antes de escrever qualquer requisito.

---

## Passo 2 — Regras de reserva do cliente

### Prompt

> "ok, para a persona do cliente, ele poderá escolher e selecionar a sessão/filme que ele quer, e isso contará como um assento válido. Ele poderá também escolher mais de um assento, mas não pode escolher sessões que conflitem."

### Resultado

Atualização de `prd/personas/cliente.md` com:

- Novos objetivos: selecionar sessão/filme (gera assento válido) e reservar múltiplos assentos
- Três regras de negócio formais:
  - **RN01 — Assento válido:** cada seleção ocupa 1 assento, que fica marcado como ocupado
  - **RN02 — Múltiplos assentos:** o cliente pode reservar mais de um assento na mesma sessão
  - **RN03 — Conflito de sessões:** é proibido reservar sessões com horários sobrepostos

**Aprendizado:** transformar frases do usuário em regras numeradas (RNxx) facilita a rastreabilidade depois.

---

## Passo 3 — Cota de filme nacional

### Prompt

> "a gente vai resolver isso quando fizermos a modelagem de dados. enquanto isso o gestor deverá cadastrar ao menos uma sessão de filme nacional de acordo com a lei, por dia, modifique isso"

### Resultado

Atualização de `prd/personas/gestor.md` com:

- Objetivo: garantir a cota de filme nacional por dia
- **RN04 — Cota de filme nacional:** ao menos uma sessão de filme nacional por dia, em conformidade com a legislação de proteção ao cinema brasileiro (cota de tela)

**Aprendizado:** a RN04 gerou uma consequência de modelo: o cadastro de filme precisaria do atributo **nacionalidade** — adiado para a modelagem de dados, como combinado.

---

## Passo 4 — Modelagem de dados (DBML / dbdiagram)

### Prompt

> "por conta do sistema relacional, teremos que criar a modelagem de dados. e temos algumas regras: para o gestor cadastrar um filme: titulo, duração, genero, sinopse, cartaz (url de uma imagem), faixa etária, especificação do elenco | sala: qnt de assentos, horário de funcionamento, especificação técnica | sessão: duração, valor (preço ingresso) filme | cliente tem que ter uma tabela de endereço associada, idade, e-mail e nome. Crie em formato dbdiagram"

### Resultado

Criação de `prd/dbdiagram.dbml` (importável em [dbdiagram.io](https://dbdiagram.io/d)) com as tabelas:

| Tabela | Campos principais |
|---|---|
| `clientes` | nome, email (unique), idade |
| `enderecos` | logradouro, numero, complemento, bairro, cidade, estado, cep |
| `filmes` | titulo, duracao_minutos, genero, sinopse, cartaz_url, faixa_etaria (enum), elenco, nacionalidade (enum) |
| `salas` | qtd_assentos, hora_abertura, hora_fechamento, especificacao_tecnica |
| `sessoes` | filme_id, sala_id, data_hora_inicio, duracao_minutos, valor_ingresso |
| `assentos` | sala_id, codigo (A1, B7...) |
| `reservas` | cliente_id, sessao_id, assento_id — unique (sessao, assento) |

Decisões além do pedido (todas comentadas no arquivo):

- Tabelas `assentos` + `reservas` para suportar RN01–RN03
- `nacionalidade` em filmes para a RN04
- `sala_id` e `data_hora_inicio` em `sessoes` (sessão vincula filme a sala com data/horário)

---

## Passo 5 — Simplificação do modelo

### Prompt

> "para não termos muita verbosidade, vamos conectar o cliente_id direto com a reserva, e a tabela de endereço fica solitária"

### Resultado

- `reservas.cliente_id` mantido conectado direto ao cliente
- Tabela `enderecos` sem FK — ficou "solitária" no diagrama

---

## Passo 6 — Confirmação: e-mail único

### Prompt

> "não se esqueça que o e-mail é unique no cliente"

### Resultado

Verificação: `clientes.email varchar [unique, not null]` já estava no modelo.

---

## Passo 7 — Fusão do endereço na tabela do cliente

### Prompt

> "a tabela de endereço, por ser 1:1 com o cliente, podemos juntar os atributos e deixar apenas a tabela de clientes"

### Resultado

- Atributos de endereço (logradouro, numero, complemento, bairro, cidade, estado, cep) incorporados à tabela `clientes`
- Tabela `enderecos` removida do DBML
- Modelo final: `clientes` (com endereço), `filmes`, `salas`, `assentos`, `sessoes`, `reservas`

---

## Passo 8 — Jornadas das personas (front end)

### Prompt

> "Agora vamos adicionar às personas, a sua jornada na aplicação, pois iremos ter um front end completo. para cada persona sugira uma jornada"

### Resultado

Seção "Jornada na Aplicação" adicionada a cada persona:

- **Admin:** login → dashboard geral → gestão de usuários/permissões → CRUD de catálogo e sessões → monitoramento de reservas
- **Gestor:** login → dashboard de programação (indicador da RN04) → cadastro de filme → sala → sessão (validação de sobreposição) → consulta e manutenção
- **Cliente:** navegação pública → cadastro → login → exploração → seleção de sessão → mapa de assentos (RN01/RN02) → validação de conflito (RN03) → confirmação → minhas reservas

---

## Passo 9 — Requisitos funcionais

### Prompt

> "Agora vamos criar um md. de requisitos funcionais, e apenas funcionais. o que a minha aplicação tem que fazer para atender a jornada e os objetivos das personas"

### Resultado

Criação de `prd/requisitos-funcionais.md` com **30 requisitos (RF01–RF30)** em 7 módulos:

1. Autenticação e controle de acesso (RF01–RF03)
2. Cadastro do cliente (RF04–RF07)
3. Gestão de filmes (RF08–RF10)
4. Gestão de salas (RF11–RF13)
5. Gestão de sessões (RF14–RF19)
6. Reservas (RF20–RF26)
7. Administração do sistema (RF27–RF30)

Encerrando com a **matriz de rastreabilidade** RN01–RN04 → RFs que as atendem.

---

## Resumo do método

1. **Personas primeiro** — quem usa o sistema e com quais objetivos
2. **Regras de negócio numeradas** — frases viram RNxx rastreáveis
3. **Modelagem de dados** — entidades e campos derivados das personas e das RNs
4. **Jornadas** — o caminho de cada persona nas telas do front end
5. **Requisitos funcionais** — o que a aplicação deve fazer para atender às jornadas, com matriz de rastreabilidade

## Próximos passos sugeridos

- [ ] Requisitos não funcionais (segurança, desempenho, usabilidade)
- [ ] Fluxos de navegação / wireframes das telas
- [ ] Definição da stack (front end, back end, banco de dados)
- [ ] Desenvolvimento
