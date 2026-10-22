# Arquitetura — CineSenac

**Versão:** 0.1.0
**Última atualização:** 2026-10-22
**Status:** Rascunho para validação pelo [@architect](../../.github/agents/architect.agent.md)

**Relacionado:** [requisitos funcionais](../requisitos-funcionais.md) · [requisitos não funcionais](../requisitos-nao-funcionais.md) · [modelagens](../modelagem/README.md) · [ADRs](adr/README.md)

---

## 1. Objetivo e escopo

Este documento descreve a arquitetura do CineSenac: o estilo adotado, as táticas que atendem aos requisitos não funcionais e as decisões registradas em ADRs.

O documento é **agnóstico de tecnologia**. Ele define responsabilidades, comunicação e táticas. A escolha de linguagem, framework, banco e provedor pertence às ADRs de aceite, e ainda não foi feita.

**Fora do escopo:** pagamento. Os requisitos funcionais registram o valor do ingresso, mas não definem cobrança. Se a cobrança entrar, é preciso um novo conjunto de RFs e ADRs.

---

## 2. Drivers arquiteturais

Os requisitos abaixo são os que mais influenciam a arquitetura. Os demais RNFs são atendidos pelas mesmas táticas ou por táticas transversais.

| ID | Atributo | Cenário (estímulo → resposta → medida) | RNFs | ADRs |
|---|---|---|---|---|
| ASR-01 | Adequação funcional | Dois clientes reservam o mesmo assento ou sessões sobrepostas ao mesmo tempo → apenas um pedido é gravado, o outro recebe 409 → 0 assentos duplicados e 0 sobreposições em C3 e C6. | RNF01, RNF02, RNF04, RNF25 | 0003, 0004, 0005 |
| ASR-02 | Desempenho | 10.000 usuários virtuais (cerca de 2.500 req/s) navegando e reservando → resposta às leituras e escritas dentro das metas → p95 de leitura ≤ 300 ms, p95 de escrita ≤ 800 ms, erro 5xx < 0,5%. | RNF06, RNF07, RNF08, RNF14 | 0007, 0008, 0009, 0018 |
| ASR-03 | Desempenho e usabilidade no frontend | Visitante em rede móvel 4G abre a vitrine → a programação aparece e a página fica estável → LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1. | RNF09, RNF10, RNF11, RNF12, RNF13 | 0008, 0017, 0018 |
| ASR-04 | Confiabilidade | Falha de uma instância ou sobrecarga → o serviço continua disponível, reservas confirmadas não se perdem e o usuário recebe resposta útil → disponibilidade ≥ 99,5%, 0 reservas perdidas, 503 com `Retry-After`. | RNF23, RNF24, RNF26, RNF27 | 0006, 0009, 0010, 0011 |
| ASR-05 | Segurança e privacidade | Tentativa de força bruta, acesso a cadastro alheio ou entrada maliciosa → a requisição é recusada e fica registrada → 0 acessos indevidos, 0 senhas em texto claro, trilha completa de ações administrativas. | RNF28 a RNF33 | 0010, 0012, 0013, 0014, 0015 |
| ASR-06 | Manutenibilidade e portabilidade | Mudança de regra de negócio ou de ambiente → a regra é testada sem a interface, e o mesmo artefato roda em teste e produção → cobertura ≥ 80% das regras e artefato promovido sem alteração. | RNF34 a RNF41 | 0001, 0002, 0016, 0019, 0020 |

---

## 3. Contexto do sistema

```
  Visitante ──┐
  Cliente ────┤
  Gestor ─────┼──▶  CineSenac  ──▶  Origem de imagens de cartaz
  Admin ──────┘     (URL informada no cadastro do filme; sem integração de API)
```

- **Atores:** Visitante, Cliente, Gestor e Admin, conforme as [personas](../personas/). Visitante não tem arquivo de persona próprio (pendência em [requisitos não funcionais](../requisitos-nao-funcionais.md)).
- **Sistemas externos:** nenhum serviço de integração. Imagens de cartaz são URLs públicas e são carregadas pelo navegador.

