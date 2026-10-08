# Persona: Cliente

## Descrição

Usuário final do sistema. Realiza o próprio cadastro na plataforma informando **endereço**, **idade** e **e-mail**. Além disso, escolhe sessões/filmes e reserva assentos, respeitando as regras de ocupação e de conflito de horários.

## Objetivos

- Criar a própria conta: realizar o cadastro com endereço, idade e e-mail.
- Manter o cadastro atualizado: editar endereço, idade e e-mail sempre que necessário.
- Consultar os próprios dados: visualizar as informações da sua conta.
- Consultar a programação: visualizar filmes e sessões disponíveis.
- Escolher e selecionar a sessão/filme desejado: cada seleção confirma um assento válido na sessão.
- Reservar mais de um assento: pode selecionar múltiplos assentos na mesma sessão.

## Jornada na Aplicação

1. **Acesso público** — navega por filmes em cartaz e sessões disponíveis, sem precisar de login.
2. **Cadastro** — cria a própria conta informando nome, e-mail (único), idade e endereço.
3. **Login** — acessa sua área no sistema.
4. **Exploração** — filtra sessões por filme, data ou sala.
5. **Seleção de sessão/filme** — escolhe a sessão desejada.
6. **Mapa de assentos** — seleciona um ou mais assentos disponíveis (RN02); assentos já reservados aparecem como ocupados (RN01).
7. **Validação de conflito** — o sistema bloqueia a reserva caso a sessão conflite com horário de sessão já reservada pelo cliente (RN03).
8. **Confirmação** — revisa e confirma a reserva, que passa a valer como assento(s) válido(s).
9. **Minhas reservas** — consulta as reservas realizadas; pode manter o cadastro atualizado (endereço, idade, e-mail).

## Regras de Negócio

- **RN01 — Assento válido:** toda seleção de sessão/filme pelo cliente corresponde a um assento válido, que passa a constar como ocupado naquela sessão.
- **RN02 — Múltiplos assentos:** o cliente pode reservar mais de um assento, desde que os assentos estejam disponíveis na sessão escolhida.
- **RN03 — Conflito de sessões:** o cliente não pode reservar assentos em sessões com horários conflitantes (sobreposição de data/hora entre sessões já reservadas por ele).

## Permissões

| Fluxo | Acesso |
|---|---|
| Cadastro da própria conta (endereço, idade, e-mail) | Total |
| Edição do próprio cadastro | Total |
| Seleção de sessão/filme e reserva de assentos | Total |
| Cadastro de filmes, salas e sessões | Sem acesso |
| Gestão de usuários e permissões | Sem acesso |
