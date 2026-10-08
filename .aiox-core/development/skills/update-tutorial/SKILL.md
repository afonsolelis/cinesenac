---
name: update-tutorial
description: >
  Keep tutorial.md in sync with the project history — add a new step with the
  user's prompt and the artifact produced after every task that creates or
  changes documented artifacts (README, PRD, personas, DBML, skills).
  Use when: "atualize o tutorial", after finishing a task that changed the
  project structure or docs, or before closing any session that produced new
  steps worth recording.
user-invocable: true
---

# update-tutorial

Lean skill. `tutorial.md` is the living history of how the project was built,
step by step, with the user's prompts.

## Steps

1. Read `tutorial.md` and identify the last recorded step number.
2. Append the new step in the established format:

   ```markdown
   ## Passo N — <short title>

   ### Prompt

   > "<the user's prompt, verbatim>"

   ### Resultado

   - <what was created/changed, with file paths>

   **Aprendizado:** <lesson, only when there is a clear one>
   ```

3. Update the "Estrutura final gerada" tree so it matches the disk.
4. Update "Próximos passos sugeridos" — check off items that are done.
5. Run the `analyze-docs` skill before finishing (links, fences, consistency).

## Forbidden

- Inventing or rephrasing the user's prompts — quote them verbatim
- Reordering or deleting existing steps
- Recording steps for trivial corrections that add no history value (use
  judgment: structural changes and new artifacts are worth a step; a one-word
  typo fix usually is not)