---

## 4. Estilo arquitetural e visão de módulos

**Estilo:** monólito modular em camadas, com uma única unidade de implantação para a API (ADR-0001). A borda, o frontend e o banco são unidades separadas.

**Módulos da aplicação**, de acordo com o [diagrama de componentes](../modelagem/estatica/componentes.md):

| Módulo | Responsabilidade | Dependências |
|---|---|---|
| Identidade | Login, sessão e verificação de credenciais. | Armazenamento de sessão |
| Autorização | Perfil, permissões e titularidade, aplicados antes de cada caso de uso. | Identidade |
| Cadastro de clientes | Criação, edição e consulta do próprio cadastro. | Autorização, Dados |
| Catálogo | Filmes e salas. | Autorização, Dados |
| Programação | Sessões, sobreposição na sala (RF15) e cota nacional (RN04). | Catálogo, Dados |
| Reservas | Seleção, reserva atômica e idempotente, conflito de horário do cliente. | Programação, Dados |
| Administração | Contas, permissões e cancelamento de reservas. | Autorização, Auditoria |
| Auditoria | Registro de ações administrativas, na mesma transação. | Dados |

**Regra de dependência:** a camada de apresentação chama a aplicação, que chama o domínio e a persistência. O domínio não depende de HTTP nem de banco (ADR-0001).

---

## 5. Visão de execução

Os fluxos de execução estão em [modelagem dinâmica](../modelagem/dinamica/README.md), com um diagrama por RF. Os fluxos mais sensíveis para a arquitetura são:

| Fluxo | Diagrama | Por que é sensível |
|---|---|---|
| Sobreposição de sessões | [RF15](../modelagem/dinamica/RF15-sobreposicao-sessao.md) | Bloqueio por sala serializa a verificação de intervalo (ADR-0004). |
| Registro de reserva | [RF22](../modelagem/dinamica/RF22-registro-reserva.md) | Idempotência, transação e restrição única convergem aqui (ADR-0003, ADR-0005, ADR-0006). |
| Conflito de horário do cliente | [RF24](../modelagem/dinamica/RF24-conflito-horario-cliente.md) | Bloqueio por cliente, em paralelo com outras reservas do mesmo cliente (ADR-0004). |
| Mapa de assentos | [RF20](../modelagem/dinamica/RF20-mapa-assentos.md) | O mapa não passa pelo cache de programação (ADR-0007, ADR-0018). |
| Programação pública | [RF03](../modelagem/dinamica/RF03-consulta-publica-programacao.md) | Leitura pela borda e cache, com degradação controlada (ADR-0007, ADR-0008, ADR-0010). |

---

## 6. Visão de implantação (agnóstica)

| Unidade | Papel | Estado | ADRs |
|---|---|---|---|
| Frontend | Páginas públicas pré-renderizadas e áreas autenticadas por rota. | Nenhum | 0017 |
| Distribuição de conteúdo | Estáticos, imagens de cartaz e programação pública com TTL. | Cache apenas | 0008 |
| Ponto de entrada e balanceador | HTTPS, limitação de taxa e distribuição entre instâncias. | Nenhum | 0010 |
| Instâncias da API | Casos de uso, em número definido por teste de carga. | **Nenhum entre requisições** | 0009 |
| Armazenamento de sessão | Sessão compartilhada entre instâncias, se não for token assinado. | Sessões | 0009, 0012 |
| Cache de leitura | Programação pública. Nunca mapa nem reservas. | Cache | 0007 |
| Banco relacional | Estado de negócio, com réplica de disponibilidade e backup. | **Estado de negócio** | 0003, 0011 |
| Observabilidade | Métricas, logs e alertas por rota. | Dados de monitoramento | 0020 |

Todas as unidades de aplicação são empacotadas em contêineres com configuração externa (ADR-0019).

---

## 7. Táticas por atributo de qualidade

