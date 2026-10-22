# Tutorial — CineSenac: da documentação ao sistema testado e publicado

Este tutorial documenta, passo a passo, o que construímos depois da fase de PRD (ver [tutorial.md](tutorial.md)): requisitos não funcionais, modelagens, arquitetura, implementação em Python com TDD, testes BDD, relatório de cobertura, contêiner e pipeline de CI, até o merge na `main`.

Cada passo traz a fala do usuário citada **literalmente**, o que foi produzido e, quando houver, a lição tirada. As falas foram copiadas como estavam, com os erros de digitação originais.

---

## Visão geral

| Passo | Tema | Artefatos principais |
|---|---|---|
| 1 | Requisitos não funcionais (SWEBOK, 8 eixos) | `prd/requisitos-nao-funcionais.md` |
| 2 | Modelagens estática e dinâmica | `prd/modelagem/` |
| 3 | Arquitetura e ADRs | `prd/arquitetura/` |
| 4 | Implementação com TDD e front end Jinja2 | `app/`, `tests/`, ADR-0021 |
| 5 | Testes BDD em Gherkin | `features/`, `tests/bdd/` |
| 6 | Relatório de cobertura, GitHub e CI com testcontainers | `prd/qualidade/`, `Dockerfile`, `.github/workflows/ci.yml` |
| 7 | Verificação do envio | — |
| 8 | Merge na `main` | commit `21ebbf5` |
| 9 | Este tutorial | `tutorial-implementacao.md` |

---

## Passo 1 — Requisitos não funcionais

### Prompt

> "Baseado no SWEBOK, vamos alinhar os requisitos não funcionais, em 8 eixos da qualidade. para 10 mil pessoas em testes ocntorlados. ligue e conecte todos os RNF com os RFS e as personas. leve em consideração um frontend"

### Resultado

- `prd/requisitos-nao-funcionais.md`, com **41 RNFs** (RNF01 a RNF41) organizados nos oito eixos da ISO/IEC 25010: adequação funcional, desempenho, compatibilidade, usabilidade, confiabilidade, segurança, manutenibilidade e portabilidade.
- Cada RNF traz critério de aceite, RFs, personas e camada (frontend, backend, dados, infra ou transversal).
- Premissas explícitas para o cenário de 10.000 usuários virtuais simultâneos (cerca de 2.500 req/s com *think time* de 4 s), todas marcadas para validação.
- Matriz RF → RNF, gerada a partir das próprias tabelas, e uma seção de decisões de frontend (D1 a D7).
- Links de volta em `README.md` e `prd/requisitos-funcionais.md`.

**Aprendizado:** a regra "No Invention" do `.aiox-core/constitution.md` exige que todo número proposto venha de uma premissa declarada. Por isso os valores ficaram marcados como *(proposta)*, e não como fato.

---

## Passo 2 — Modelagens estática e dinâmica

### Prompt

> "precisamos então agora fazer uma pasta de modelagens dinamicas e outra de modelagens esttaticas> Na estatica quero um diagrama d ecomponenets completo, agnostico, e classes para delimitar as entidades. Na modelagem dinamica quero para cada requisito funcional suportado por rnf o diagrama de sequencia. Pode ser em mermaid"

### Resultado

- `prd/modelagem/estatica/componentes.md`: diagrama de componentes agnóstico de tecnologia, em camadas (apresentação, borda, aplicação, dados), com responsabilidades e interfaces.
- `prd/modelagem/estatica/classes.md`: diagrama de classes das entidades, com restrições de unicidade e mapeamento para o DBML. Entidades ausentes do DBML (Usuario, Perfil, Permissao, RegistroAuditoria) aparecem marcadas como pendentes.
- `prd/modelagem/dinamica/`: **30 arquivos**, um por RF (RF01 a RF30), cada um com um diagrama de sequência em Mermaid, personas, RNFs realizados e notas explicando como o fluxo cumpre cada RNF.
- Validação dos 32 blocos Mermaid com o parser oficial (versão 11.17.2), com um teste de sanidade confirmando que o validador rejeita um diagrama quebrado.

**Aprendizado:** a matriz RF → RNF e os diagramas dinâmicos divergiram em três pontos (RNF28, RNF29 e RNF32). A checagem cruzada por script encontrou os três, e a matriz foi corrigida para refletir os diagramas.

---

## Passo 3 — Arquitetura e ADRs

