# Repository instructions

## Commit behavior

After completing a requested implementation task:

1. Run the relevant verification commands.
2. If tests pass and the working tree contains only expected changes, create a git commit automatically.
3. Use a clear Conventional Commit style message:
   - `fix: ...`
   - `feat: ...`
   - `docs: ...`
   - `test: ...`
   - `chore: ...`
4. Do not push unless I explicitly ask for push.
5. Do not create or move tags unless I explicitly ask.
6. If tests fail, do not commit. Report the failure.
7. If git status shows unexpected or unrelated files, do not commit. Report them first.
8. Always include the commit hash in the final report.

Default verification before commit:

- `python -m pytest`

For docs-only changes:

- Run a lightweight sanity check if relevant.
- Commit if no code behavior is affected.
