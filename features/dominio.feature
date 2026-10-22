# language: pt
Funcionalidade: Regras de domínio puras
  Regras de negócio sem HTTP nem banco. Sustentam RF11, RF15, RN04 e RNF19.

  Contexto:
    Dado que o sistema está em execução

  # Equivale a: tests/test_dominio.py::TestRF15Sobreposicao::test_sessoes_adjacentes_nao_conflitam, tests/test_dominio.py::TestRF15Sobreposicao::test_sessoes_que_se_cruzam_conflitam, tests/test_dominio.py::TestRF15Sobreposicao::test_sessao_contida_em_outra_conflita, tests/test_dominio.py::TestRF15Sobreposicao::test_mesmo_horario_conflita, tests/test_dominio.py::TestRF15Sobreposicao::test_sessao_anterior_adjacente_nao_conflita
  Esquema do Cenário: RF15 - sessões na mesma sala conflitam apenas quando os intervalos se cruzam
    Quando eu verifico se os intervalos "<inicio_a>" por <duracao_a> minutos e "<inicio_b>" por <duracao_b> minutos se sobrepõem
    Então o resultado é <resultado>

    Exemplos:
      | inicio_a | duracao_a | inicio_b | duracao_b | resultado |
      | 19:00    | 120       | 21:00    | 60        | false     |
      | 19:00    | 120       | 20:00    | 60        | true      |
      | 19:00    | 180       | 19:30    | 30        | true      |
      | 19:00    | 120       | 19:00    | 120       | true      |
      | 19:00    | 120       | 18:00    | 60        | false     |

  # Equivale a: tests/test_dominio.py::TestRF11Assentos::test_gera_codigos_de_A1_ate_An
  Cenário: RF11 - a sala gera os assentos de A1 até An
    Quando eu gero os códigos de 3 assentos
    Então o resultado é ["A1", "A2", "A3"]

  # Equivale a: tests/test_dominio.py::TestRF11Assentos::test_quantidade_zero_nao_gera_assentos
  Cenário: RF11 - uma sala sem assentos não é gerada
    Quando eu gero os códigos de 0 assentos
    Então ocorre um erro de valor que contém "a sala precisa de pelo menos um assento"

  # Equivale a: tests/test_dominio.py::TestRN04CotaNacional::test_cota_atendida_com_ao_menos_um_nacional
  Cenário: RN04 - o dia tem cota atendida com ao menos um filme nacional
    Quando eu avalio a cota com as nacionalidades "INTERNACIONAL,NACIONAL"
    Então o resultado é true

  # Equivale a: tests/test_dominio.py::TestRN04CotaNacional::test_cota_pendente_sem_nacional
  Cenário: RN04 - o dia fica com cota pendente sem filme nacional
    Quando eu avalio a cota com as nacionalidades "INTERNACIONAL"
    Então o resultado é false

  # Equivale a: tests/test_dominio.py::TestRN04CotaNacional::test_cota_pendente_sem_sessoes
  Cenário: RN04 - o dia sem sessões fica com cota pendente
    Quando eu avalio a cota com as nacionalidades ""
    Então o resultado é false

  # Equivale a: tests/test_dominio.py::TestRNF19RotuloAcessivel::test_rotulo_de_assento_livre, tests/test_dominio.py::TestRNF19RotuloAcessivel::test_rotulo_de_assento_ocupado
  Esquema do Cenário: RNF19 - cada assento tem rótulo legível por leitor de tela
    Quando eu monto o rótulo do assento "<codigo>" como "<estado>"
    Então o resultado é "<rotulo>"

    Exemplos:
      | codigo | estado  | rotulo                        |
      | B7     | livre   | Fila B, assento 7, livre      |
      | A1     | ocupado | Fila A, assento 1, ocupado    |
