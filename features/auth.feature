# language: pt
Funcionalidade: Autenticação, controle de acesso e proteção CSRF
  O visitante entra com e-mail e senha. Cada perfil acessa apenas o que lhe cabe.
  Sustenta RF01, RF02, RNF28, RNF29, RNF30 e a proteção contra falsificação de requisição.

  Contexto:
    Dado que o sistema está em execução

  # Equivale a: tests/test_auth.py::TestRF01Login::test_login_com_credenciais_validas_cria_sessao
  Cenário: RF01 - login com credenciais válidas cria a sessão
    Quando o visitante envia POST "/v1/autenticacao" com os dados:
      """
      {"email": "admin@cinesenac.test", "senha": "senha-admin-forte-123"}
      """
    Então a resposta tem status 200
    Então o campo "usuario.perfil" é "admin"
    Quando o visitante envia GET "/v1/sessao"
    Então o campo "usuario.email" é "admin@cinesenac.test"

  # Equivale a: tests/test_auth.py::TestRF01Login::test_credenciais_invalidas_retornam_401_generico
  Cenário: RF01 - credenciais inválidas retornam a mesma resposta genérica
    Quando o visitante envia POST "/v1/autenticacao" com os dados:
      """
      {"email": "admin@cinesenac.test", "senha": "errada-123456"}
      """
    Então a resposta tem status 401
    Quando o visitante envia POST "/v1/autenticacao" com os dados:
      """
      {"email": "ninguem@exemplo.com", "senha": "errada-123456"}
      """
    Então a resposta tem status 401
    Então o corpo da resposta é igual ao da resposta anterior
    Então o código de erro é "credenciais_invalidas"

  # Equivale a: tests/test_auth.py::TestRF01Login::test_cookie_de_sessao_e_httponly_e_samesite
  Cenário: RNF28 - o cookie de sessão não é acessível a scripts e tem SameSite
    Quando o visitante envia POST "/v1/autenticacao" com os dados:
      """
      {"email": "admin@cinesenac.test", "senha": "senha-admin-forte-123"}
      """
    Então o cookie de sessão é HttpOnly e SameSite Lax

  # Equivale a: tests/test_auth.py::TestRF01Login::test_conta_desativada_nao_entra
  Cenário: RF27 - uma conta desativada não consegue entrar
    Dado que existe um gestor "gestor@cinesenac.test"
    Dado que a conta "gestor@cinesenac.test" foi desativada pelo admin
    Quando o visitante tenta entrar com "gestor@cinesenac.test" e senha "senha-gestor-forte-123"
    Então a resposta tem status 401

  # Equivale a: tests/test_auth.py::TestRF01Login::test_logout_encerra_a_sessao
  Cenário: RF01 - o logout encerra a sessão
    Dado que o admin está autenticado
    Quando o admin envia DELETE "/v1/autenticacao"
    Então a resposta tem status 204
    Quando o admin envia GET "/v1/sessao"
    Então o campo "usuario" é null

  # Equivale a: tests/test_auth.py::TestRNF30LimiteDeTentativas::test_bloqueia_apos_tentativas_excessivas
  Cenário: RNF30 - tentativas excessivas bloqueiam o login, mesmo com a senha certa
    Dado que o visitante errou a senha de "admin@cinesenac.test" 5 vezes
    Quando o visitante tenta entrar com "admin@cinesenac.test" e senha "senha-admin-forte-123"
    Então a resposta tem status 429
    Então o código de erro é "muitas_tentativas"

  # Equivale a: tests/test_auth.py::TestRF02ControleDeAcesso::test_rota_protegida_sem_login_retorna_401
  Cenário: RF02 - rota protegida sem login retorna 401
    Quando o visitante envia GET "/v1/filmes"
    Então a resposta tem status 401
    Então o código de erro é "nao_autenticado"

  # Equivale a: tests/test_auth.py::TestRF02ControleDeAcesso::test_perfil_sem_permissao_retorna_403
  Cenário: RF02 - perfil sem permissão recebe 403
    Dado que o cliente está autenticado
    Quando o cliente envia GET "/v1/filmes"
    Então a resposta tem status 403
    Então o código de erro é "sem_permissao"

  # Equivale a: tests/test_auth.py::TestRF02ControleDeAcesso::test_sessao_de_conta_desativada_deixa_de_valer
  Cenário: RNF28 - a sessão de uma conta desativada deixa de valer na próxima requisição
    Dado que o cliente está autenticado
    Dado que a conta "ana@exemplo.com" foi desativada pelo admin
    Quando o cliente envia GET "/v1/clientes/{cliente_id}"
    Então a resposta tem status 401

  # Equivale a: tests/test_auth.py::TestCSRF::test_escrita_sem_token_csrf_e_recusada
  Cenário: RNF31 - escrita sem token CSRF é recusada
    Quando o visitante envia POST "/v1/clientes" sem token CSRF com os dados:
      """
      {"email": "x@exemplo.com", "senha": "senha-forte-123456", "nome": "X", "idade": 20,
       "endereco": {"logradouro": "R", "numero": "1", "bairro": "B", "cidade": "C",
                    "estado": "SP", "cep": "01000-000"}}
      """
    Então a resposta tem status 403
    Então o código de erro é "csrf_invalido"

  # Equivale a: tests/test_auth.py::TestCSRF::test_token_de_outra_sessao_e_recusado
  Cenário: RNF31 - um token CSRF de outra sessão é recusado
    Quando o visitante envia POST "/v1/autenticacao" com o token CSRF de outra sessão e os dados:
      """
      {"email": "admin@cinesenac.test", "senha": "senha-admin-forte-123"}
      """
    Então a resposta tem status 403
