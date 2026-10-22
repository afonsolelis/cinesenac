# language: pt
Funcionalidade: Mapa e reserva de assentos
  O cliente vê o mapa, reserva um ou mais assentos com idempotência, e não reserva
  assentos ocupados nem sessões que conflitam com outras já reservadas.
  Sustenta RF20 a RF26, RF30, RNF01, RNF02, RNF24 e RNF25.

  Contexto:
    Dado que o sistema está em execução
    Dado que existe um filme "Filme Nacional"
    Dado que existe uma sala "Sala 1" com 5 assentos
    Dado que existe uma sessão "s" do filme "Filme Nacional" na sala "Sala 1" em "19:00" com 120 minutos e valor "25.00"
    Dado que o dia "2026-11-02" está publicado

  # Equivale a: tests/test_reservas.py::TestRF20Mapa::test_mapa_mostra_assentos_livres_e_ocupados
  Cenário: RF20 - o mapa mostra assentos livres e ocupados
    Dado que o cliente está autenticado
    Dado que o outro cliente está autenticado
    Quando o cliente envia GET "/v1/sessoes/{id:sessao:s}/assentos"
    Então o campo "assentos[].codigo" tem os valores "A1, A2, A3, A4, A5"
    Quando o outro cliente reserva "A1" na sessão "s" com a chave "k1"
    Então a resposta tem status 201
    Quando o cliente envia GET "/v1/sessoes/{id:sessao:s}/assentos"
    Então o assento "A1" da sessão "s" está ocupado
    Então o assento "A2" da sessão "s" está livre

  # Equivale a: tests/test_reservas.py::TestRF20Mapa::test_mapa_exige_cliente_logado
  Cenário: RF20 - o mapa exige login de cliente
    Quando o visitante envia GET "/v1/sessoes/{id:sessao:s}/assentos"
    Então a resposta tem status 401

  # Equivale a: tests/test_reservas.py::TestRF20Mapa::test_mapa_nao_mostra_assento_recem_reservado_como_livre
  Cenário: RNF14 - o mapa não usa cache e mostra o assento recém-reservado como ocupado
    Dado que o cliente está autenticado
    Dado que o outro cliente está autenticado
    Quando o cliente envia GET "/v1/sessoes/{id:sessao:s}/assentos"
    Quando o outro cliente reserva "A2" na sessão "s" com a chave "k2"
    Então a resposta tem status 201
    Quando o cliente envia GET "/v1/sessoes/{id:sessao:s}/assentos"
    Então o assento "A2" da sessão "s" está ocupado

  # Equivale a: tests/test_reservas.py::TestRF21RF22Reserva::test_reserva_de_varios_assentos_grava_todos
  Cenário: RF21 e RF22 - a reserva de vários assentos grava todos e informa o valor
    Dado que o cliente está autenticado
    Quando o cliente reserva "A1, A2" na sessão "s" com a chave "chave-varios"
    Então a resposta tem status 201
    Então o campo "reservas[].assento" tem os valores "A1, A2"
    Então o campo "valor_total" é "50.00"

  # Equivale a: tests/test_reservas.py::TestRF21RF22Reserva::test_reenvio_com_mesma_chave_nao_duplica
  Cenário: RNF24 - o reenvio com a mesma chave não duplica a reserva
    Dado que o cliente está autenticado
    Quando o cliente reserva "A1, A2" na sessão "s" com a chave "chave-fixa-1"
    Então a resposta tem status 201
    Quando o cliente reserva "A1, A2" na sessão "s" com a chave "chave-fixa-1"
    Então a resposta tem status 201
    Então as duas respostas têm as mesmas reservas
    Quando o cliente envia GET "/v1/minhas-reservas"
    Então o campo "itens" tem 2 itens

  # Equivale a: tests/test_reservas.py::TestRF21RF22Reserva::test_mesma_chave_com_corpo_diferente_retorna_422
  Cenário: RNF24 - a mesma chave com outro pedido é recusada
    Dado que o cliente está autenticado
    Quando o cliente reserva "A1" na sessão "s" com a chave "chave-reutilizada"
    Então a resposta tem status 201
    Quando o cliente reserva "A2" na sessão "s" com a chave "chave-reutilizada"
    Então a resposta tem status 422
    Então o código de erro é "idempotencia_conflito"

  # Equivale a: tests/test_reservas.py::TestRF21RF22Reserva::test_cabecalho_idempotency_key_e_obrigatorio
  Cenário: RNF24 - a reserva sem chave de idempotência é recusada
    Dado que o cliente está autenticado
    Quando o cliente reserva "A1" na sessão "s" sem chave de idempotência
    Então a resposta tem status 422
    Então o código de erro é "cabecalho_obrigatorio"

  # Equivale a: tests/test_reservas.py::TestRF21RF22Reserva::test_lista_vazia_de_assentos_retorna_422
  Cenário: RF21 - a reserva sem assentos é recusada
    Dado que o cliente está autenticado
    Quando o cliente envia POST "/v1/reservas" com os dados:
      """
      {"sessao_id": "{id:sessao:s}", "assentos": []}
      """
    Então a resposta tem status 422
    Então o campo "campos" contém "assentos"

  # Equivale a: tests/test_reservas.py::TestRF21RF22Reserva::test_sessao_cancelada_nao_aceita_reserva
  Cenário: RF22 - sessão cancelada não aceita reserva
    Dado que o cliente está autenticado
    Dado que a sessão "s" foi cancelada
    Quando o cliente reserva "A1" na sessão "s" com a chave "k"
    Então a resposta tem status 409
    Então o código de erro é "sessao_cancelada"

  # Equivale a: tests/test_reservas.py::TestRF23AssentoOcupado::test_assento_ocupado_por_outro_cliente_retorna_409
  Cenário: RF23 - assento ocupado por outro cliente é recusado
    Dado que o cliente está autenticado
    Dado que o outro cliente está autenticado
    Quando o outro cliente reserva "A1" na sessão "s" com a chave "k-outro"
    Então a resposta tem status 201
    Quando o cliente reserva "A1" na sessão "s" com a chave "k-cli"
    Então a resposta tem status 409
    Então o código de erro é "assento_indisponivel"

  # Equivale a: tests/test_reservas.py::TestRF23AssentoOcupado::test_assento_inexistente_nao_grava_nada
  Cenário: RNF25 - assento inexistente não grava nenhum assento do pedido
    Dado que o cliente está autenticado
    Quando o cliente reserva "A1, Z9" na sessão "s" com a chave "k-z"
    Então a resposta tem status 422
    Então o código de erro é "assento_inexistente"
    Quando o cliente envia GET "/v1/sessoes/{id:sessao:s}/assentos"
    Então o assento "A1" da sessão "s" está livre

  # Equivale a: tests/test_reservas.py::TestRF24ConflitoDoCliente::test_reserva_em_sessao_que_conflita_com_outra_do_cliente_retorna_409
  Cenário: RF24 - reserva em sessão que conflita com outra do cliente é recusada
    Dado que o cliente está autenticado
    Dado que existe uma sala "Sala 2" com 3 assentos
    Dado que existe uma sessão "outra" do filme "Filme Nacional" na sala "Sala 2" em "20:00" com 60 minutos e valor "25.00"
    Dado que o cliente reservou "A1" na sessão "s"
    Quando o cliente reserva "A1" na sessão "outra" com a chave "k-x"
    Então a resposta tem status 409
    Então o código de erro é "conflito_horario_cliente"

  # Equivale a: tests/test_reservas.py::TestRF24ConflitoDoCliente::test_sessoes_nao_conflitantes_podem_ser_reservadas_pelo_mesmo_cliente
  Cenário: RF24 - o mesmo cliente reserva sessões que não conflitam
    Dado que o cliente está autenticado
    Dado que existe uma sala "Sala 2" com 3 assentos
    Dado que existe uma sessão "outra" do filme "Filme Nacional" na sala "Sala 2" em "21:00" com 60 minutos e valor "25.00"
    Dado que o cliente reservou "A1" na sessão "s"
    Quando o cliente reserva "A1" na sessão "outra" com a chave "k-y"
    Então a resposta tem status 201

  # Equivale a: tests/test_reservas.py::TestRF25Confirmacao::test_confirmacao_traz_sessao_assentos_e_valor
  Cenário: RF25 - a confirmação traz sessão, assentos e valor
    Dado que o cliente está autenticado
    Quando o cliente reserva "A3" na sessão "s" com a chave "k-c"
    Então a resposta tem status 201
    Então o campo "data_hora_inicio" é "2026-11-02T19:00:00"
    Então o campo "filme.titulo" é "Filme Nacional"
    Então o campo "valor_total" é "25.00"

  # Equivale a: tests/test_reservas.py::TestRF26MinhasReservas::test_lista_apenas_as_reservas_do_proprio_cliente
  Cenário: RF26 - o cliente lista apenas as próprias reservas
    Dado que o cliente está autenticado
    Dado que o outro cliente está autenticado
    Dado que o cliente reservou "A1" na sessão "s"
    Dado que o outro cliente reservou "A2" na sessão "s"
    Quando o cliente envia GET "/v1/minhas-reservas"
    Então o campo "itens[].assento" tem os valores "A1"

  # Equivale a: tests/test_reservas.py::TestRF26MinhasReservas::test_minhas_reservas_exige_login
  Cenário: RF26 - minhas reservas exige login
    Quando o visitante envia GET "/v1/minhas-reservas"
    Então a resposta tem status 401

  # Equivale a: tests/test_reservas.py::TestRF30CancelamentoPeloAdmin::test_admin_lista_e_cancela_reserva_liberando_o_assento
  Cenário: RF30 - o admin cancela uma reserva e libera o assento
    Dado que o cliente está autenticado
    Dado que o cliente reservou "A1" na sessão "s"
    Dado que o admin está autenticado
    Quando o admin cancela a reserva de "A1" do cliente
    Então a resposta tem status 204
    Quando o cliente envia GET "/v1/sessoes/{id:sessao:s}/assentos"
    Então o assento "A1" da sessão "s" está livre
    Então o administrador vê a ação "reserva.cancelar" na auditoria

  # Equivale a: tests/test_reservas.py::TestRF30CancelamentoPeloAdmin::test_gestor_nao_cancela_reserva
  Cenário: RF30 - o gestor não cancela reserva
    Dado que o cliente está autenticado
    Dado que o cliente reservou "A1" na sessão "s"
    Dado que o gestor está autenticado
    Quando o gestor cancela a reserva de "A1" do cliente
    Então a resposta tem status 403

  # Equivale a: tests/test_reservas.py::TestRNF01RNF02Concorrencia::test_somente_uma_reserva_por_assento_sob_concorrencia
  Cenário: RNF01 - somente uma reserva por assento sob concorrência
    Quando 10 clientes disputam o assento "A1" da sessão "s" ao mesmo tempo
    Então o resultado da disputa tem exatamente 1 sucesso e 9 "assento_indisponivel"

  # Equivale a: tests/test_reservas.py::TestRNF01RNF02Concorrencia::test_mesmo_cliente_nao_reserva_sessoes_sobrepostas_em_paralelo
  Cenário: RNF02 - o mesmo cliente não reserva sessões sobrepostas em paralelo
    Dado que existe uma sala "Sala A" com 3 assentos
    Dado que existe uma sala "Sala B" com 3 assentos
    Dado que existe uma sessão "a" do filme "Filme Nacional" na sala "Sala A" em "19:00" com 120 minutos e valor "25.00"
    Dado que existe uma sessão "b" do filme "Filme Nacional" na sala "Sala B" em "20:00" com 120 minutos e valor "25.00"
    Quando um cliente reserva "A1" nas sessões "a" e "b" ao mesmo tempo
    Então o resultado da disputa tem exatamente 1 sucesso e 1 "conflito_horario_cliente"
