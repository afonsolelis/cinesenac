# language: pt
Funcionalidade: Páginas web (front end server-rendered)
  Páginas Jinja2 que usam os mesmos serviços da API: vitrine, login, cadastro, mapa de
  assentos acessível, reserva pelo formulário, painéis e cabeçalhos de segurança.
  Sustenta ADR-0017, RNF09, RNF18, RNF19, RNF31 e RF25.

  Contexto:
    Dado que o sistema está em execução

  # Equivale a: tests/test_web.py::TestProgramacaoPublica::test_pagina_declara_idioma_e_viewport_para_celular
  Cenário: RNF18 - a página declara idioma e viewport para celular
    Quando o visitante abre a página "/programacao"
    Então a página tem o idioma "pt-BR" e viewport para celular
    Então a página contém "Programação"

  # Equivale a: tests/test_web.py::TestProgramacaoPublica::test_mostra_filmes_publicados
  Cenário: RF03 - a vitrine mostra os filmes publicados
    Dado que existe um filme "Filme em Cartaz"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "a" do filme "Filme em Cartaz" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Dado que o dia "2026-11-02" está publicado
    Quando o visitante abre a página "/programacao"
    Então a página contém "Filme em Cartaz"

  # Equivale a: tests/test_web.py::TestProgramacaoPublica::test_escapa_html_de_titulos
  Cenário: RNF31 - títulos com HTML são escapados na página
    Dado que existe um filme "<b>Negrito</b>"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "a" do filme "<b>Negrito</b>" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Dado que o dia "2026-11-02" está publicado
    Quando o visitante abre a página "/programacao"
    Então a página contém "&lt;b&gt;Negrito&lt;/b&gt;"
    Então a página não contém "<b>Negrito</b>"

  # Equivale a: tests/test_web.py::TestProgramacaoPublica::test_raiz_redireciona_para_programacao
  Cenário: ADR-0017 - a raiz redireciona para a programação
    Quando o visitante abre a página "/"
    Então a resposta redireciona para "/programacao"

  # Equivale a: tests/test_web.py::TestLoginPorFormulario::test_formulario_de_login_tem_token_csrf
  Cenário: RNF31 - o formulário de login traz o token CSRF
    Quando o visitante abre a página "/entrar"
    Então a página contém o campo "csrf_token"

  # Equivale a: tests/test_web.py::TestLoginPorFormulario::test_login_com_formulario_redireciona_para_a_area_do_perfil
  Cenário: RF01 - login pelo formulário redireciona para a área do perfil
    Quando o visitante abre a página "/entrar"
    Quando o visitante envia o formulário "/entrar" com os campos:
      | campo | valor                 |
      | email | admin@cinesenac.test  |
      | senha | senha-admin-forte-123 |
    Então a resposta redireciona para "/admin"

  # Equivale a: tests/test_web.py::TestLoginPorFormulario::test_login_com_senha_errada_mostra_mensagem_generica
  Cenário: RF01 - senha errada mostra mensagem genérica no formulário
    Quando o visitante abre a página "/entrar"
    Quando o visitante envia o formulário "/entrar" com os campos:
      | campo | valor                 |
      | email | x@exemplo.com         |
      | senha | errada-123456         |
    Então a resposta tem status 401
    Então a página contém "E-mail ou senha inválidos"

  # Equivale a: tests/test_web.py::TestControleDeAcessoDasPaginas::test_area_restrita_sem_login_redireciona_para_entrar
  Cenário: RF02 - área restrita sem login redireciona para a entrada
    Quando o visitante abre a página "/gestor"
    Então a resposta redireciona para "/entrar"

  # Equivale a: tests/test_web.py::TestControleDeAcessoDasPaginas::test_area_de_outro_perfil_retorna_403_em_html
  Cenário: RF02 - área de outro perfil retorna 403 em página de erro
    Dado que o cliente está autenticado
    Quando o cliente abre a página "/gestor"
    Então a resposta tem status 403
    Então a página contém "Acesso negado"

  # Equivale a: tests/test_web.py::TestMapaEReservaPelaPagina::test_mapa_tem_assentos_com_rotulo_acessivel
  Cenário: RNF19 - o mapa de assentos tem rótulo acessível em cada assento
    Dado que o cliente está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 3 assentos
    Dado que existe uma sessão "s" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Dado que o dia "2026-11-02" está publicado
    Quando o cliente abre a página "/sessoes/{id:sessao:s}"
    Então a página contém o rótulo "Fila A, assento 1, livre"
    Então a página contém o rótulo "Fila A, assento 3, livre"

  # Equivale a: tests/test_web.py::TestMapaEReservaPelaPagina::test_mapa_exige_login_de_cliente
  Cenário: RF20 - o mapa pela página exige login de cliente
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 3 assentos
    Dado que existe uma sessão "s" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Dado que o dia "2026-11-02" está publicado
    Quando o visitante abre a página "/sessoes/{id:sessao:s}"
    Então a resposta redireciona para "/entrar"

  # Equivale a: tests/test_web.py::TestMapaEReservaPelaPagina::test_reserva_pelo_formulario_mostra_confirmacao_com_valor
  Cenário: RF25 - a reserva pelo formulário mostra a confirmação com o valor
    Dado que o cliente está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 3 assentos
    Dado que existe uma sessão "s" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Dado que o dia "2026-11-02" está publicado
    Quando o cliente abre a página "/sessoes/{id:sessao:s}"
    Quando o cliente envia o formulário "/sessoes/{id:sessao:s}/reservas" com os campos:
      | campo    | valor     |
      | assentos | A1,A2     |
    Então a página contém "Reserva confirmada"
    Então a página contém "R$ 50,00"
    Então a página contém "A1"
    Então a página contém "A2"

  # Equivale a: tests/test_web.py::TestMapaEReservaPelaPagina::test_minhas_reservas_mostra_a_reserva
  Cenário: RF26 - minhas reservas na página mostra a reserva feita
    Dado que o cliente está autenticado
    Dado que existe um filme "Minha Sessão"
    Dado que existe uma sala "Sala 1" com 3 assentos
    Dado que existe uma sessão "s" do filme "Minha Sessão" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Dado que o dia "2026-11-02" está publicado
    Quando o cliente abre a página "/sessoes/{id:sessao:s}"
    Quando o cliente envia o formulário "/sessoes/{id:sessao:s}/reservas" com os campos:
      | campo    | valor |
      | assentos | A3    |
    Quando o cliente abre a página "/minhas-reservas"
    Então a página contém "Minha Sessão"
    Então a página contém "A3"

  # Equivale a: tests/test_web.py::TestPaineisDoGestorEAdmin::test_painel_do_gestor_mostra_indicador_de_cota
  Cenário: RF18 - o painel do gestor mostra o indicador da cota nacional
    Dado que o gestor está autenticado
    Quando o gestor abre a página "/gestor"
    Então a página contém "Cota de filme nacional"

  # Equivale a: tests/test_web.py::TestPaineisDoGestorEAdmin::test_painel_admin_mostra_dashboard
  Cenário: RF29 - o painel do admin mostra o dashboard
    Dado que o admin está autenticado
    Quando o admin abre a página "/admin"
    Então a página contém "Usuários"
    Então a página contém "Reservas"

  # Equivale a: tests/test_web.py::TestCabecalhosDeSeguranca::test_paginas_enviam_csp_e_protecoes
  Cenário: RNF31 - as páginas enviam política de conteúdo e proteções
    Quando o visitante abre a página "/programacao"
    Então o cabeçalho "Content-Security-Policy" contém "default-src 'self'"
    Então o cabeçalho "X-Content-Type-Options" é "nosniff"
    Então o cabeçalho "X-Frame-Options" é "DENY"

  # Equivale a: tests/test_web.py::TestCabecalhosDeSeguranca::test_cookie_de_sessao_nao_vaza_para_script
  Cenário: RNF28 - o cookie de sessão é HttpOnly também pelo formulário
    Quando o visitante abre a página "/entrar"
    Quando o visitante envia o formulário "/entrar" com os campos:
      | campo | valor                 |
      | email | admin@cinesenac.test  |
      | senha | senha-admin-forte-123 |
    Então o cabeçalho "set-cookie" contém "HttpOnly"

  # Equivale a: tests/test_web.py::TestCadastroPelaPagina::test_cadastro_pelo_formulario_cria_conta_e_redireciona_para_minhas_reservas
  Cenário: RF04 - o cadastro pelo formulário cria a conta e entra
    Quando o visitante abre a página "/cadastro"
    Quando o visitante envia o formulário "/cadastro" com os campos:
      | campo       | valor                  |
      | nome        | Carla                  |
      | email       | carla@exemplo.com      |
      | idade       | 28                     |
      | senha       | senha-carla-forte-123  |
      | logradouro  | Av. Central            |
      | numero      | 50                     |
      | complemento |                        |
      | bairro      | Sé                     |
      | cidade      | São Paulo              |
      | estado      | SP                     |
      | cep         | 01001-000              |
    Então a resposta redireciona para "/minhas-reservas"
    Quando o visitante abre a página "/minha-conta"
    Então a página contém "Carla"

  # Equivale a: tests/test_web.py::TestCadastroPelaPagina::test_cadastro_com_email_duplicado_mostra_erro
  Cenário: RF05 - cadastro pelo formulário com e-mail duplicado mostra erro
    Dado que existe um cliente com e-mail "ana@exemplo.com"
    Quando o visitante abre a página "/cadastro"
    Quando o visitante envia o formulário "/cadastro" com os campos:
      | campo       | valor                  |
      | nome        | Carla                  |
      | email       | ana@exemplo.com        |
      | idade       | 28                     |
      | senha       | senha-carla-forte-123  |
      | logradouro  | Av. Central            |
      | numero      | 50                     |
      | complemento |                        |
      | bairro      | Sé                     |
      | cidade      | São Paulo              |
      | estado      | SP                     |
      | cep         | 01001-000              |
    Então a resposta tem status 409
    Então a página contém "Este e-mail já está cadastrado"

  # Equivale a: tests/test_web.py::TestCadastroPelaPagina::test_cadastro_com_dados_invalidos_mostra_erro_sem_criar_conta
  Cenário: RF04 - cadastro pelo formulário com dados inválidos mostra erro sem criar conta
    Quando o visitante abre a página "/cadastro"
    Quando o visitante envia o formulário "/cadastro" com os campos:
      | campo       | valor                  |
      | nome        | Carla                  |
      | email       | carla@exemplo.com      |
      | idade       | 0                      |
      | senha       | senha-carla-forte-123  |
      | logradouro  | Av. Central            |
      | numero      | 50                     |
      | complemento |                        |
      | bairro      | Sé                     |
      | cidade      | São Paulo              |
      | estado      | SP                     |
      | cep         | 01001-000              |
    Então a resposta tem status 422
    Então a página contém "Revise o formulário"

  # Equivale a: tests/test_web.py::TestMinhaContaSemCadastro::test_admin_sem_cadastro_de_cliente_recebe_403_na_minha_conta
  Cenário: RF07 - o admin sem cadastro de cliente recebe 403 em minha conta
    Dado que o admin está autenticado
    Quando o admin abre a página "/minha-conta"
    Então a resposta tem status 403
