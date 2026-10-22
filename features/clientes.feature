# language: pt
Funcionalidade: Cadastro do cliente
  O cliente cria a própria conta, edita e consulta seus dados.
  Sustenta RF04 a RF07, RNF03, RNF29 e RNF32.

  Contexto:
    Dado que o sistema está em execução

  # Equivale a: tests/test_clientes.py::TestRF04Cadastro::test_cadastro_cria_conta_de_cliente
  Cenário: RF04 - o visitante cria a conta de cliente com nome, e-mail, idade e endereço
    Quando o visitante envia POST "/v1/clientes" com os dados:
      """
      {"email": "bia@exemplo.com", "senha": "senha-cliente-forte-123", "nome": "Bia", "idade": 25,
       "endereco": {"logradouro": "Rua das Flores", "numero": "100", "complemento": null,
                    "bairro": "Centro", "cidade": "São Paulo", "estado": "SP", "cep": "01000-000"}}
      """
    Então a resposta tem status 201
    Então o campo "nome" é "Bia"
    Então o campo "email" é "bia@exemplo.com"
    Então o campo "idade" é 25
    Então o campo "endereco.cidade" é "São Paulo"
    Então o campo "senha" não existe

  # Equivale a: tests/test_clientes.py::TestRF04Cadastro::test_idade_invalida_retorna_422_com_campo
  Cenário: RF04 - idade inválida é recusada indicando o campo
    Quando o visitante envia POST "/v1/clientes" com os dados:
      """
      {"email": "x@exemplo.com", "senha": "senha-forte-123456", "nome": "X", "idade": -1,
       "endereco": {"logradouro": "R", "numero": "1", "bairro": "B", "cidade": "C",
                    "estado": "SP", "cep": "01000-000"}}
      """
    Então a resposta tem status 422
    Então o código de erro é "validacao"
    Então o campo "campos" contém "idade"

  # Equivale a: tests/test_clientes.py::TestRF04Cadastro::test_endereco_incompleto_retorna_422
  Cenário: RF04 - endereço incompleto é recusado indicando o campo
    Quando o visitante envia POST "/v1/clientes" com os dados:
      """
      {"email": "x@exemplo.com", "senha": "senha-forte-123456", "nome": "X", "idade": 20,
       "endereco": {"logradouro": "R", "numero": "1", "bairro": "B", "estado": "SP", "cep": "01000-000"}}
      """
    Então a resposta tem status 422
    Então o campo "campos" contém "cidade"

  # Equivale a: tests/test_clientes.py::TestRF05EmailUnico::test_email_duplicado_retorna_409
  Cenário: RF05 - e-mail já cadastrado é recusado
    Dado que existe um cliente com e-mail "dup@exemplo.com"
    Quando o visitante envia POST "/v1/clientes" com os dados:
      """
      {"email": "dup@exemplo.com", "senha": "senha-forte-123456", "nome": "Outra", "idade": 40,
       "endereco": {"logradouro": "R", "numero": "1", "bairro": "B", "cidade": "C",
                    "estado": "SP", "cep": "01000-000"}}
      """
    Então a resposta tem status 409
    Então o código de erro é "email_duplicado"

  # Equivale a: tests/test_clientes.py::TestRF05EmailUnico::test_cadastros_simultaneos_com_mesmo_email_criam_uma_conta
  Cenário: RNF03 - cadastros simultâneos com o mesmo e-mail criam uma única conta
    Quando 12 cadastros com o e-mail "corrida@exemplo.com" são feitos ao mesmo tempo
    Então o resultado da disputa tem exatamente 1 sucesso e 11 "email_duplicado"

  # Equivale a: tests/test_clientes.py::TestRF06Edicao::test_cliente_edita_o_proprio_cadastro
  Cenário: RF06 - o cliente edita o próprio cadastro
    Dado que o cliente está autenticado
    Quando o cliente envia PATCH "/v1/clientes/{cliente_id}" com os dados:
      """
      {"idade": 31}
      """
    Então a resposta tem status 200
    Então o campo "idade" é 31

  # Equivale a: tests/test_clientes.py::TestRF06Edicao::test_edicao_para_email_ja_usado_retorna_409
  Cenário: RF06 - trocar para um e-mail já usado é recusado
    Dado que o cliente está autenticado
    Dado que existe um cliente com e-mail "ocupado@exemplo.com"
    Quando o cliente envia PATCH "/v1/clientes/{cliente_id}" com os dados:
      """
      {"email": "ocupado@exemplo.com"}
      """
    Então a resposta tem status 409
    Então o código de erro é "email_duplicado"

  # Equivale a: tests/test_clientes.py::TestRF07Visualizacao::test_cliente_visualiza_o_proprio_cadastro
  Cenário: RF07 - o cliente visualiza o próprio cadastro
    Dado que o cliente está autenticado
    Quando o cliente envia GET "/v1/clientes/{cliente_id}"
    Então a resposta tem status 200
    Então o campo "email" é "ana@exemplo.com"

  # Equivale a: tests/test_clientes.py::TestRF07Visualizacao::test_cliente_nao_ve_cadastro_de_outro
  Cenário: RNF32 - o cliente não vê o cadastro de outro cliente
    Dado que o cliente está autenticado
    Dado que existe um cliente com e-mail "outro@exemplo.com"
    Quando o cliente envia GET "/v1/clientes/{id:cliente:outro@exemplo.com}"
    Então a resposta tem status 403
    Então o código de erro é "sem_permissao"

  # Equivale a: tests/test_clientes.py::TestRF07Visualizacao::test_cliente_nao_edita_cadastro_de_outro
  Cenário: RNF29 - o cliente não edita o cadastro de outro cliente
    Dado que o cliente está autenticado
    Dado que existe um cliente com e-mail "outro2@exemplo.com"
    Quando o cliente envia PATCH "/v1/clientes/{id:cliente:outro2@exemplo.com}" com os dados:
      """
      {"idade": 99}
      """
    Então a resposta tem status 403

  # Equivale a: tests/test_clientes.py::TestRF07Visualizacao::test_admin_visualiza_cadastro_de_cliente
  Cenário: RNF32 - o admin visualiza o cadastro de um cliente
    Dado que o cliente está autenticado
    Dado que o admin está autenticado
    Quando o admin envia GET "/v1/clientes/{cliente_id}"
    Então a resposta tem status 200
