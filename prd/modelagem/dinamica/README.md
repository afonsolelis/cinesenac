# Modelagem dinâmica — Sequências por requisito funcional

Um diagrama de sequência em Mermaid por RF. Cada arquivo traz as personas, os RNFs que o fluxo realiza e as entidades usadas. Os diagramas são validados contra o parser Mermaid antes de entrar no repositório.

Visão estática de apoio: [componentes](../estatica/componentes.md) e [classes](../estatica/classes.md).

| RF | Requisito | Personas | RNFs realizados | Diagrama |
|---|---|---|---|---|
| RF01 | Login por perfil | Todas. | RNF28, RNF30 | [RF01-login.md](RF01-login.md) |
| RF02 | Controle de acesso por perfil | Todas. | RNF29 | [RF02-controle-de-acesso.md](RF02-controle-de-acesso.md) |
| RF03 | Consulta pública da programação | Visitante. | RNF06, RNF08, RNF09, RNF11, RNF12, RNF13, RNF14, RNF27 | [RF03-consulta-publica-programacao.md](RF03-consulta-publica-programacao.md) |
| RF04 | Cadastro do cliente | Cliente. | RNF03, RNF22, RNF31, RNF32, RNF41 | [RF04-cadastro-cliente.md](RF04-cadastro-cliente.md) |
| RF05 | E-mail único | Cliente, Admin. | RNF03, RNF20 | [RF05-email-unico.md](RF05-email-unico.md) |
| RF06 | Edição do cadastro do cliente | Cliente. | RNF03, RNF29, RNF31, RNF32 | [RF06-edicao-cadastro-cliente.md](RF06-edicao-cadastro-cliente.md) |
| RF07 | Visualização do cadastro do cliente | Cliente. | RNF32 | [RF07-visualizacao-cadastro-cliente.md](RF07-visualizacao-cadastro-cliente.md) |
| RF08 | Cadastro de filme | Gestor, Admin. | RNF05, RNF13, RNF22, RNF31, RNF37, RNF41 | [RF08-cadastro-filme.md](RF08-cadastro-filme.md) |
| RF09 | Edição e exclusão de filme | Gestor, Admin. | RNF13, RNF29, RNF31, RNF37 | [RF09-edicao-exclusao-filme.md](RF09-edicao-exclusao-filme.md) |
| RF10 | Listagem e busca de filmes | Gestor, Admin. | RNF06, RNF13, RNF37 | [RF10-listagem-busca-filmes.md](RF10-listagem-busca-filmes.md) |
| RF11 | Cadastro de sala | Gestor, Admin. | RNF22, RNF37, RNF41 | [RF11-cadastro-sala.md](RF11-cadastro-sala.md) |
| RF12 | Edição e exclusão de sala | Gestor, Admin. | RNF29, RNF37 | [RF12-edicao-exclusao-sala.md](RF12-edicao-exclusao-sala.md) |
| RF13 | Listagem e busca de salas | Gestor, Admin. | RNF06, RNF37 | [RF13-listagem-busca-salas.md](RF13-listagem-busca-salas.md) |
| RF14 | Cadastro de sessão | Gestor, Admin. | RNF04, RNF22, RNF41 | [RF14-cadastro-sessao.md](RF14-cadastro-sessao.md) |
| RF15 | Sobreposição de sessão na sala | Gestor, Admin. | RNF04, RNF20, RNF34 | [RF15-sobreposicao-sessao.md](RF15-sobreposicao-sessao.md) |
| RF16 | Edição e cancelamento de sessão | Gestor, Admin. | RNF04, RNF29, RNF33 | [RF16-edicao-cancelamento-sessao.md](RF16-edicao-cancelamento-sessao.md) |
| RF17 | Consulta da programação com filtros | Visitante, Cliente, Gestor, Admin. | RNF06, RNF08, RNF09, RNF11, RNF12, RNF14, RNF27 | [RF17-consulta-programacao-filtros.md](RF17-consulta-programacao-filtros.md) |
| RF18 | Indicador da cota nacional | Gestor, Admin. | RNF05, RNF34 | [RF18-indicador-cota-nacional.md](RF18-indicador-cota-nacional.md) |
| RF19 | Bloqueio de publicação sem cota nacional | Gestor, Admin. | RNF05, RNF34 | [RF19-bloqueio-publicacao.md](RF19-bloqueio-publicacao.md) |
| RF20 | Mapa de assentos | Cliente. | RNF06, RNF08, RNF09, RNF10, RNF11, RNF12, RNF19, RNF21, RNF27, RNF37 | [RF20-mapa-assentos.md](RF20-mapa-assentos.md) |
| RF21 | Seleção de assentos | Cliente. | RNF01, RNF02, RNF07, RNF08, RNF10, RNF19, RNF21, RNF24, RNF27, RNF34 | [RF21-selecao-assentos.md](RF21-selecao-assentos.md) |
| RF22 | Registro da reserva | Cliente. | RNF01, RNF07, RNF08, RNF21, RNF24, RNF25, RNF26, RNF34, RNF41 | [RF22-registro-reserva.md](RF22-registro-reserva.md) |
| RF23 | Bloqueio de assento ocupado | Cliente. | RNF01, RNF20, RNF34 | [RF23-bloqueio-assento-ocupado.md](RF23-bloqueio-assento-ocupado.md) |
| RF24 | Conflito de horário do cliente | Cliente. | RNF02, RNF20, RNF34 | [RF24-conflito-horario-cliente.md](RF24-conflito-horario-cliente.md) |
| RF25 | Confirmação da reserva | Cliente. | RNF07, RNF21 | [RF25-confirmacao-reserva.md](RF25-confirmacao-reserva.md) |
| RF26 | Minhas reservas | Cliente. | RNF06, RNF12, RNF32 | [RF26-minhas-reservas.md](RF26-minhas-reservas.md) |
| RF27 | Gestão de contas pelo Admin | Admin. | RNF26, RNF28, RNF29, RNF32, RNF33 | [RF27-gestao-contas-admin.md](RF27-gestao-contas-admin.md) |
| RF28 | Gestão de permissões dos perfis | Admin. | RNF29, RNF33 | [RF28-permissoes-perfis.md](RF28-permissoes-perfis.md) |
| RF29 | Dashboard do Admin | Admin. | RNF06, RNF08, RNF37, RNF38 | [RF29-dashboard-admin.md](RF29-dashboard-admin.md) |
| RF30 | Cancelamento de reserva pelo Admin | Admin. | RNF01, RNF26, RNF29, RNF33 | [RF30-cancelamento-reserva-admin.md](RF30-cancelamento-reserva-admin.md) |

