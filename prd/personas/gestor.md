# Persona: Gestor

## Descrição

Profissional da equipe do cinema responsável pela operação do catálogo. Pode cadastrar **salas**, **filmes** e **sessões**, mantendo a programação do cinema atualizada.

## Objetivos

- Cadastrar salas: registrar novas salas com suas informações (nome/código, capacidade, etc.).
- Editar e manter salas: atualizar dados e status das salas existentes.
- Cadastrar filmes: incluir novos filmes no catálogo com suas informações (título, sinopse, duração, classificação indicativa, etc.).
- Editar e manter filmes: atualizar dados do catálogo de filmes.
- Cadastrar sessões: criar sessões vinculando um filme a uma sala, com data e horário.
- Editar e manter sessões: ajustar ou cancelar sessões conforme a programação.
- Consultar a programação: visualizar sessões por sala, filme ou período.
- Garantir a cota de filme nacional: assegurar o cadastro de ao menos uma sessão de filme nacional por dia, em conformidade com a legislação vigente.

## Jornada na Aplicação

1. **Login** — acessa o painel do gestor com credenciais próprias.
2. **Dashboard de programação** — visualiza o calendário de sessões por sala/dia e o indicador da cota de filme nacional do dia (RN04).
3. **Cadastro de filme** — preenche o formulário com título, duração, gênero, sinopse, cartaz (URL da imagem), faixa etária, elenco e nacionalidade.
4. **Cadastro de sala** — preenche quantidade de assentos, horário de funcionamento e especificação técnica.
5. **Cadastro de sessão** — seleciona filme e sala, define data/hora, duração e valor do ingresso; o sistema valida sobreposição de horários na sala.
6. **Consulta de programação** — filtra sessões por sala, filme ou período.
7. **Manutenção de sessões** — edita ou cancela sessões conforme a necessidade da programação.

## Regras de Negócio

- **RN04 — Cota de filme nacional:** o Gestor deve cadastrar, obrigatoriamente, ao menos uma sessão de filme nacional por dia, em atendimento à legislação de proteção ao cinema brasileiro (cota de tela). A programação não pode ser publicada para um dia sem essa sessão.

## Permissões

| Fluxo | Acesso |
|---|---|
| Cadastro de salas | Total |
| Cadastro de filmes | Total |
| Cadastro de sessões | Total |
| Gestão de usuários | Sem acesso |
| Gestão de permissões | Sem acesso |
