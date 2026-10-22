# language: pt
Funcionalidade: Administração de contas, permissões e painel
  O admin cria e desativa contas, exclui contas sem reservas, gerencia permissões dos
  perfis e acompanha o dashboard e a auditoria.
  Sustenta RF27 a RF29, RF28, RNF28, RNF29 e RNF33.

  Contexto:
    Dado que o sistema está em execução
    Dado que o admin está autenticado

  # Equivale a: tests/test_admin.py::TestRF27Contas::test_admin_cria_gestor
  Cenário: RF27 - o admin cria um gestor
    Quando o admin envia POST "/v1/usuarios" com os dados:
      """
      {"email": "novo.gestor@cinesenac.test", "senha": "senha-gestor-forte-123", "perfil": "gestor"}
      """
    Então a resposta tem status 201
    Então o campo "perfil" é "gestor"
    Então o campo "senha" não existe

  # Equivale a: tests/test_admin.py::TestRF27Contas::test_admin_cria_cliente_com_dados_de_cadastro
  Cenário: RF27 - o admin cria um cliente com os dados de cadastro
    Quando o admin envia POST "/v1/usuarios" com os dados:
      """
      {"email": "cliente.admin@exemplo.com", "senha": "senha-cliente-forte-123", "perfil": "cliente",
       "cliente": {"nome": "Caio", "idade": 40,
                   "endereco": {"logradouro": "Rua das Flores", "numero": "100", "complemento": null,
                                "bairro": "Centro", "cidade": "São Paulo", "estado": "SP", "cep": "01000-000"}}}
      """
    Então a resposta tem status 201
    Então o campo "perfil" é "cliente"
    Então o campo "cliente_id" não é null

  # Equivale a: tests/test_admin.py::TestRF27Contas::test_cliente_sem_dados_de_cadastro_retorna_422
  Cenário: RF27 - cliente criado sem dados de cadastro é recusado
    Quando o admin envia POST "/v1/usuarios" com os dados:
      """
      {"email": "sem.dados@exemplo.com", "senha": "senha-cliente-forte-123", "perfil": "cliente"}
      """
    Então a resposta tem status 422
    Então o campo "campos" contém "cliente"

  # Equivale a: tests/test_admin.py::TestRF27Contas::test_email_duplicado_em_conta_retorna_409
  Cenário: RF27 - e-mail de conta já existente é recusado
    Quando o admin envia POST "/v1/usuarios" com os dados:
      """
      {"email": "admin@cinesenac.test", "senha": "senha-forte-123456", "perfil": "gestor"}
      """
    Então a resposta tem status 409
    Então o código de erro é "email_duplicado"

  # Equivale a: tests/test_admin.py::TestRF27Contas::test_admin_desativa_conta
  Cenário: RF27 - o admin desativa uma conta
    Dado que existe um gestor "gestor@cinesenac.test"
    Quando o admin altera a situação da conta "gestor@cinesenac.test" para desativada
    Então a resposta tem status 200
    Então o campo "ativo" é false

  # Equivale a: tests/test_admin.py::TestRF27Contas::test_admin_exclui_cliente_sem_reservas
  Cenário: RF27 - o admin exclui um cliente sem reservas
    Dado que existe um cliente com e-mail "sem.reserva@exemplo.com"
    Quando o admin exclui a conta "sem.reserva@exemplo.com"
    Então a resposta tem status 204
    Então a conta "sem.reserva@exemplo.com" não existe

  # Equivale a: tests/test_admin.py::TestRF27Contas::test_conta_com_reservas_nao_e_excluida
  Cenário: RF27 - conta com reservas não é excluída
    Dado que o cliente está autenticado
    Dado que existe um filme "Filme"
    Dado que existe uma sala "Sala" com 3 assentos
    Dado que existe uma sessão "s" do filme "Filme" na sala "Sala" em "19:00" com 120 minutos e valor "25.00"
    Dado que o dia "2026-11-02" está publicado
    Dado que o cliente reservou "A1" na sessão "s"
    Quando o admin exclui a conta "ana@exemplo.com"
    Então a resposta tem status 409
    Então o código de erro é "conta_com_reservas"

  # Equivale a: tests/test_admin.py::TestRF27Contas::test_admin_nao_exclui_a_propria_conta
  Cenário: RF27 - o admin não exclui a própria conta
    Quando o admin exclui a conta "admin@cinesenac.test"
    Então a resposta tem status 409
    Então o código de erro é "operacao_nao_permitida"

  # Equivale a: tests/test_admin.py::TestRF27Contas::test_acoes_de_conta_geram_auditoria
  Cenário: RNF33 - a criação de conta fica registrada na auditoria
    Quando o admin envia POST "/v1/usuarios" com os dados:
      """
      {"email": "audit@cinesenac.test", "senha": "senha-forte-123456", "perfil": "gestor"}
      """
    Então a resposta tem status 201
    Então o administrador vê a ação "usuario.criar" na auditoria

  # Equivale a: tests/test_admin.py::TestRF27Contas::test_gestor_nao_gerencia_contas
  Cenário: RF27 - o gestor não gerencia contas
    Dado que o gestor está autenticado
    Quando o gestor envia GET "/v1/usuarios"
    Então a resposta tem status 403

  # Equivale a: tests/test_admin.py::TestRF28Permissoes::test_admin_lista_permissoes_do_perfil
  Cenário: RF28 - o admin lista as permissões de um perfil
    Quando o admin envia GET "/v1/perfis/gestor/permissoes"
    Então o campo "perfil" é "gestor"
    Então o campo "permissoes" contém "catalogo:gerenciar"

  # Equivale a: tests/test_admin.py::TestRF28Permissoes::test_alteracao_de_permissao_vale_imediatamente
  Cenário: RF28 - a alteração de permissão vale na próxima requisição
    Dado que o gestor está autenticado
    Quando o admin envia PUT "/v1/perfis/gestor/permissoes" com os dados:
      """
      {"permissoes": ["programacao:gerenciar"]}
      """
    Então a resposta tem status 200
    Quando o gestor envia POST "/v1/filmes" com os dados:
      """
      {"titulo": "X"}
      """
    Então a resposta tem status 403

  # Equivale a: tests/test_admin.py::TestRF28Permissoes::test_admin_nao_remove_a_propria_permissao_de_gerir_permissoes
  Cenário: RF28 - o admin não remove a própria permissão de gerenciar permissões
    Quando o admin envia PUT "/v1/perfis/admin/permissoes" com os dados:
      """
      {"permissoes": ["catalogo:gerenciar"]}
      """
    Então a resposta tem status 422
    Então o código de erro é "permissao_obrigatoria"

  # Equivale a: tests/test_admin.py::TestRF28Permissoes::test_gestor_nao_gerencia_permissoes
  Cenário: RF28 - o gestor não gerencia permissões
    Dado que o gestor está autenticado
    Quando o gestor envia GET "/v1/perfis/gestor/permissoes"
    Então a resposta tem status 403

  # Equivale a: tests/test_admin.py::TestRF28Permissoes::test_alteracao_de_permissoes_gera_auditoria
  Cenário: RNF33 - a alteração de permissões fica registrada na auditoria
    Quando o admin envia PUT "/v1/perfis/gestor/permissoes" com os dados:
      """
      {"permissoes": ["catalogo:gerenciar", "programacao:gerenciar"]}
      """
    Então o administrador vê a ação "perfil.permissoes" na auditoria

  # Equivale a: tests/test_admin.py::TestRF29Dashboard::test_dashboard_resume_todas_as_entidades
  Cenário: RF29 - o dashboard resume todas as entidades
    Quando o admin envia GET "/v1/dashboard"
    Então o campo "usuarios" é um número
    Então o campo "clientes" é um número
    Então o campo "filmes" é um número
    Então o campo "salas" é um número
    Então o campo "sessoes" é um número
    Então o campo "reservas" é um número
    Então o campo "usuarios" é maior ou igual a 1

  # Equivale a: tests/test_admin.py::TestRF29Dashboard::test_gestor_nao_ve_dashboard
  Cenário: RF29 - o gestor não vê o dashboard
    Dado que o gestor está autenticado
    Quando o gestor envia GET "/v1/dashboard"
    Então a resposta tem status 403

  # Equivale a: tests/test_admin.py::TestRF29Dashboard::test_auditoria_so_para_admin
  Cenário: RNF33 - a auditoria é restrita ao admin
    Dado que o gestor está autenticado
    Quando o gestor envia GET "/v1/auditoria"
    Então a resposta tem status 403

  # Equivale a: tests/test_admin.py::TestProtecaoContraAutoBloqueio::test_admin_nao_desativa_a_propria_conta
  Cenário: RNF28 - o admin não desativa a própria conta
    Quando o admin altera a situação da conta "admin@cinesenac.test" para desativada
    Então a resposta tem status 409
    Então o código de erro é "operacao_nao_permitida"
    Quando o admin envia GET "/v1/sessao"
    Então o campo "usuario.email" é "admin@cinesenac.test"