### Prompt

> "Crie a documentçaão da arquietetura e as ADRs para cada tática arquietetural"

### Resultado

- `prd/arquitetura/arquitetura.md`: drivers arquiteturais (seis cenários de qualidade), contexto, estilo, visão de execução, implantação agnóstica, mapa de táticas por atributo, trade-offs e riscos.
- `prd/arquitetura/adr/`: **20 ADRs** (ADR-0001 a ADR-0020), uma por tática arquitetural, cada uma com contexto, decisão, alternativas, consequências e links para RNFs, RFs e diagramas.
- `prd/arquitetura/adr/README.md`: índice, processo de aceite (Proposta → Aceita → Substituída) e modelo para novas decisões.

Todas as ADRs nasceram com status **Proposta**, porque a aceitação é decisão do `@architect`.

**Aprendizado:** a lista de RFs de cada ADR foi escrita à mão no primeiro rascunho e estava errada. Foi substituída por derivação automática a partir da matriz de RNFs. Quando a fonte de verdade é uma tabela, deixe o script derivar o que for derivável.

---

## Passo 4 — Implementação com TDD e front end Jinja2

### Prompt

> "Agora com a documentção como fonte de verdad,e implemente os testes em TDD e a espinha dorsal da infra estrutura: em pytohon, e o front end e jinja"

### Resultado

**Decisão de stack, registrada antes do código** (`prd/arquitetura/adr/ADR-0021-stack-de-implementacao-inicial.md`): Python 3.12, FastAPI com API `/v1` e OpenAPI, Jinja2 para as páginas, SQLAlchemy com SQLite, argon2 para senhas, cookie de sessão assinado, cache e limitação em memória atrás de interfaces. A ADR também registra as limitações conhecidas: instância única, bloqueio de escrita global e migrações ainda não versionadas.

**Ordem TDD:**

1. Escrevemos a suíte inteira antes do código: `tests/conftest.py`, `tests/helpers.py` e nove arquivos de teste, cada um citando o RF ou RNF que verifica.
2. Primeira execução: falha de importação, porque o pacote `app` não existia. Esse vermelho é o esperado, mas é pouco informativo, porque reprova o módulo inteiro, e não cada comportamento.
3. Implementação por camada: configuração e erros, regras puras, infraestrutura, modelos e banco, serviços, API v1, páginas Jinja2.
4. Ciclos de vermelho e verde posteriores: cinco testes novos para o cadastro pela página, a página "Minha conta" de um admin sem cadastro (que dava erro 500) e a auto-desativação do admin.

**Estrutura entregue:**

- `app/main.py`: fábrica `create_app`, com middlewares de admissão, cabeçalhos de segurança e identificador de requisição.
- `app/servicos/`: regras com efeito no banco (clientes, catálogo, programação, reservas, administração, autenticação e auditoria). Cada escrita grava a auditoria na mesma transação.
- `app/api/`: API `/v1`, com schemas Pydantic na borda e dependências de sessão, CSRF e permissão.
- `app/web/`: páginas Jinja2 que chamam os mesmos serviços, com CSS responsivo e nenhum script ou estilo inline (compatível com a CSP).
- `app/cli.py`: `criar-admin`, porque a API exige um administrador já autenticado.
- **156 testes passando** ao fim do passo.

**Verificações específicas:**

- Concorrência real com threads: 10 e 12 clientes disputando o mesmo assento e o mesmo e-mail, e um cliente disputando duas sessões sobrepostas.
- Idempotência, limite de tentativas de login, degradação com 503 e `Retry-After`, CSRF, cabeçalhos de segurança e escape de HTML.
- Execução real do servidor com uvicorn, e um fluxo de negócio completo pela rede.
- Imagem Docker construída e executada como usuário sem privilégio, com healthcheck.

**Problemas encontrados e corrigidos neste passo:**

- Um comando de shell com heredoc quebrado fez o módulo `auditoria.py` não ser gravado. Foi recriado e verificado.
- O OpenAPI expunha as páginas Jinja2, quando o contrato deveria ser só a API. Corrigido com `include_in_schema=False`.
- Um teste tinha uma asserção vazia (`or True`), que foi substituída por uma verificação real antes de rodar.
- `uv run pytest` falhava por causa de `sys.path`, enquanto `python -m pytest` funcionava. Corrigido com `pythonpath = ["."]`.

