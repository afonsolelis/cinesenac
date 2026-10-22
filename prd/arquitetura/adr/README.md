# Registro de Decisões Arquiteturais (ADRs) — CineSenac

Cada ADR registra uma tática arquitetural: o problema, a decisão, as alternativas e as consequências. As decisões ligam-se aos RNFs e aos RFs do projeto. Documento geral: [arquitetura.md](../arquitetura.md).

## Processo

1. Nova ADR nasce com status **Proposta**, numerada em sequência (`ADR-NNNN-slug.md`).
2. O [@architect](../../../.github/agents/architect.agent.md) revisa e registra o aceite, mudando o status para **Aceita**.
3. Quando uma decisão for substituída, a ADR antiga recebe status **Substituída** e aponta para a nova. Nenhuma ADR aceita é reescrita para mudar a decisão.

Status possíveis: **Proposta**, **Aceita**, **Substituída**.

## Índice

| ADR | Decisão | Tática arquitetural | RNFs | Status |
|---|---|---|---|---|
| [ADR-0001](ADR-0001-estilo-monolito-modular-em-camadas.md) | Estilo monólito modular em camadas com regras de negócio isoladas | Modificabilidade: encapsular e separar responsabilidades em camadas | RNF34, RNF37, RNF35 | Proposta |
| [ADR-0002](ADR-0002-contrato-api-versionado.md) | Contrato de API versionado e documentado | Modificabilidade: manter a interface estável (versionamento e fachada de contrato) | RNF17, RNF15, RNF16 | Proposta |
| [ADR-0003](ADR-0003-unicidade-garantida-pelo-armazenamento.md) | Unicidade garantida por restrição no armazenamento | Integridade: impor restrições no armazenamento (enforce constraints) | RNF01, RNF03, RNF41 | Proposta |
| [ADR-0004](ADR-0004-bloqueio-por-recurso-de-dominio.md) | Bloqueio por recurso de domínio para sobreposição de intervalos | Concorrência: controlar o acesso a recursos com bloqueio (locking) por sala e por cliente | RNF02, RNF04, RNF34 | Proposta |
| [ADR-0005](ADR-0005-transacao-curta-por-comando.md) | Transação curta por comando de escrita | Integridade: transação atômica com confirmação ou desfazimento (commit e rollback) | RNF25, RNF26, RNF07 | Proposta |
| [ADR-0006](ADR-0006-idempotencia-de-reserva.md) | Idempotência do comando de reserva por chave de requisição | Confiabilidade: reexecução segura (idempotência) | RNF24, RNF07, RNF23 | Proposta |
| [ADR-0007](ADR-0007-cache-de-leitura-com-ttl.md) | Cache de leitura da programação pública com TTL curto | Desempenho: manter cópias dos dados de leitura (caching) | RNF06, RNF08, RNF14 | Proposta |
| [ADR-0008](ADR-0008-distribuicao-de-conteudo-na-borda.md) | Distribuição de conteúdo estático e de leitura pública na borda | Desempenho: replicar recursos próximos ao usuário (distribuição de conteúdo) | RNF09, RNF13, RNF14 | Proposta |
| [ADR-0009](ADR-0009-escalonamento-horizontal-sem-estado.md) | Escalonamento horizontal com instâncias da API sem estado | Desempenho: introduzir concorrência e replicar o recurso de processamento (escalonamento horizontal, balanceamento de carga) | RNF08, RNF23, RNF36 | Proposta |
| [ADR-0010](ADR-0010-limitacao-de-taxa-e-degradacao-controlada.md) | Limitação de taxa e degradação controlada acima da capacidade | Disponibilidade: limitar a resposta a eventos (limitação de taxa e controle de admissão) | RNF27, RNF30, RNF08 | Proposta |
| [ADR-0011](ADR-0011-redundancia-e-recuperacao-de-dados.md) | Redundância do banco e recuperação por backup testado | Disponibilidade: redundância ativa e recuperação por backup (recover: restore) | RNF23, RNF26 | Proposta |
| [ADR-0012](ADR-0012-autenticacao-com-sessao-segura.md) | Autenticação com sessão em cookie seguro e hash adaptativo de senha | Segurança: autenticar atores (verificação de credenciais e gestão de sessão) | RNF28, RNF30, RNF31 | Proposta |
| [ADR-0013](ADR-0013-autorizacao-por-perfil-no-servidor.md) | Autorização por perfil e titularidade verificada no servidor | Segurança: autorizar atores (checagem centralizada de permissão) | RNF29, RNF32, RNF33 | Proposta |
| [ADR-0014](ADR-0014-validacao-e-saneamento-de-entrada.md) | Validação e saneamento de entrada no servidor | Segurança: limitar a exposição e validar entrada (validate input, encode output) | RNF31, RNF22, RNF03 | Proposta |
| [ADR-0015](ADR-0015-trilha-de-auditoria.md) | Trilha de auditoria gravada na mesma transação da ação administrativa | Segurança: manter trilha de auditoria (audit trail) | RNF33, RNF32 | Proposta |
| [ADR-0016](ADR-0016-migracoes-de-esquema-versionadas.md) | Mudanças de esquema por migrações versionadas e reproduzíveis | Manutenibilidade: reduzir o acoplamento entre código e esquema (migrações versionadas) | RNF41, RNF36, RNF39 | Proposta |
| [ADR-0017](ADR-0017-pre-renderizacao-de-paginas-publicas.md) | Pré-renderização das páginas públicas e aplicação por rota para áreas autenticadas | Desempenho do frontend: pré-renderização e divisão de código por rota | RNF09, RNF11, RNF12, RNF14, RNF15, RNF16 | Proposta |
| [ADR-0018](ADR-0018-revalidacao-do-mapa-sob-demanda.md) | Revalidação do mapa de assentos sob demanda, sem polling | Desempenho e integridade: revalidar sob demanda em vez de atualizar continuamente | RNF01, RNF06, RNF08, RNF20 | Proposta |
| [ADR-0019](ADR-0019-conteineres-e-configuracao-externa.md) | Empacotamento em contêineres e configuração externa ao artefato | Portabilidade: isolar a dependência de ambiente (contêineres e configuração externa) | RNF39, RNF40, RNF36 | Proposta |
| [ADR-0020](ADR-0020-observabilidade-por-rota.md) | Observabilidade por rota com métricas, logs estruturados e rastreamento | Monitoramento: detectar e diagnosticar falhas (monitor e registro de eventos) | RNF38, RNF36, RNF23 | Proposta |
| [ADR-0021](ADR-0021-stack-de-implementacao-inicial.md) | Stack de implementação inicial em Python | Escolha de tecnologia que materializa as ADRs 0001 a 0020, sem contrariá-las | RNF35, RNF39, RNF40 | Proposta |

## Modelo

```markdown
# ADR-NNNN: título da decisão

**Status:** Proposta
**Data:** AAAA-MM-DD
**Tática arquitetural:** atributo e tática
**RNFs:** ...
**RFs:** ...
**Personas:** ...

## Contexto
## Decisão
## Alternativas consideradas
## Consequências
## Relacionados
```

Ao registrar uma decisão, use o mesmo modelo. Um arquivo por decisão, com título que diga o que foi decidido.