| Atributo | Tática | ADR |
|---|---|---|
| Modificabilidade | Encapsular as regras em camadas de domínio | 0001 |
| Modificabilidade | Manter a interface estável com contrato versionado | 0002 |
| Modificabilidade | Migrações de esquema versionadas | 0016 |
| Integridade | Impor restrições de unicidade no armazenamento | 0003 |
| Integridade | Bloquear o recurso que governa a regra de intervalo | 0004 |
| Integridade | Transação atômica por comando de escrita | 0005 |
| Confiabilidade | Idempotência por chave de requisição | 0006 |
| Confiabilidade | Redundância e recuperação por backup testado | 0011 |
| Desempenho | Manter cópias de leitura com TTL (cache) | 0007 |
| Desempenho | Replicar na borda (distribuição de conteúdo) | 0008 |
| Desempenho | Escalonamento horizontal sem estado e balanceamento de carga | 0009 |
| Desempenho | Pré-renderizar páginas públicas e dividir o código por rota | 0017 |
| Desempenho | Revalidar sob demanda em vez de atualizar continuamente | 0018 |
| Disponibilidade | Limitar a taxa de requisições e degradar com 503 | 0010 |
| Segurança | Autenticar com sessão em cookie seguro e hash adaptativo | 0012 |
| Segurança | Autorizar por perfil e titularidade no servidor | 0013 |
| Segurança | Validar e sanear a entrada no servidor | 0014 |
| Segurança | Manter trilha de auditoria na mesma transação | 0015 |
| Portabilidade | Empacotar em contêineres com configuração externa | 0019 |
| Monitoramento | Observabilidade por rota com métricas e logs estruturados | 0020 |

---

## 8. Trade-offs principais

| Decisão | Ganho | Custo aceito | ADR |
|---|---|---|---|
| Monólito modular | Simplicidade de implantação e de transação | Escala apenas no nível da aplicação inteira | 0001 |
| Bloqueio por sala e por cliente | Correção de intervalos | Serialização de operações da mesma sala | 0004 |
| Cache de 30 s na programação | Carga de leitura absorvida fora do banco | Mudança de programação visível com até 30 s de atraso | 0007 |
| Sem polling no mapa | Cerca de 80% de carga evitada | Cliente pode ver assento livre até revalidar | 0018 |
| Sessão em cookie, não no navegador | Menor superfície de roubo de credencial | Proteção contra CSRF e fluxo de renovação | 0012 |
| Idempotência com armazenamento de chaves | Reenvio seguro | Armazenamento e limpeza de chaves | 0006 |

---

## 9. Riscos e pendências

1. **ADRs em proposta:** todas as 21 estão com status "Proposta" e aguardam aceite do [@architect](../../.github/agents/architect.agent.md). O [ADR-0007](adr/ADR-0007-cache-de-leitura-com-ttl.md) tem um achado de implementação que pede decisão sobre invalidação do cache.
2. **Entidades faltantes:** Usuario, Perfil, Permissao e RegistroAuditoria não estão no [DBML](../dbdiagram.dbml). Sustentam RF01, RF02, RF27, RF28 e RNF33.
3. **Parâmetros a definir:** prazo de sessão (ADR-0012), N tentativas de login (ADR-0010), limites de taxa e de capacidade após teste de carga (ADR-0010), RPO e RTO (ADR-0011), retenção de chaves de idempotência (ADR-0006), retenção da auditoria (ADR-0015) e limite de assentos por pedido (ADR-0005).
4. **Aceitabilidade do TTL:** confirmar com o produto se 30 s de defasagem na programação pública é aceitável (ADR-0007).
5. **Escolhas concretas de tecnologia:** a implementação inicial usa Python, FastAPI, Jinja2, SQLAlchemy e SQLite, registrados na [ADR-0021](adr/ADR-0021-stack-de-implementacao-inicial.md) (proposta). Provedor e gerenciador de segredos ainda não foram escolhidos.
6. **Persona Visitante:** sem arquivo próprio em [personas](../personas/).

---

## 10. Índice de ADRs

As decisões estão em [adr/](adr/README.md). Cada ADR registra a tática, os RNFs e RFs atendidos, o contexto, a decisão, as alternativas, as consequências e os documentos relacionados.
