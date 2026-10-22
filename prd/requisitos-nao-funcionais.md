# Requisitos Não Funcionais — CineSenac

**Versão:** 0.1.0
**Última atualização:** 2026-10-22
**Status:** Rascunho para validação

---

## Objetivo e referências

Este documento define os requisitos não funcionais (RNFs) do CineSenac, organizados nos **oito eixos de qualidade de produto** da ISO/IEC 25010, modelo de qualidade tratado no capítulo de qualidade de software do SWEBOK. Cada RNF é conectado aos requisitos funcionais ([requisitos-funcionais.md](requisitos-funcionais.md)) e às personas ([personas](personas/)).

O cenário de referência é de **10.000 usuários em testes controlados**, detalhado nas premissas da seção 1.

**Convenções:**

- `RNFxx` identifica o requisito não funcional. Não confundir com `RNxx`, que são as regras de negócio das personas.
- `RFxx` refere-se a [requisitos-funcionais.md](requisitos-funcionais.md).
- Valores marcados como **(proposta)** são pontos de partida a validar. Nenhum valor foi medido ainda.
- Personas: **Visitante** (acesso público, sem conta), **Cliente**, **Gestor** e **Admin**. A coluna *Camada* indica onde o requisito se aplica: Frontend, Backend, Dados, Infra ou Transversal.

---

## 1. Premissas e cenário de carga

| ID | Premissa | Status |
|---|---|---|
| P01 | "10 mil pessoas" é lido como **10.000 usuários virtuais simultâneos** em ambiente de teste controlado, não em produção. | Validar: simultâneos ou total no período? |
| P02 | Tempo de pensar (*think time*) médio de 4 s por usuário, o que resulta em carga média de cerca de **2.500 req/s** (10.000 ÷ 4). | Proposta |
| P03 | Mix de comportamento: 60% navegação pública, 10% login e área do cliente, 25% reservas, 3% operação do Gestor, 2% Admin. | Proposta |
| P04 | Sala de referência para o teste de disputa de assentos: 150 assentos. É uma sala de teste, não uma regra do modelo. | Proposta |
| P05 | O ambiente de teste tem a mesma topologia da produção: frontend, API, banco e cache. | Premissa |
| P06 | Core Web Vitals são medidos em uma amostra de navegadores reais, não nos 10.000 usuários virtuais, que medem o servidor. | Premissa |

---

## 2. Requisitos não funcionais por eixo

### 2.1 Adequação funcional

Correção e integridade das regras de negócio sob concorrência.

| ID | Requisito | Critério de aceite | RFs | Personas | Camada |
|---|---|---|---|---|---|
| RNF01 | **Integridade de assentos sob concorrência:** um assento nunca é reservado duas vezes na mesma sessão, mesmo com requisições simultâneas. | 0 assentos duplicados. Reservas registradas = assentos ocupados ao final de C3 e C6. | RF21, RF22, RF23, RF30 | Cliente, Admin | Dados |
| RNF02 | **Conflito de horário sob concorrência:** um cliente não obtém reservas em sessões sobrepostas, mesmo com envios simultâneos. | 0 reservas com sobreposição de horário para o mesmo cliente em C3. | RF21, RF24 | Cliente | Backend |
| RNF03 | **Unicidade do e-mail sob concorrência:** dois cadastros simultâneos com o mesmo e-mail não criam duas contas. | 0 e-mails duplicados. O segundo pedido recebe 409. | RF04, RF05, RF06 | Cliente, Admin | Dados |
| RNF04 | **Sem sobreposição de sessões na sala:** cadastros simultâneos do Gestor não criam sessões com horário conflitante na mesma sala. | 0 sessões sobrepostas na mesma sala ao final de C4. | RF14, RF15, RF16 | Gestor | Dados |
| RNF05 | **Cota de filme nacional aplicada sempre (RN04):** nenhum dia é publicado sem sessão de filme nacional. | 100% dos dias sem sessão nacional bloqueados para publicação. | RF08, RF18, RF19 | Gestor | Backend |

### 2.2 Eficiência de desempenho

Tempo de resposta, vazão e custo de recursos, no frontend e no backend.

