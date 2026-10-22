# language: pt
Funcionalidade: Programação de sessões
  O gestor cadastra sessões, evita sobreposição na sala, acompanha a cota nacional e
  publica o dia. O público vê apenas dias publicados.
  Sustenta RF03, RF14 a RF19, RF17, RN04, RNF05 e RNF14.

  Contexto:
    Dado que o sistema está em execução

  # Equivale a: tests/test_programacao.py::TestRF14CadastroSessao::test_cadastra_sessao_sem_avisos_quando_cota_atendida
  Cenário: RF14 - sessão cadastrada sem avisos quando a cota nacional está atendida
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Quando o gestor envia POST "/v1/sessoes" com os dados:
      """
      {"filme_id": "{id:filme:Filme Nacional}", "sala_id": "{id:sala:Sala 1}",
       "data_hora_inicio": "2026-11-02T19:00:00", "duracao_minutos": 120, "valor_ingresso": "25.00"}
      """
    Então a resposta tem status 201
    Então o campo "avisos" está vazio
    Então o campo "valor_ingresso" é "25.00"

  # Equivale a: tests/test_programacao.py::TestRF14CadastroSessao::test_referencia_inexistente_retorna_404
  Cenário: RF14 - sessão com filme inexistente é recusada
    Dado que o gestor está autenticado
    Dado que existe uma sala "Sala 1" com 10 assentos
    Quando o gestor envia POST "/v1/sessoes" com os dados:
      """
      {"filme_id": 9999, "sala_id": "{id:sala:Sala 1}",
       "data_hora_inicio": "2026-11-02T19:00:00", "duracao_minutos": 120, "valor_ingresso": "25.00"}
      """
    Então a resposta tem status 404
    Então o código de erro é "nao_encontrado"

  # Equivale a: tests/test_programacao.py::TestRF14CadastroSessao::test_dia_sem_filme_nacional_gera_aviso
  Cenário: RN04 - sessão em dia sem filme nacional gera aviso de cota pendente
    Dado que o gestor está autenticado
    Dado que existe um filme internacional "Filme Internacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Quando o gestor envia POST "/v1/sessoes" com os dados:
      """
      {"filme_id": "{id:filme:Filme Internacional}", "sala_id": "{id:sala:Sala 1}",
       "data_hora_inicio": "2026-11-02T19:00:00", "duracao_minutos": 120, "valor_ingresso": "25.00"}
      """
    Então a resposta tem status 201
    Então o campo "avisos" contém "cota_nacional_pendente"

  # Equivale a: tests/test_programacao.py::TestRF15Sobreposicao::test_sobreposicao_na_mesma_sala_retorna_409
  Cenário: RF15 - sessão sobreposta na mesma sala é recusada
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "a" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Quando o gestor envia POST "/v1/sessoes" com os dados:
      """
      {"filme_id": "{id:filme:Filme Nacional}", "sala_id": "{id:sala:Sala 1}",
       "data_hora_inicio": "2026-11-02T20:00:00", "duracao_minutos": 60, "valor_ingresso": "25.00"}
      """
    Então a resposta tem status 409
    Então o código de erro é "conflito_horario_sala"

  # Equivale a: tests/test_programacao.py::TestRF15Sobreposicao::test_mesmo_horario_em_salas_diferentes_nao_conflita
  Cenário: RF15 - o mesmo horário em salas diferentes não conflita
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sala "Sala 2" com 10 assentos
    Dado que existe uma sessão "a" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Quando o gestor envia POST "/v1/sessoes" com os dados:
      """
      {"filme_id": "{id:filme:Filme Nacional}", "sala_id": "{id:sala:Sala 2}",
       "data_hora_inicio": "2026-11-02T19:00:00", "duracao_minutos": 120, "valor_ingresso": "25.00"}
      """
    Então a resposta tem status 201

  # Equivale a: tests/test_programacao.py::TestRF15Sobreposicao::test_sessao_adjacente_na_mesma_sala_nao_conflita
  Cenário: RF15 - sessão adjacente na mesma sala não conflita
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "a" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Quando o gestor envia POST "/v1/sessoes" com os dados:
      """
      {"filme_id": "{id:filme:Filme Nacional}", "sala_id": "{id:sala:Sala 1}",
       "data_hora_inicio": "2026-11-02T21:00:00", "duracao_minutos": 60, "valor_ingresso": "25.00"}
      """
    Então a resposta tem status 201

  # Equivale a: tests/test_programacao.py::TestRF16EdicaoCancelamento::test_altera_horario_livre
  Cenário: RF16 - o gestor altera o horário para um intervalo livre
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "s" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Quando o gestor envia PATCH "/v1/sessoes/{id:sessao:s}" com os dados:
      """
      {"data_hora_inicio": "2026-11-02T22:00:00"}
      """
    Então a resposta tem status 200
    Então o campo "data_hora_inicio" é "2026-11-02T22:00:00"

  # Equivale a: tests/test_programacao.py::TestRF16EdicaoCancelamento::test_altera_horario_que_conflita_retorna_409
  Cenário: RF16 - alterar horário para um conflito é recusado
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "a" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Dado que existe uma sessão "b" do filme "Filme Nacional" na sala "Sala 1" em "22:00" com 60 minutos e valor "25.00"
    Quando o gestor envia PATCH "/v1/sessoes/{id:sessao:b}" com os dados:
      """
      {"data_hora_inicio": "2026-11-02T20:00:00"}
      """
    Então a resposta tem status 409
    Então o código de erro é "conflito_horario_sala"

  # Equivale a: tests/test_programacao.py::TestRF16EdicaoCancelamento::test_cancela_sessao_sem_reservas
  Cenário: RF16 - o gestor cancela uma sessão sem reservas
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "s" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Quando o gestor envia POST "/v1/sessoes/{id:sessao:s}/cancelamento"
    Então a resposta tem status 200
    Então o campo "cancelada" é true

  # Equivale a: tests/test_programacao.py::TestRF16EdicaoCancelamento::test_cancelamento_com_reservas_retorna_409
  Cenário: RF16 - sessão com reservas não pode ser cancelada
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "s" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Dado que o dia "2026-11-02" está publicado
    Dado que o cliente reservou "A1" na sessão "s"
    Quando o gestor envia POST "/v1/sessoes/{id:sessao:s}/cancelamento"
    Então a resposta tem status 409
    Então o código de erro é "sessao_com_reservas"

  # Equivale a: tests/test_programacao.py::TestRF16EdicaoCancelamento::test_cancelamento_gera_registro_de_auditoria
  Cenário: RNF33 - o cancelamento de sessão fica registrado na auditoria
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "s" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Dado que o admin está autenticado
    Quando o gestor envia POST "/v1/sessoes/{id:sessao:s}/cancelamento"
    Então o administrador vê a ação "sessao.cancelar" na auditoria

  # Equivale a: tests/test_programacao.py::TestRF18IndicadorCota::test_indicador_fica_pendente_sem_nacional_e_atendido_com_nacional
  Cenário: RF18 - o indicador da cota nacional muda quando entra um filme nacional
    Dado que o gestor está autenticado
    Dado que existe um filme internacional "Filme Internacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "a" do filme "Filme Internacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Quando o gestor envia GET "/v1/programacao/2026-11-02/cota-nacional"
    Então o campo "atendida" é false
    Então o campo "sessoes_nacionais" é 0
    Dado que existe um filme "Nacional"
    Dado que existe uma sessão "b" do filme "Nacional" na sala "Sala 1" em "21:00" com 60 minutos e valor "25.00"
    Quando o gestor envia GET "/v1/programacao/2026-11-02/cota-nacional"
    Então o campo "atendida" é true
    Então o campo "sessoes_nacionais" é 1

  # Equivale a: tests/test_programacao.py::TestRF19BloqueioPublicacao::test_publicacao_bloqueada_sem_cota_nacional
  Cenário: RF19 - a publicação é bloqueada sem filme nacional no dia
    Dado que o gestor está autenticado
    Dado que existe um filme internacional "Filme Internacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "a" do filme "Filme Internacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Quando o gestor envia POST "/v1/programacao/2026-11-02/publicacao"
    Então a resposta tem status 422
    Então o código de erro é "cota_nacional_nao_atendida"

  # Equivale a: tests/test_programacao.py::TestRF19BloqueioPublicacao::test_publicacao_com_cota_atendida
  Cenário: RF19 - a publicação é concluída com a cota atendida
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "a" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Quando o gestor envia POST "/v1/programacao/2026-11-02/publicacao"
    Então a resposta tem status 200
    Então o campo "publicado" é true

  # Equivale a: tests/test_programacao.py::TestRF03RF17ProgramacaoPublica::test_visitante_so_ve_dias_publicados
  Cenário: RF03 - o visitante vê apenas sessões de dias publicados
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "a" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Quando o visitante envia GET "/v1/programacao"
    Então o campo "itens" está vazio
    Dado que o dia "2026-11-02" está publicado
    Quando o visitante envia GET "/v1/programacao"
    Então o campo "itens" tem 1 itens
    Então o campo "itens[].filme.titulo" tem os valores "Filme Nacional"

  # Equivale a: tests/test_programacao.py::TestRF03RF17ProgramacaoPublica::test_sessoes_canceladas_nao_aparecem
  Cenário: RF03 - sessões canceladas não aparecem na vitrine
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "a" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Dado que o dia "2026-11-02" está publicado
    Dado que a sessão "a" foi cancelada
    Quando o visitante envia GET "/v1/programacao"
    Então o campo "itens" está vazio

  # Equivale a: tests/test_programacao.py::TestRF03RF17ProgramacaoPublica::test_filtra_por_sala
  Cenário: RF17 - a programação filtra por sala
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sala "Sala 2" com 10 assentos
    Dado que existe uma sessão "a" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Dado que existe uma sessão "b" do filme "Filme Nacional" na sala "Sala 2" em "21:00" com 60 minutos e valor "25.00"
    Dado que o dia "2026-11-02" está publicado
    Quando o visitante envia GET "/v1/programacao?sala_id={id:sala:Sala 2}"
    Então o campo "itens[].sala.nome" tem os valores "Sala 2"

  # Equivale a: tests/test_programacao.py::TestRF03RF17ProgramacaoPublica::test_filtra_por_periodo
  Cenário: RF17 - a programação filtra por período
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "a" do filme "Filme Nacional" na sala "Sala 1" em "2026-11-02T19:00:00" com 120 minutos e valor "25.00"
    Dado que existe uma sessão "b" do filme "Filme Nacional" na sala "Sala 1" em "2026-11-03T19:00:00" com 120 minutos e valor "25.00"
    Dado que o dia "2026-11-02" está publicado
    Dado que o dia "2026-11-03" está publicado
    Quando o visitante envia GET "/v1/programacao?inicio=2026-11-03&fim=2026-11-03"
    Então o campo "itens" tem 1 itens

  # Equivale a: tests/test_programacao.py::TestRF03RF17ProgramacaoPublica::test_resposta_publica_usa_cache_dentro_do_ttl
  Cenário: RNF14 - a segunda leitura da programação pública vem do cache
    Dado que a programação pública tem cache de 30 segundos
    Dado que o gestor está autenticado
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 10 assentos
    Dado que existe uma sessão "a" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Dado que o dia "2026-11-02" está publicado
    Quando o visitante envia GET "/v1/programacao"
    Então o cabeçalho "X-Cache" é "MISS"
    Quando o visitante envia GET "/v1/programacao"
    Então o cabeçalho "X-Cache" é "HIT"
