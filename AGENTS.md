# AGENTS.md — Ut99py

Python port of Unreal Tournament 99. Reference C++ source is `~/code/Ut99PubSrc`
(read-only). Each Python module mirrors a C++ header/lib; name the source file it
ports in the module docstring.

## Hard Rules

0. Make surgical changes. Minimize changed lines; leave unrelated code alone.
1. Follow existing conventions. Read the surrounding code before adding
   anything; match layout, naming, error handling, comment style. Don't invent a
   parallel way of doing what the repo already does.
2. Port fidelity: keep 1-to-1 semantics with the C++ when reasonable. If the
   Python must deviate (or the C++ impl lives in a prebuilt `.lib` and only the
   header exists), say so in a comment and cite the source (`Core/Inc/UnMath.h`).
3. Verify claims against the source. Read the header before acting on a
   signature, default, or behavior — never infer from a name.
4. Avoid magic numbers/strings: extract meaningful or recurring values into
   named constants or enums. Keep self-explanatory one-off values inline.
5. Reduce indentation; avoid the arrow anti-pattern. Use early return/continue.
6. Keep function names under 30 chars.
7. Comment what the block does and why; keep it short. No comments on code you
   didn't touch.
8. Terse writing in comments, commit messages, and replies. Drop superlatives
   and praise; state the cold facts.
9. Never leave a stub that silently returns a wrong/default value — mark it
   `raise NotImplementedError` or document the gap.
10. Keep numpy vectorization. Once a function is correct, try a numpy version,
    benchmark both, and keep the faster one. Keep the scalar version only when
    numpy loses or changes semantics — then say why in a comment.
11. Push ifs up, fors down. Decide modes/flags once and bind the result (table,
    bound method, filtered list) — don't re-check per item. Give functions the
    whole batch (numpy) instead of calling per element. Hoist loop-invariant
    work out of loops.

## Code Style

- Type hints on public APIs; Google-style docstrings.
- Prefer `array.array` over lists for homogeneous numeric data.
- Prefer iteration/DP over recursion.
- Hoist `len(data)` out of loops: `n = len(data)` then `while i < n`.

## Testing

- Test first: for a bug fix write the failing test, watch it fail, then fix.
  For a new feature, same order (TDD).
- No retry-until-random-hit loops (`for _ in range(N): if cond: break`). Inject a
  scripted RNG and assert the exact output.
- No hardcoded counts; assert `>=` lower bounds, not `==`.
- A ported function's test should derive expected values from the C++ semantics,
  not echo the Python implementation back.
- Run the tests for the affected code, not the whole suite blindly.

## Workflows

### Finish a task

1. Create a TODO tracking the work.
2. Make the change; every fixed bug ships with a regression test.
3. Run the affected tests; must pass.
4. `ruff format ut99py/` and `ruff check ut99py/`.
5. New source file: run `lizard --CCN=15 <file.py>` and fix warnings.
6. Update docs when a high-level capability changes.
7. `git commit` and `git push`.