| ID | Requisito | Critério de aceite | RFs | Personas | Camada |
|---|---|---|---|---|---|
| RNF06 | **Latência de leitura da API:** programação, filmes, salas, mapa de assentos, reservas e dashboard respondem rápido com carga total. | p95 ≤ 300 ms em C1, C2 e C5 (proposta). | RF03, RF10, RF13, RF17, RF20, RF26, RF29 | Visitante, Cliente, Gestor, Admin | Backend |
| RNF07 | **Latência de escrita de reserva,** incluindo as respostas de negócio 409. | p95 ≤ 800 ms em C3 (proposta). | RF21, RF22, RF25 | Cliente | Backend |
| RNF08 | **Vazão sustentada:** a plataforma sustenta a carga de P02 sem sair dos critérios de desempenho. | 10.000 usuários virtuais (cerca de 2.500 req/s) por 30 min, com erro 5xx < 0,5% (proposta). | RF03, RF17, RF20, RF21, RF22, RF29 | Visitante, Cliente, Gestor, Admin | Infra |
| RNF09 | **LCP das páginas públicas:** a programação e a ficha do filme carregam rápido em rede móvel. | LCP ≤ 2,5 s no percentil 75, perfil 4G móvel, cache frio (proposta). | RF03, RF17, RF20 | Visitante, Cliente | Frontend |
| RNF10 | **INP na seleção e confirmação:** selecionar assento e confirmar a reserva responde sem atraso perceptível. | INP ≤ 200 ms no percentil 75 (proposta). | RF20, RF21 | Cliente | Frontend |
| RNF11 | **Estabilidade visual (CLS):** o layout não se desloca ao carregar a programação e o mapa de assentos. | CLS ≤ 0,1 no percentil 75 (proposta). | RF03, RF17, RF20 | Visitante, Cliente | Frontend |
| RNF12 | **Peso do JavaScript inicial:** o bundle da entrada é enxuto para dispositivos modestos. | ≤ 250 KB gzip no carregamento inicial (proposta). | RF03, RF17, RF20, RF26 | Visitante, Cliente, Gestor | Frontend |
| RNF13 | **Imagens de cartaz otimizadas:** formato moderno, tamanhos responsivos e carregamento preguiçoso fora da tela. | ≤ 200 KB por cartaz na listagem (proposta). Lazy load verificado. | RF03, RF08, RF09, RF10 | Visitante, Gestor | Frontend |
| RNF14 | **Cache da programação pública:** a leitura de C1 é absorvida fora do banco. | TTL ≤ 30 s para a programação pública. Taxa de acerto ≥ 90% em C1 (proposta). O mapa de assentos fica fora desse cache (ver RNF01). | RF03, RF17 | Visitante, Cliente | Infra |

### 2.3 Compatibilidade

Convivência com navegadores, dispositivos e outros sistemas.

| ID | Requisito | Critério de aceite | RFs | Personas | Camada |
|---|---|---|---|---|---|
| RNF15 | **Navegadores:** últimas 2 versões principais de Chrome, Edge, Firefox e Safari. | Os fluxos E2E de reserva passam nos quatro navegadores. | Todos | Todas | Frontend |
| RNF16 | **Dispositivos:** layout responsivo de 360 px até desktop, com Android (Chrome) e iOS (Safari) nas últimas 2 versões principais. Prioridade para RF20 a RF26, usados majoritariamente pelo Cliente em celular. | Fluxos principais sem rolagem horizontal em 360 px. | Todos | Cliente, Gestor, Admin | Frontend |
| RNF17 | **Contrato de API versionado:** a API é documentada (OpenAPI) e consumida pelo frontend. Mudança incompatível exige nova versão. | Contrato publicado. Teste de contrato executado no build. | Todos | Todas | Backend |

### 2.4 Usabilidade

Facilidade de aprender, operar e entender o sistema.