**Aprendizado:** o cache da programação pública ficou com dado antigo por até 30 s, porque a ADR-0007 não prevê invalidação ativa. Isso apareceu na primeira execução real, e não nos testes, que usavam TTL zero para ser determinísticos. O efeito foi registrado na própria ADR-0007 como achado de implementação, com a proposta de invalidar ao publicar, e não foi alterado sem decisão do arquiteto.

---

## Passo 5 — Testes BDD em Gherkin

### Prompt

> "ok, agora vamos criar os testes em gerkhin, BDD, given when then, com todos os cenarios de testes que encontramos. cubra 100% dos testes em BDD source /home/afonsolelis/repos/cinesenac/.venv/bin/activate"

### Resultado

- `features/`: **9 arquivos** `.feature` em português (`dominio`, `infra`, `auth`, `clientes`, `catalogo`, `programacao`, `reservas`, `admin`, `web`), com **151 cenários** (dois deles são Esquemas do Cenário), que expandem para **156 execuções**.
- Cada cenário tem uma linha `# Equivale a: <node ids>` apontando para o teste original. Um cenário pode cobrir mais de um teste (os esquemas).
- `tests/bdd/`: `mundo.py` (estado de cada cenário: atores HTTP com cookies próprios, respostas e identificadores), `steps.py` (passos com expressões regulares ancoradas), `conftest.py` e um módulo `test_*_bdd.py` por feature.
- `tests/bdd/test_cobertura_bdd.py`: lê os testes por AST e os marcadores `# Equivale a:` e garante o mapeamento nos dois sentidos. Falha se um teste ficar sem cenário ou se um cenário apontar para um teste que não existe.
- Ao fim do passo: **314 testes passando** (156 unitários, 2 de cobertura BDD e 156 cenários).

**Problemas encontrados e corrigidos neste passo:**

- O pytest-bdd casa o texto do passo **sem** a palavra-chave (`Dado`, `Quando`, `Então`). Minhas expressões regulares incluíam a palavra-chave, e nenhum passo casava. Corrigido removendo o prefixo das 96 âncoras.
- Expressões regulares com `"{caminho}"` no parser padrão causariam ambiguidade entre passos mais longos e mais curtos. Por isso os passos usam `parsers.re` com `[^"]+` e âncoras.
- O `TestClient` seguia redirects por padrão, e os testes de página verificam o 303. O mundo passou a usar `follow_redirects=False`.
- Um cenário de cookie faltava abrir a página de login antes de postar, então não havia token CSRF. Corrigido no próprio cenário, que tinha a falha.
- O Starlette escreve atributos de cookie em minúsculas (`httponly`). A comparação de cabeçalhos passou a ignorar caixa, o comportamento correto para esse caso.

**Aprendizado:** o mapeamento por código é mais confiável que a inspeção humana. O teste de cobertura BDD pegou divergências que uma revisão visual deixaria passar, e ele próprio fica na suíte, então o mapeamento não pode degradar sem que o pipeline quebre.

---

## Passo 6 — Relatório de cobertura, GitHub e CI com testcontainers

### Prompt

> "depois que você fizer todos os BDDs, gere um relatório com a cobertura de testes. suba no github, com um pipeline em CI com testcontainers."

Esta fala foi enviada **durante** a execução do passo 5. Ela foi tratada depois que os cenários ficaram prontos.

### Resultado

- **Cobertura medida:** 91,1% de linhas e ramos em `app/` (1197 de 1290 linhas, 179 de 220 ramos). Os números vêm do `coverage.json`, e o relatório é gerado por script (`tests/bdd/gerar_relatorio.py`), não digitado.
- `prd/qualidade/relatorio-cobertura.md`: resumo, cobertura por módulo, lacunas conhecidas e como reproduzir. Indicador de mapeamento BDD: **156 de 156** testes com cenário equivalente.
- `Dockerfile`: imagem em `python:3.12-slim`, com usuário sem privilégio (uid 10001), segredo só por variável de ambiente, banco em volume e healthcheck.
- `tests/container/test_imagem.py`: **5 testes com testcontainers** que sobem a imagem real e verificam healthcheck, vitrine com cabeçalhos de segurança, estáticos, contrato da API e que o processo não roda como root.
- `.github/workflows/ci.yml`, com dois jobs:
  - **Testes, BDD e cobertura:** `uv sync --locked`, testes com gate de 85%, relatório no resumo do job e upload de artefatos.
  - **Imagem de contêiner:** constrói a imagem e roda os testes de contêiner contra ela.
