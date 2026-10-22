# language: pt
Funcionalidade: Catálogo de filmes e salas
  O gestor cadastra, edita, exclui e lista filmes e salas.
  Sustenta RF08 a RF13, RNF13 e RNF31.

  Contexto:
    Dado que o sistema está em execução

  # Equivale a: tests/test_catalogo.py::TestRF08CadastroFilme::test_gestor_cadastra_filme
  Cenário: RF08 - o gestor cadastra um filme
    Dado que o gestor está autenticado
    Quando o gestor envia POST "/v1/filmes" com os dados:
      """
      {"titulo": "O Sertão", "duracao_minutos": 120, "genero": "Drama", "sinopse": "Uma história.",
       "cartaz_url": "https://img.exemplo.com/cartaz.jpg", "faixa_etaria": "LIVRE",
       "elenco": "Elenco", "nacionalidade": "NACIONAL"}
      """
    Então a resposta tem status 201
    Então o campo "titulo" é "O Sertão"
    Então o campo "nacionalidade" é "NACIONAL"
    Então o campo "faixa_etaria" é "LIVRE"

  # Equivale a: tests/test_catalogo.py::TestRF08CadastroFilme::test_cliente_nao_cadastra_filme
  Cenário: RF08 - o cliente não cadastra filme
    Dado que o cliente está autenticado
    Quando o cliente envia POST "/v1/filmes" com os dados:
      """
      {"titulo": "X"}
      """
    Então a resposta tem status 403

  # Equivale a: tests/test_catalogo.py::TestRF08CadastroFilme::test_cartaz_com_esquema_javascript_e_recusado
  Cenário: RNF31 - cartaz com esquema javascript é recusado
    Dado que o gestor está autenticado
    Quando o gestor envia POST "/v1/filmes" com os dados:
      """
      {"titulo": "Perigoso", "duracao_minutos": 90, "genero": "Terror", "sinopse": "x",
       "cartaz_url": "javascript:alert(1)", "faixa_etaria": "LIVRE", "elenco": "x",
       "nacionalidade": "NACIONAL"}
      """
    Então a resposta tem status 422
    Então o campo "campos" contém "cartaz_url"

  # Equivale a: tests/test_catalogo.py::TestRF08CadastroFilme::test_cartaz_https_e_aceito
  Cenário: RF08 - cartaz com endereço https é aceito
    Dado que o gestor está autenticado
    Quando o gestor envia POST "/v1/filmes" com os dados:
      """
      {"titulo": "Com Cartaz", "duracao_minutos": 90, "genero": "Drama", "sinopse": "x",
       "cartaz_url": "https://img.exemplo.com/a.png", "faixa_etaria": "LIVRE", "elenco": "x",
       "nacionalidade": "NACIONAL"}
      """
    Então a resposta tem status 201
    Então o campo "cartaz_url" é "https://img.exemplo.com/a.png"

  # Equivale a: tests/test_catalogo.py::TestRF08CadastroFilme::test_faixa_etaria_fora_do_dominio_retorna_422
  Cenário: RF08 - faixa etária fora do domínio é recusada
    Dado que o gestor está autenticado
    Quando o gestor envia POST "/v1/filmes" com os dados:
      """
      {"titulo": "X", "duracao_minutos": 90, "genero": "Drama", "sinopse": "x",
       "cartaz_url": "https://img.exemplo.com/a.png", "faixa_etaria": "CINQUENTA_ANOS",
       "elenco": "x", "nacionalidade": "NACIONAL"}
      """
    Então a resposta tem status 422
    Então o campo "campos" contém "faixa_etaria"

  # Equivale a: tests/test_catalogo.py::TestRF09EdicaoExclusaoFilme::test_gestor_edita_filme
  Cenário: RF09 - o gestor edita um filme
    Dado que o gestor está autenticado
    Dado que existe um filme "Original"
    Quando o gestor envia PATCH "/v1/filmes/{id:filme:Original}" com os dados:
      """
      {"titulo": "Novo Título"}
      """
    Então a resposta tem status 200
    Então o campo "titulo" é "Novo Título"

  # Equivale a: tests/test_catalogo.py::TestRF09EdicaoExclusaoFilme::test_gestor_exclui_filme_sem_sessoes
  Cenário: RF09 - o gestor exclui um filme sem sessões
    Dado que o gestor está autenticado
    Dado que existe um filme "Para Excluir"
    Quando o gestor envia DELETE "/v1/filmes/{id:filme:Para Excluir}"
    Então a resposta tem status 204
    Quando o gestor envia GET "/v1/filmes"
    Então o campo "itens[].titulo" não contém "Para Excluir"

  # Equivale a: tests/test_catalogo.py::TestRF09EdicaoExclusaoFilme::test_exclusao_de_filme_com_sessoes_e_recusada
  Cenário: RF09 - filme com sessões não é excluído
    Dado que o gestor está autenticado
    Dado que existe um filme "Com Sessão"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "s" do filme "Com Sessão" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Quando o gestor envia DELETE "/v1/filmes/{id:filme:Com Sessão}"
    Então a resposta tem status 409
    Então o código de erro é "filme_com_sessoes"

  # Equivale a: tests/test_catalogo.py::TestRF10ListagemFilmes::test_busca_filtra_por_titulo
  Cenário: RF10 - a busca filtra filmes pelo título
    Dado que o gestor está autenticado
    Dado que existe um filme "Domingo Infinito"
    Dado que existe um filme "Madrugada"
    Quando o gestor envia GET "/v1/filmes?q=Dom"
    Então o campo "itens[].titulo" tem os valores "Domingo Infinito"

  # Equivale a: tests/test_catalogo.py::TestRF10ListagemFilmes::test_listagem_sem_busca_traz_todos
  Cenário: RF10 - a listagem sem busca traz todos os filmes
    Dado que o gestor está autenticado
    Dado que existe um filme "A"
    Dado que existe um filme "B"
    Quando o gestor envia GET "/v1/filmes"
    Então o campo "itens" tem 2 itens

  # Equivale a: tests/test_catalogo.py::TestRF11CadastroSala::test_cadastro_gera_assentos_de_A1_ate_An
  Cenário: RF11 - o cadastro da sala gera os assentos de A1 até An
    Dado que o gestor está autenticado
    Dado que existe uma sala "Sala" com 3 assentos
    Quando o gestor envia GET "/v1/salas/{id:sala:Sala}"
    Então o campo "assentos[].codigo" tem os valores "A1, A2, A3"

  # Equivale a: tests/test_catalogo.py::TestRF11CadastroSala::test_quantidade_zero_retorna_422
  Cenário: RF11 - sala sem assentos é recusada
    Dado que o gestor está autenticado
    Quando o gestor envia POST "/v1/salas" com os dados:
      """
      {"nome": "X", "qtd_assentos": 0, "hora_abertura": "14:00", "hora_fechamento": "23:00",
       "especificacao_tecnica": "2D"}
      """
    Então a resposta tem status 422
    Então o campo "campos" contém "qtd_assentos"

  # Equivale a: tests/test_catalogo.py::TestRF11CadastroSala::test_fechamento_antes_da_abertura_retorna_422
  Cenário: RF11 - fechamento antes da abertura é recusado
    Dado que o gestor está autenticado
    Quando o gestor envia POST "/v1/salas" com os dados:
      """
      {"nome": "X", "qtd_assentos": 5, "hora_abertura": "22:00", "hora_fechamento": "10:00",
       "especificacao_tecnica": "2D"}
      """
    Então a resposta tem status 422
    Então o campo "campos" contém "hora_fechamento"

  # Equivale a: tests/test_catalogo.py::TestRF12EdicaoExclusaoSala::test_aumentar_assentos_cria_os_novos
  Cenário: RF12 - aumentar a quantidade de assentos cria os novos
    Dado que o gestor está autenticado
    Dado que existe uma sala "Sala" com 2 assentos
    Quando o gestor envia PATCH "/v1/salas/{id:sala:Sala}" com os dados:
      """
      {"qtd_assentos": 4}
      """
    Então a resposta tem status 200
    Quando o gestor envia GET "/v1/salas/{id:sala:Sala}"
    Então o campo "assentos[].codigo" tem os valores "A1, A2, A3, A4"

  # Equivale a: tests/test_catalogo.py::TestRF12EdicaoExclusaoSala::test_reduzir_assentos_com_reserva_retorna_409
  Cenário: RF12 - reduzir assentos reservados é recusado
    Dado que o gestor está autenticado
    Dado que existe uma sala "Sala" com 3 assentos
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sessão "s" do filme "Filme Nacional" na sala "Sala" em "19:00" com 120 minutos e valor "25.00"
    Dado que o cliente reservou "A3" na sessão "s"
    Quando o gestor envia PATCH "/v1/salas/{id:sala:Sala}" com os dados:
      """
      {"qtd_assentos": 2}
      """
    Então a resposta tem status 409
    Então o código de erro é "assentos_reservados"

  # Equivale a: tests/test_catalogo.py::TestRF12EdicaoExclusaoSala::test_exclui_sala_sem_sessoes
  Cenário: RF12 - o gestor exclui uma sala sem sessões
    Dado que o gestor está autenticado
    Dado que existe uma sala "Vazia" com 5 assentos
    Quando o gestor envia DELETE "/v1/salas/{id:sala:Vazia}"
    Então a resposta tem status 204

  # Equivale a: tests/test_catalogo.py::TestRF12EdicaoExclusaoSala::test_exclusao_de_sala_com_sessoes_e_recusada
  Cenário: RF12 - sala com sessões não é excluída
    Dado que o gestor está autenticado
    Dado que existe uma sala "Com Sessao" com 5 assentos
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sessão "s" do filme "Filme Nacional" na sala "Com Sessao" em "19:00" com 120 minutos e valor "25.00"
    Quando o gestor envia DELETE "/v1/salas/{id:sala:Com Sessao}"
    Então a resposta tem status 409
    Então o código de erro é "sala_com_sessoes"

  # Equivale a: tests/test_catalogo.py::TestRF13ListagemSalas::test_busca_de_salas_por_nome
  Cenário: RF13 - a busca filtra salas pelo nome
    Dado que o gestor está autenticado
    Dado que existe uma sala "Sala IMAX" com 2 assentos
    Dado que existe uma sala "Sala Comum" com 2 assentos
    Quando o gestor envia GET "/v1/salas?q=IMAX"
    Então o campo "itens[].nome" tem os valores "Sala IMAX"