| ID | Requisito | Critério de aceite | RFs | Personas | Camada |
|---|---|---|---|---|---|
| RNF18 | **Acessibilidade WCAG 2.2 nível AA** em todas as telas. | 0 falhas AA na verificação automatizada. Revisão manual das telas de RF20 a RF25. | Todos | Todas | Frontend |
| RNF19 | **Mapa de assentos acessível:** operável por teclado, e cada assento tem rótulo legível (ex.: "Fila A, assento 7, livre"). | Navegação completa só por teclado. Leitor de tela anuncia o estado do assento. | RF20, RF21 | Cliente | Frontend |
| RNF20 | **Mensagens de conflito e unicidade claras:** cada 409 vira texto com a ação sugerida. | Cada erro de RF05, RF15, RF23 e RF24 tem mensagem específica revisada. | RF05, RF15, RF23, RF24 | Cliente, Gestor | Frontend |
| RNF21 | **Fluxo de reserva curto:** da escolha da sessão até a confirmação. | Até 4 interações após escolher a sessão. Conclusão ≥ 90% em teste de usabilidade com usuários de teste (proposta). | RF20, RF21, RF22, RF25 | Cliente | Frontend |
| RNF22 | **Formulários com validação antes do envio:** campos obrigatórios sinalizados e erros exibidos sem recarregar a página. | Erros de campo aparecem na própria tela, sem perda dos dados digitados. | RF04, RF08, RF11, RF14 | Cliente, Gestor | Frontend |

### 2.5 Confiabilidade

Comportamento correto e estável, inclusive em falhas e retentativas.

| ID | Requisito | Critério de aceite | RFs | Personas | Camada |
|---|---|---|---|---|---|
| RNF23 | **Disponibilidade durante a janela de teste.** | ≥ 99,5% (proposta). | Todos | Todas | Infra |
| RNF24 | **Idempotência da reserva:** reenvio do mesmo pedido (duplo clique, retentativa de rede) não gera reservas duplicadas. | 0 reservas duplicadas em teste de reenvio. Chave de idempotência por pedido. | RF21, RF22 | Cliente | Backend |
| RNF25 | **Atomicidade da reserva de múltiplos assentos (RN02):** ou todos os assentos são reservados, ou nenhum. | 0 reservas parciais em falha simulada no meio do pedido. | RF22 | Cliente | Dados |
| RNF26 | **Durabilidade e recuperação:** reservas confirmadas sobrevivem à queda de uma instância, e o banco tem backup. | 0 reservas confirmadas perdidas em teste de queda. RPO ≤ 24 h (proposta). | RF22, RF27, RF30 | Cliente, Admin | Infra |
| RNF27 | **Degradação controlada acima da capacidade:** resposta 503 com `Retry-After` e tela de "tente novamente", nunca página em branco. | 100% das respostas de erro em sobrecarga trazem `Retry-After` e mensagem. | RF03, RF17, RF20, RF21 | Visitante, Cliente | Backend |

### 2.6 Segurança

Proteção de dados, acesso e integridade contra uso indevido.

| ID | Requisito | Critério de aceite | RFs | Personas | Camada |
|---|---|---|---|---|---|
| RNF28 | **Autenticação segura:** senhas com hash adaptativo, todo tráfego por HTTPS e sessão que expira por inatividade. | 0 senhas em texto claro. Prazo de expiração definido (a definir). | RF01, RF27 | Todas | Backend |
| RNF29 | **Autorização no servidor:** toda rota valida o perfil. Ocultar botão na tela não é controle de acesso. | 0 rotas acessíveis fora do perfil em teste de acesso cruzado. | RF02, RF06, RF07, RF09, RF12, RF16, RF27, RF28, RF30 | Gestor, Admin, Cliente | Backend |
| RNF30 | **Proteção contra força bruta no login:** limite de tentativas por e-mail e por IP, com bloqueio temporário após N falhas (N a definir). | Tentativas acima do limite são recusadas. Login legítimo não é afetado em C2. | RF01 | Todas | Backend |
| RNF31 | **Segurança de conteúdo no frontend:** política de conteúdo (CSP), saneamento de textos livres (sinopse, elenco) e aceitação apenas de URL `http(s)` para o cartaz. | 0 scripts injetados executados em teste. URL com esquema `javascript:` rejeitada. | RF04, RF06, RF08, RF09 | Gestor, Cliente | Frontend |
| RNF32 | **Privacidade (LGPD):** dados pessoais (nome, e-mail, idade, endereço) têm finalidade declarada e são visíveis apenas ao titular e ao Admin. Exportação e exclusão são possíveis. | 0 leituras de dados de outro cliente em teste de acesso. Fluxo de exclusão documentado. | RF04, RF06, RF07, RF26, RF27 | Cliente, Admin | Dados |
| RNF33 | **Trilha de auditoria:** ações administrativas e cancelamentos ficam registrados com autor, data e hora, ação e alvo. | 100% das ações de RF16, RF27, RF28 e RF30 com registro. | RF16, RF27, RF28, RF30 | Admin, Gestor | Backend |

