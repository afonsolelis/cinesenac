# Modelagens — CineSenac

Este diretório reúne os modelos do sistema, separados em duas visões:

| Pasta | Visão | Conteúdo |
|---|---|---|
| [estatica/](estatica/) | Estrutura | Componentes e classes de entidades. Não muda com o tempo de execução. |
| [dinamica/](dinamica/) | Comportamento | Um diagrama de sequência por requisito funcional (RF01 a RF30). |

## Estática

- [componentes.md](estatica/componentes.md): diagrama de componentes agnóstico de tecnologia, com responsabilidades e interfaces.
- [classes.md](estatica/classes.md): diagrama de classes das entidades, com restrições de unicidade e mapeamento para o DBML.

## Dinâmica

Cada RF tem um arquivo próprio com o diagrama de sequência em Mermaid, as personas envolvidas, os RNFs que o diagrama realiza e as entidades usadas. O índice completo está em [dinamica/README.md](dinamica/README.md).

## Relação com os demais documentos

- Requisitos funcionais: [requisitos-funcionais.md](../requisitos-funcionais.md)
- Requisitos não funcionais: [requisitos-nao-funcionais.md](../requisitos-nao-funcionais.md)
- Personas: [personas](../personas/)
- Fluxos já documentados (visão resumida): [fluxos-sequencia.md](../fluxos-sequencia.md)
- Modelo de dados atual: [dbdiagram.dbml](../dbdiagram.dbml)

## Convenções

- Nomes de componentes e entidades seguem o vocabulário de [requisitos-funcionais.md](../requisitos-funcionais.md).
- Os diagramas são agnósticos de tecnologia. Escolhas de implementação ficam em decisões de arquitetura.
- Entidades pendentes são marcadas explicitamente, e não aparecem como definitivas.
