# language: pt
Funcionalidade: Infraestrutura da aplicação
  Configuração, cache, limitação de tentativas, admissão, hash de senha, endpoints
  técnicos, cabeçalhos de segurança e comandos de operação.

  Contexto:
    Dado que o sistema está em execução

  # Equivale a: tests/test_infra.py::TestConfiguracao::test_le_variaveis_com_prefixo_cinesenac
  Cenário: RNF40 - a configuração é lida das variáveis com prefixo CINESENAC
    Dado que a variável "CINESENAC_SECRET_KEY" vale "chave-de-teste-com-mais-de-trinta-caracteres"
    Dado que a variável "CINESENAC_DATABASE_URL" vale "sqlite:///./outro.db"
    Dado que a variável "CINESENAC_CACHE_TTL_SEGUNDOS" vale "45"
    Dado que a variável "CINESENAC_HTTPS_ONLY" vale "true"
    Quando eu carrego a configuração do ambiente
    Então a configuração tem secret_key igual a "chave-de-teste-com-mais-de-trinta-caracteres"
    Então a configuração tem database_url igual a "sqlite:///./outro.db"
    Então a configuração tem cache_ttl_seconds igual a 45
    Então a configuração tem https_only igual a true

  # Equivale a: tests/test_infra.py::TestConfiguracao::test_valores_padrao_seguros
  Cenário: RNF28 - sem variáveis opcionais valem os padrões seguros
    Dado que a variável "CINESENAC_SECRET_KEY" vale "chave-de-teste-com-mais-de-trinta-caracteres"
    Dado que a variável "CINESENAC_HTTPS_ONLY" não está definida
    Dado que a variável "CINESENAC_CACHE_TTL_SEGUNDOS" não está definida
    Quando eu carrego a configuração do ambiente
    Então a configuração tem https_only igual a false
    Então a configuração tem cache_ttl_seconds igual a 30
    Então a configuração tem login_max_tentativas igual a 5

  # Equivale a: tests/test_infra.py::TestConfiguracao::test_exige_chave_secreta
  Cenário: RNF40 - a chave secreta é obrigatória
    Dado que a variável "CINESENAC_SECRET_KEY" não está definida
    Quando eu carrego a configuração do ambiente
    Então ocorre um erro de valor que contém "CINESENAC_SECRET_KEY"

  # Equivale a: tests/test_infra.py::TestConfiguracao::test_recusa_chave_secreta_curta
  Cenário: RNF28 - uma chave secreta curta é recusada
    Quando eu crio a configuração com a chave "curta"
    Então ocorre um erro de valor que contém "CINESENAC_SECRET_KEY"

  # Equivale a: tests/test_infra.py::TestRNF14Cache::test_devolve_valor_dentro_do_ttl
  Cenário: RNF14 - o cache devolve o valor dentro do TTL
    Dado um cache com TTL de 30 segundos
    Quando eu guardo "sessao" na chave "programacao"
    Quando o relógio avança 29 segundos
    Quando eu consulto a chave "programacao"
    Então o resultado é "sessao"

  # Equivale a: tests/test_infra.py::TestRNF14Cache::test_expira_apos_o_ttl
  Cenário: RNF14 - o cache expira após o TTL
    Dado um cache com TTL de 30 segundos
    Quando eu guardo "sessao" na chave "programacao"
    Quando o relógio avança 31 segundos
    Quando eu consulto a chave "programacao"
    Então o resultado é null

  # Equivale a: tests/test_infra.py::TestRNF14Cache::test_limpar_remove_todas_as_chaves
  Cenário: RNF14 - limpar o cache remove todas as chaves
    Dado um cache com TTL de 30 segundos
    Quando eu guardo "sessao" na chave "programacao"
    Quando eu limpo o cache
    Quando eu consulto a chave "programacao"
    Então o resultado é null

  # Equivale a: tests/test_infra.py::TestRNF30LimitacaoDeTentativas::test_bloqueia_apos_o_limite_de_falhas
  Cenário: RNF30 - a chave é bloqueada após o limite de falhas
    Dado um limitador de 3 tentativas em 900 segundos
    Quando eu registro 3 falhas para "ana@exemplo.com"
    Quando eu consulto o bloqueio de "ana@exemplo.com"
    Então o resultado é true

  # Equivale a: tests/test_infra.py::TestRNF30LimitacaoDeTentativas::test_libera_apos_a_janela
  Cenário: RNF30 - o bloqueio termina quando a janela passa
    Dado um limitador de 2 tentativas em 60 segundos
    Quando eu registro 2 falhas para "x"
    Quando o relógio avança 61 segundos
    Quando eu consulto o bloqueio de "x"
    Então o resultado é false

  # Equivale a: tests/test_infra.py::TestRNF30LimitacaoDeTentativas::test_sucesso_zera_as_falhas
  Cenário: RNF30 - um login bem-sucedido zera as falhas
    Dado um limitador de 2 tentativas em 900 segundos
    Quando eu registro 1 falhas para "x"
    Quando eu registro um sucesso para "x"
    Quando eu registro 1 falhas para "x"
    Quando eu consulto o bloqueio de "x"
    Então o resultado é false

  # Equivale a: tests/test_infra.py::TestRNF27Admissao::test_recusa_quando_o_limite_de_simultaneas_e_atingido
  Cenário: RNF27 - o excedente de requisições simultâneas é recusado
    Dado um controle de admissão com 1 vaga
    Quando eu tento entrar
    Quando eu tento entrar
    Então a tentativa 1 retorna true
    Então a tentativa 2 retorna false

  # Equivale a: tests/test_infra.py::TestRNF27Admissao::test_libera_vaga_ao_sair
  Cenário: RNF27 - a vaga volta quando a requisição termina
    Dado um controle de admissão com 1 vaga
    Quando eu tento entrar
    Quando eu saio
    Quando eu tento entrar
    Então a tentativa 2 retorna true

  # Equivale a: tests/test_infra.py::TestRNF28Senhas::test_hash_nao_contem_a_senha
  Cenário: RNF28 - o hash da senha não contém a senha em texto claro
    Quando eu gero o hash da senha "senha-forte-123"
    Então o hash não contém "senha-forte-123"

  # Equivale a: tests/test_infra.py::TestRNF28Senhas::test_verifica_senha_correta
  Cenário: RNF28 - a senha correta é verificada
    Quando eu gero o hash da senha "senha-forte-123"
    Quando eu verifico a senha "senha-forte-123" contra o hash gerado
    Então o resultado é true

  # Equivale a: tests/test_infra.py::TestRNF28Senhas::test_recusa_senha_errada
  Cenário: RNF28 - uma senha errada não é aceita
    Quando eu gero o hash da senha "senha-forte-123"
    Quando eu verifico a senha "outra-senha" contra o hash gerado
    Então o resultado é false

  # Equivale a: tests/test_infra.py::TestRNF28Senhas::test_hash_invalido_nao_verifica
  Cenário: RNF28 - um hash inválido nunca verifica
    Quando eu verifico a senha "qualquer" contra o valor "nao-e-um-hash"
    Então o resultado é false

  # Equivale a: tests/test_infra.py::TestInfraHttp::test_healthz_responde_ok
  Cenário: ADR-0020 - o endpoint de saúde responde ok
    Quando o visitante envia GET "/healthz"
    Então a resposta tem status 200
    Então o campo "status" é "ok"

  # Equivale a: tests/test_infra.py::TestInfraHttp::test_openapi_expoe_contrato_v1
  Cenário: ADR-0002 - o contrato OpenAPI expõe apenas a API v1 e a saúde
    Quando o visitante envia GET "/openapi.json"
    Então a resposta tem status 200
    Então o contrato OpenAPI expõe "/v1/reservas"
    Então o contrato OpenAPI expõe "/v1/clientes"
    Então o contrato OpenAPI só expõe caminhos "/v1" e "/healthz"

  # Equivale a: tests/test_infra.py::TestInfraHttp::test_requisicao_recebe_identificador
  Cenário: ADR-0020 - a requisição mantém o identificador enviado pelo cliente
    Quando o visitante envia GET "/healthz" com o cabeçalho "X-Request-ID" igual a "abc-123"
    Então o cabeçalho "X-Request-ID" é "abc-123"

  # Equivale a: tests/test_infra.py::TestInfraHttp::test_gera_identificador_quando_ausente
  Cenário: ADR-0020 - a requisição sem identificador recebe um novo
    Quando o visitante envia GET "/healthz"
    Então o cabeçalho "X-Request-ID" existe

  # Equivale a: tests/test_infra.py::TestInfraHttp::test_recusa_com_503_e_retry_after_quando_saturado
  Cenário: RNF27 - sistema saturado responde 503 com Retry-After
    Dado que o limite de requisições simultâneas é 0
    Quando o visitante envia GET "/v1/programacao"
    Então a resposta tem status 503
    Então o cabeçalho "Retry-After" existe
    Então o código de erro é "servico_indisponivel"

  # Equivale a: tests/test_infra.py::TestInfraHttp::test_healthz_nao_e_recusado_quando_saturado
  Cenário: RNF27 - a saúde do sistema não é recusada quando saturado
    Dado que o limite de requisições simultâneas é 0
    Quando o visitante envia GET "/healthz"
    Então a resposta tem status 200

  # Equivale a: tests/test_infra.py::TestRNF31CabecalhosDeSeguranca::test_api_envia_cabecalhos_de_seguranca
  Cenário: RNF31 - a API envia cabeçalhos de segurança
    Quando o visitante envia GET "/v1/sessao"
    Então o cabeçalho "Content-Security-Policy" contém "default-src 'self'"
    Então o cabeçalho "X-Content-Type-Options" é "nosniff"
    Então o cabeçalho "X-Frame-Options" é "DENY"
    Então o cabeçalho "Referrer-Policy" é "same-origin"

  # Equivale a: tests/test_infra.py::TestCli::test_cria_administrador_inicial
  Cenário: RF01 - o comando de operação cria o primeiro administrador
    Quando eu executo a criação do administrador "dono@cinesenac.test" com a senha "senha-dono-forte-123"
    Então "dono@cinesenac.test" consegue entrar com a senha "senha-dono-forte-123"

  # Equivale a: tests/test_infra.py::TestCli::test_nao_cria_admin_com_senha_fraca
  Cenário: RNF28 - o comando recusa administrador com senha fraca
    Quando eu executo a criação do administrador "dono@cinesenac.test" com a senha "curta"
    Então ocorre um erro de domínio com o código "validacao"