### 2.7 Manutenibilidade

Facilidade de modificar, testar e evoluir o sistema.

| ID | Requisito | Critério de aceite | RFs | Personas | Camada |
|---|---|---|---|---|---|
| RNF34 | **Regras de negócio em camada testável:** RN01 a RN04 ficam em serviços independentes da interface. | Cobertura de testes automatizados ≥ 80% nessa camada (proposta). | RF15, RF18, RF19, RF21, RF22, RF23, RF24 | Gestor, Cliente | Backend |
| RNF35 | **Gates de qualidade antes do merge:** lint, typecheck, testes e build (Art. V da constituição do AIOX). | Pipeline verde obrigatório para merge. | Todos | Equipe | Transversal |
| RNF36 | **Teste de carga reproduzível e versionado:** cenários C1 a C6 estão em código, com dados de teste recriáveis. | Dois ciclos com resultado dentro de ±10% (proposta). | Todos | Equipe, Admin | Infra |
| RNF37 | **Componentes de frontend isolados:** mapa de assentos, formulários e dashboard são componentes reutilizáveis e testados. | Teste de componente para o mapa de assentos e para os formulários de RF08 a RF13. | RF08, RF09, RF10, RF11, RF12, RF13, RF20, RF29 | Gestor, Cliente, Admin | Frontend |
| RNF38 | **Observabilidade:** latência, taxa de erro e saturação por rota, com logs estruturados, para diagnosticar C1 a C6. | Painel com métricas por rota durante o teste. | RF29 | Admin | Infra |

### 2.8 Portabilidade

Facilidade de executar o sistema em outros ambientes.

| ID | Requisito | Critério de aceite | RFs | Personas | Camada |
|---|---|---|---|---|---|
| RNF39 | **Empacotamento em contêineres:** aplicação e banco rodam com a mesma imagem em teste e em produção. | Build reproduzível. O mesmo artefato é promovido entre ambientes. | Todos | Todas | Infra |
| RNF40 | **Configuração externalizada:** parâmetros de ambiente vêm de variáveis, sem segredos no código. | 0 segredos versionados (ver [.env.example](../.env.example)). | Todos | Todas | Infra |
| RNF41 | **Esquema de banco versionado:** migrações derivadas de [dbdiagram.dbml](dbdiagram.dbml). | Banco de teste criado do zero por migrações, sem intervenção manual. | RF04, RF08, RF11, RF14, RF22 | Todas | Dados |

---

## 3. Considerações de frontend

Decisões que afetam o frontend e os RNFs de desempenho, usabilidade e segurança. Cabem ao [@architect](../.github/agents/architect.agent.md), exceto onde indicado.

| ID | Decisão | Recomendação | RNFs | Responsável |
|---|---|---|---|---|
| D1 | Renderização | Páginas públicas (programação e filmes) renderizadas no servidor ou estáticas, com cache. Áreas autenticadas podem ser SPA. | RNF09, RNF11, RNF14 | @architect |
| D2 | Atualização do mapa de assentos | Sem *polling* automático. Revalidar ao abrir o mapa e no envio da reserva. *Polling* a cada 5 s com 10.000 usuários adicionaria cerca de 2.000 req/s, cerca de 80% da carga média de P02. | RNF01, RNF06, RNF08 | @architect |
| D3 | Envio da reserva | Botão de confirmação desabilitado durante a requisição. O reenvio usa a mesma chave de idempotência. | RNF07, RNF24 | Frontend |
| D4 | Estados de carga e erro | Skeleton nas listas. Tela de "tente novamente" com contagem para `Retry-After`. Nunca tela em branco. | RNF21, RNF27 | Frontend |
| D5 | Token de sessão | Preferir cookie `HttpOnly`, inacessível a scripts, a armazenamento legível pelo JavaScript. | RNF28, RNF31 | @architect |
| D6 | Imagens | Servidas por CDN, com dimensões responsivas. | RNF13, RNF14 | Infra e frontend |
| D7 | Validação em navegadores reais | Testes E2E de RF20 a RF25 em uma matriz de navegadores e dispositivos. | RNF10, RNF15, RNF16 | QA |

