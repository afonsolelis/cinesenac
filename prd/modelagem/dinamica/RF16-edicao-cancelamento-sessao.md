# RF16 — Edição e cancelamento de sessão

**Requisito:** editar e cancelar sessões.
**Personas:** Gestor, Admin.
**RNFs realizados:** [RNF04](../../requisitos-nao-funcionais.md) (sem sobreposição na alteração de horário), [RNF29](../../requisitos-nao-funcionais.md) (autorização), [RNF33](../../requisitos-nao-funcionais.md) (auditoria do cancelamento).
**Entidades:** Sessao, Reserva, RegistroAuditoria ([classes](../estatica/classes.md)).

## Diagrama de sequência

O cancelamento de sessão com reservas já feitas ainda não tem regra definida. O diagrama marca esse ponto como **a definir**.

```mermaid
sequenceDiagram
    actor G as Gestor
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional
    participant AUD as Auditoria

    G->>FE: Altera horário, duração ou valor, ou cancela
    FE->>API: PATCH /sessoes/{id} ou POST /sessoes/{id}/cancelamento
    API->>AUTZ: Confirma perfil Gestor ou Admin
    alt Perfil sem permissão
        AUTZ-->>API: Negado
        API-->>FE: 403 Sem permissão
    else Perfil autorizado
        alt Alteração de horário
            API->>API: Executa verificação de sobreposição (RF15)
            API->>DB: Atualiza sessão
            DB-->>API: Sessão atualizada
            API-->>FE: 200 Sessão atualizada
        else Alteração de dados sem horário
            API->>DB: Atualiza sessão
            API-->>FE: 200 Sessão atualizada
        else Cancelamento
            API->>DB: Consulta reservas da sessão
            DB-->>API: Quantidade de reservas
            Note over API,DB: Regra a definir para reservas existentes
            API->>DB: Marca sessão como cancelada
            API->>AUD: Registra cancelamento com autor, alvo e data
            API-->>FE: 200 Sessão cancelada
        end
        FE-->>G: Atualiza o calendário
    end
```

## Notas de RNF

- **RNF04:** qualquer mudança de horário passa de novo pela verificação de sobreposição de [RF15](RF15-sobreposicao-sessao.md).
- **RNF29:** a checagem de perfil acontece no servidor.
- **RNF33:** o cancelamento grava registro de auditoria com autor, alvo, ação e data.
- **Pendência:** definir o tratamento de reservas de uma sessão cancelada, que afeta [RF30](RF30-cancelamento-reserva-admin.md).