- Branch `feat/app-bdd-ci` e **PR #1**, que disparou o pipeline.

**Lacunas que o relatório declara, sem esconder:**

- As rotas de formulário do gestor e do admin (`app/web/routes.py`) têm cerca de 75% de cobertura, porque nenhum cenário BDD as exercita.
- O testcontainers sobe apenas a imagem da aplicação. O app usa SQLite de arquivo, então não há contêiner de banco para subir. Isso exige trocar o banco, como já está previsto na ADR-0021.

**Aprendizado:** o relatório gerado pelo mesmo comando que roda a suíte e o pipeline mantém o número honesto. Um relatório escrito à mão tenderia a arredondar.

---

## Passo 7 — Verificação do envio

### Prompt

> "ja subiu?"

### Resultado

Verificado o estado do PR e do pipeline com `gh`. O job de contêiner já tinha sucesso, e o job de testes ainda estava em andamento. Respondi sem fazer nenhuma ação.

**Aprendizado:** não mesclar antes de o pipeline inteiro terminar. Uma verificação parcial não basta para uma ação irreversível na `main`.

---

## Passo 8 — Merge na `main`

### Prompt

> "ok, faça o merge na main"

### Resultado

- Antes do merge, conferi o resultado dos dois jobs: **testes, BDD e cobertura: SUCCESS** e **imagem de contêiner: SUCCESS**, com o gate de 85% atendido.
- Merge do PR #1 com `--merge` (preserva o commit da branch), com a remoção da branch `feat/app-bdd-ci` no GitHub.
- A `main` local foi sincronizada. Commit de merge: `21ebbf5`. Commit da funcionalidade: `147a684`.

**Aprendizado:** a ordem certa é verificar o resultado de cada job e só então mesclar. A mensagem do usuário pedia o merge, mas o merge só era seguro depois do sinal verde.

---

## Passo 9 — Este tutorial

### Prompt

> "agora crie um tutorial completo do que fizemos aqui, mas não suba ainda."

### Resultado

- `tutorial-implementacao.md`, criado localmente e **não versionado**. Não foi feito commit nem push.
- O `tutorial.md` original, que é o histórico do PRD, foi mantido intacto. A skill `update-tutorial` manda acrescentar passos a ele, então a integração entre os dois fica como decisão sua.

---

## Como reproduzir o estado final

```bash
git checkout main && git pull
uv sync --locked
uv run pytest -m "not container" --cov               # 314 testes e cobertura
uv run python -m tests.bdd.gerar_relatorio           # relatório em prd/qualidade/
docker build -t cinesenac:dev .
CINESENAC_IMAGE=cinesenac:dev uv run pytest -m container
```

Para subir a aplicação localmente:

```bash
export CINESENAC_SECRET_KEY="uma-chave-com-32-ou-mais-caracteres"
uv run python -m app.cli criar-admin --email admin@exemplo.com
uv run uvicorn app.main:criar_app --factory --reload
```

---

## Pendências e decisões em aberto

Estas decisões não foram tomadas por mim, porque pertencem ao usuário ou ao arquiteto:

1. **Aceitar ou ajustar as 21 ADRs** (todas em Proposta).
2. **Invalidação do cache da programação** (ADR-0007): ao publicar, cancelar ou alterar sessão.
3. **Parâmetros ainda sem valor:** prazo de sessão, tentativas de login, limites de taxa após teste de carga, RPO e RTO, retenção de auditoria e de chaves de idempotência, limite de assentos por pedido.
4. **Persona Visitante** continua sem arquivo próprio.
5. **Entidades fora do DBML:** Usuario, Perfil, Permissao e RegistroAuditoria ainda não estão no `dbdiagram.dbml`.
6. **Assentos todos na fila A**, seguindo o fluxo de RF11 ao pé da letra. Vale confirmar se é o comportamento desejado para salas grandes.
7. **Lacunas de cobertura** em `app/web/routes.py` (formulários do gestor e do admin).
8. **Migrações versionadas** (ADR-0016) e **banco cliente-servidor** para escalar horizontalmente.
9. **Repositório público:** o GitHub `afonsolelis/cinesenac` é público, e o código já está lá.
10. **Não enviado:** este tutorial, criado localmente e ainda não versionado.