---

## 4. Cenários de teste controlado

Os cenários usam o mix da premissa P03. Cada cenário verifica os RNFs listados.

| Cenário | Descrição | Personas | RFs | RNFs verificados | Critério de aceite |
|---|---|---|---|---|---|
| C1 | Navegação pública: programação, filmes e mapa de assentos. | Visitante, Cliente | RF03, RF17, RF20 | RNF06, RNF08, RNF14, RNF27 | p95 ≤ 300 ms. 5xx < 0,5%. Acerto de cache ≥ 90%. |
| C2 | Login, cadastro e área do cliente. | Cliente | RF01, RF04, RF07, RF26 | RNF03, RNF06, RNF28, RNF30, RNF32 | p95 ≤ 300 ms. Nenhum vazamento de dados entre clientes. |
| C3 | Pico de reserva em uma mesma sessão (25% dos usuários, sala de 150 assentos). | Cliente | RF20 a RF25 | RNF01, RNF02, RNF07, RNF24, RNF25 | 0 assentos duplicados. 0 sobreposições. p95 ≤ 800 ms. |
| C4 | Operação do Gestor durante C1 a C3. | Gestor | RF08 a RF16 | RNF04, RNF05, RNF13 | 0 sessões sobrepostas. p95 da escrita ≤ 800 ms. C1 sem regressão. |
| C5 | Admin: dashboard e cancelamento de reservas. | Admin | RF27 a RF30 | RNF06, RNF26, RNF33, RNF38 | Dashboard p95 ≤ 300 ms. Cancelamento libera o assento (RNF01). |
| C6 | Estresse: 10.000 usuários disputando a mesma sessão. | Cliente | RF21 a RF24, RF30 | RNF01, RNF02, RNF07, RNF27 | 0 duplicidades. Ao final, reservas = assentos ocupados. 503 com `Retry-After` onde houver saturação. |

---

## 5. Matriz de rastreabilidade

### 5.1 RF → RNF

Cada RF aponta para os RNFs que se aplicam a ele. Os RNFs transversais (RNF15, RNF16, RNF17, RNF18, RNF23, RNF35, RNF36, RNF39 e RNF40) valem para todos os RFs e não aparecem aqui.