## Como ler

- **Participantes:** o ator é a persona. `FE` é o frontend, `API` é a camada de aplicação, `DB` é o banco. Os demais participantes aparecem quando o fluxo os usa.
- **Blocos `alt` e `else`:** caminhos de erro e de sucesso. Os códigos de status são indicativos e seguem o padrão já usado em [fluxos-sequencia.md](../../fluxos-sequencia.md).
- **Notas `Note over`:** regras que ainda não foram definidas aparecem como **a definir**. São pendências, não decisões.
- **Notas de RNF:** cada diagrama termina com a explicação de como o fluxo cumpre cada RNF listado.

## Pendências que aparecem nos diagramas

- [RF09](RF09-edicao-exclusao-filme.md) e [RF12](RF12-edicao-exclusao-sala.md): regra de exclusão com sessões vinculadas.
- [RF12](RF12-edicao-exclusao-sala.md): tratamento de assentos reservados quando a quantidade muda.
- [RF16](RF16-edicao-cancelamento-sessao.md): tratamento de reservas de uma sessão cancelada.
- [RF27](RF27-gestao-contas-admin.md) e [RF28](RF28-permissoes-perfis.md): entidades Usuario, Perfil, Permissao e RegistroAuditoria não existem no DBML ainda.

Ver também [modelagem/README.md](../README.md).
