---
name: analyze-docs
description: >
  Documentation review gate — analyze and validate all project docs (README,
  PRD, markdown, Mermaid, DBML) before finishing any task that created or
  edited them. Use when: finishing a documentation task, "analise a
  documentação", before wrapping up any change to .md/.dbml files, or when
  asked to review docs.
user-invocable: true
---

# analyze-docs

Lean documentation gate. Run **before finishing** any task that created or
modified documentation files.

## Scope

Every `.md` and `.dbml` file touched in the task, plus the project `README.md`.

## Protocol

1. **Links** — resolve every relative link in the touched docs and in README;
   targets must exist on disk.
2. **Code blocks** — every fenced block is closed (balanced ``` fences) and
   language-tagged. Validate syntax per type:
   - **Mermaid** — no `;` inside diagram lines (Mermaid treats it as a
     statement separator and breaks rendering); balanced `alt/else/end` and
     `opt/end`; participants declared before use.
   - **DBML** — tables/enums/refs balanced; referenced tables exist.
3. **Consistency** — identifiers (RNxx, RFxx, story ids), entity/table names
   and persona names match across all docs.
4. **Structure** — heading hierarchy is coherent, tables are well-formed, and
   the project tree in README matches the actual disk layout.
5. **Language** — spelling and grammar in the document's language.
6. **Report** — deliver a short analysis to the user: issues found, fixes
   applied, and anything requiring a user decision.

## Post-phase verification

- [ ] All relative links resolve
- [ ] All fenced blocks render (no stray `;` in Mermaid, fences balanced)
- [ ] README structure/roadmap in sync with disk
- [ ] Analysis report delivered

## Forbidden

- Declaring docs "done" with broken links or non-rendering Mermaid
- Silently changing meaning while fixing grammar/typos