| RF | Requisito (resumo) | RNFs específicos |
|---|---|---|
| RF01 | Login por perfil | RNF28, RNF30 |
| RF02 | Controle de acesso por perfil | RNF29 |
| RF03 | Consulta pública da programação | RNF06, RNF08, RNF09, RNF11, RNF12, RNF13, RNF14, RNF27 |
| RF04 | Cadastro do cliente | RNF03, RNF22, RNF31, RNF32, RNF41 |
| RF05 | E-mail único | RNF03, RNF20 |
| RF06 | Edição do cadastro do cliente | RNF03, RNF29, RNF31, RNF32 |
| RF07 | Visualização do cadastro do cliente | RNF29, RNF32 |
| RF08 | Cadastro de filme | RNF05, RNF13, RNF22, RNF31, RNF37, RNF41 |
| RF09 | Edição e exclusão de filme | RNF13, RNF29, RNF31, RNF37 |
| RF10 | Listagem e busca de filmes | RNF06, RNF13, RNF37 |
| RF11 | Cadastro de sala | RNF22, RNF37, RNF41 |
| RF12 | Edição e exclusão de sala | RNF29, RNF37 |
| RF13 | Listagem e busca de salas | RNF06, RNF37 |
| RF14 | Cadastro de sessão | RNF04, RNF22, RNF41 |
| RF15 | Sobreposição de sessão na sala | RNF04, RNF20, RNF34 |
| RF16 | Edição e cancelamento de sessão | RNF04, RNF29, RNF33 |
| RF17 | Consulta da programação com filtros | RNF06, RNF08, RNF09, RNF11, RNF12, RNF14, RNF27 |
| RF18 | Indicador da cota nacional | RNF05, RNF34 |
| RF19 | Bloqueio de publicação sem cota nacional | RNF05, RNF34 |
| RF20 | Mapa de assentos | RNF06, RNF08, RNF09, RNF10, RNF11, RNF12, RNF19, RNF21, RNF27, RNF37 |
| RF21 | Seleção de assentos | RNF01, RNF02, RNF07, RNF08, RNF10, RNF19, RNF21, RNF24, RNF27, RNF34 |
| RF22 | Registro da reserva | RNF01, RNF07, RNF08, RNF21, RNF24, RNF25, RNF26, RNF34, RNF41 |
| RF23 | Bloqueio de assento ocupado | RNF01, RNF20, RNF34 |
| RF24 | Conflito de horário do cliente | RNF02, RNF20, RNF34 |
| RF25 | Confirmação da reserva | RNF07, RNF21 |
| RF26 | Lista das próprias reservas | RNF06, RNF12, RNF32 |
| RF27 | Gestão de contas pelo Admin | RNF26, RNF28, RNF29, RNF32, RNF33 |
| RF28 | Gestão de permissões | RNF29, RNF33 |
| RF29 | Dashboard do Admin | RNF06, RNF08, RNF37, RNF38 |
| RF30 | Cancelamento de reservas pelo Admin | RNF01, RNF26, RNF29, RNF33 |

### 5.2 Persona → RNF prioritários

| Persona | RNFs prioritários | Motivo |
|---|---|---|
| Visitante | RNF06, RNF09, RNF11, RNF12, RNF14, RNF27 | Navegação pública é a maior parte da carga (P03) e define a primeira impressão. |
| Cliente | RNF01, RNF02, RNF07, RNF10, RNF19, RNF20, RNF21, RNF24, RNF25, RNF28, RNF30, RNF32 | Reserva é o fluxo de maior disputa e tem regras de concorrência. |
| Gestor | RNF04, RNF05, RNF13, RNF22, RNF29, RNF31, RNF33 | Opera o catálogo e a programação, e precisa de validação e cota corretas. |
| Admin | RNF01, RNF26, RNF29, RNF32, RNF33, RNF38 | Monitora a integridade dos dados e responde por exceções e cancelamentos. |

---

## 6. Pendências e decisões

1. **Escopo da carga (P01):** os 10.000 são simultâneos ou o total de usuários no período? A carga deve ser sustentada por quanto tempo?
2. **Mix de personas (P03) e sala de referência (P04):** validar as proporções e o tamanho da sala de teste.
3. **Valores propostos:** validar os números marcados como (proposta) com produto e infraestrutura.
4. **Persona Visitante:** os RF03 e RF17 usam o perfil Visitante, mas não há arquivo em [personas](personas/). Criar `prd/personas/visitante.md` ou confirmar que é um perfil sem conta, sem persona própria.
5. **Terminologia:** [gestor.md](personas/gestor.md) fala em "classificação indicativa", enquanto RF08 e o DBML usam "faixa etária". Alinhar o termo.
6. **LGPD (RNF32):** confirmar o papel do CineSenac como controlador dos dados e as finalidades de tratamento.
7. **Decisões de arquitetura D1, D2 e D5:** para o [@architect](../.github/agents/architect.agent.md).
8. **Parâmetros a definir:** prazo de expiração da sessão (RNF28) e limite N de tentativas de login (RNF30).

---

## 7. Fontes

- SWEBOK — capítulo de qualidade de software (modelo de características de qualidade, ISO/IEC 25010).
- ISO/IEC 25010 — modelo de qualidade de sistemas e software (características de qualidade de produto).
- WCAG 2.2 — Web Content Accessibility Guidelines, W3C.
- Core Web Vitals — LCP, INP e CLS, Google (web.dev).
- Lei nº 13.709/2018 — Lei Geral de Proteção de Dados Pessoais (LGPD).

---

_Última atualização: 2026-10-22 | Rascunho para validação_
