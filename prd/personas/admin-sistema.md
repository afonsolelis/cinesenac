# Persona: Admin do Sistema

## Descrição

Responsável pela administração global do sistema. Possui acesso irrestrito a **todos os fluxos** da plataforma, incluindo os fluxos de Gestor e Cliente, além das funcionalidades exclusivas de administração.

## Objetivos

- Ter visão completa e controle total sobre todas as entidades do sistema (usuários, filmes, salas e sessões).
- Gerenciar usuários do sistema: criar, editar, ativar/desativar e excluir contas de Gestores e Clientes.
- Administrar o catálogo de filmes: criar, editar e remover registros.
- Administrar as salas: criar, editar e remover salas.
- Administrar as sessões: criar, editar, cancelar e remover sessões.
- Gerenciar permissões e perfis de acesso.
- Monitorar a integridade e a consistência dos dados da plataforma.
- Resolver exceções e conflitos que Gestores e Clientes não consigam resolver por conta própria.

## Jornada na Aplicação

1. **Login** — acessa o painel administrativo com credenciais próprias.
2. **Dashboard** — visualiza a visão geral do sistema: filmes, salas, sessões do dia, clientes e reservas.
3. **Gestão de usuários** — cria, edita, ativa/desativa e exclui contas de Gestores e Clientes; define permissões de acesso.
4. **Gestão do catálogo** — administra filmes e salas com CRUD completo (mesmos fluxos do Gestor).
5. **Gestão de sessões** — cria, edita, cancela e remove sessões (mesmos fluxos do Gestor).
6. **Monitoramento de reservas** — consulta reservas de qualquer cliente, resolve conflitos de horário e exceções que Gestores e Clientes não consigam resolver.
7. **Encerramento** — encerra a sessão com segurança.

## Permissões

| Fluxo | Acesso |
|---|---|
| Gestão de usuários (Gestores e Clientes) | Total |
| Cadastro de filmes | Total |
| Cadastro de salas | Total |
| Cadastro de sessões | Total |
| Cadastro de clientes | Total |
