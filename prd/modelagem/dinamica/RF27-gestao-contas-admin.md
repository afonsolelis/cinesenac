# RF27 — Gestão de contas pelo Admin

**Requisito:** o Admin cria, edita, ativa/desativa e exclui contas de Gestores e Clientes.
**Personas:** Admin.
**RNFs realizados:** [RNF26](../../requisitos-nao-funcionais.md) (durabilidade), [RNF28](../../requisitos-nao-funcionais.md) (senhas e sessão), [RNF29](../../requisitos-nao-funcionais.md) (autorização), [RNF32](../../requisitos-nao-funcionais.md) (LGPD), [RNF33](../../requisitos-nao-funcionais.md) (auditoria).
**Entidades:** Usuario, Perfil, Cliente, RegistroAuditoria ([classes](../estatica/classes.md)). Usuario e RegistroAuditoria são **pendentes**.

## Diagrama de sequência

```mermaid
sequenceDiagram
    actor A as Admin
    participant FE as Frontend
    participant API as API
    participant AUTZ as Autorização
    participant DB as Banco relacional
    participant AUD as Auditoria

    A->>FE: Abre gestão de usuários
    FE->>API: GET /usuarios
    API->>AUTZ: Confirma perfil Admin
    alt Perfil sem permissão
        AUTZ-->>API: Negado
        API-->>FE: 403 Sem permissão
    else Perfil Admin
        API->>DB: Lista Gestores e Clientes
        DB-->>API: Contas
        API-->>FE: 200 Lista de contas
        FE-->>A: Exibe a lista

        A->>FE: Cria, edita, ativa, desativa ou exclui conta
        FE->>API: POST, PATCH ou DELETE /usuarios/{id}
        API->>AUTZ: Confirma perfil Admin
        API->>DB: Aplica a alteração em transação
        alt Desativação ou exclusão
            API->>DB: Encerra sessões ativas da conta
        end
        DB-->>API: Alteração confirmada
        API->>AUD: Registra ação, autor, alvo e data
        API-->>FE: 200 Conta atualizada
        FE-->>A: Atualiza a lista
    end
```

## Notas de RNF

- **RNF28:** desativar ou excluir conta encerra as sessões dela. Quem foi desativado não continua logado.
- **RNF29:** a rota exige perfil Admin no servidor.
- **RNF33:** toda alteração gera registro de auditoria com autor, ação, alvo e data.
- **RNF32:** exclusão de cliente tem de seguir a política de exclusão de dados pessoais, ainda a definir.
- **Pendência:** a entidade Usuario não está no DBML. Ver [classes.md](../estatica/classes.md).
- **RNF26:** criação, edição, desativação e exclusão são gravadas em transação. Uma queda no meio não deixa conta em estado parcial.
