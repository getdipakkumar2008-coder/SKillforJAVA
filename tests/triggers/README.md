# Trigger tests

Do the skill `description`s make an agent load the right skill (and only the right skill)? This folder holds the test cases; `scripts/check-triggers.py` runs them.

## Files
- `cases.json` - 68 natural-language prompts: 61 positive cases (at least 3 for every skill except the core skill, which every Java task may load) and 7 negatives (non-Java prompts, plus one cross-platform mobile case). Each case lists `expect_all`, `expect_any`, `forbid` or `forbid_all`.
- `results/` - output of `claude` runs (git-ignored).

## Case semantics
| Field | Meaning |
|---|---|
| `expect_all` | every listed skill must activate |
| `expect_any` | at least one listed skill must activate (used where two skills are both legitimate, e.g. a slow query may load the database or the performance skill) |
| `forbid` | none of these may activate |
| `forbid_all` | none of this repository's skills may activate (non-Java prompts) |

`java-engineering-core` is always acceptable. Other activations beyond the expected set are printed as `extra=` (possible over-activation) but do not fail a case.

## Commands
```bash
python scripts/check-triggers.py lint                  # offline: cases valid, every skill covered, description overlap report
python scripts/check-triggers.py lexical               # offline heuristic: TF-IDF similarity of prompt vs descriptions
python scripts/check-triggers.py claude --batch 1 --yes   # REAL, 5 cases per batch (14 batches), spends API credits
python scripts/check-triggers.py claude --batch 1 --bootstrap --yes   # same, with adapters/claude/CLAUDE.md in the project
python scripts/check-triggers.py claude --yes          # REAL: all cases, roughly $12-14 and 15-20 minutes
python scripts/check-triggers.py claude --ids core-01,sec-01,neg-01 --yes
python scripts/check-triggers.py claude --yes --jobs 3 --budget 0.30 --model <model>
```

### `lint` (deterministic, free)
Validates the case file (known skills, unique ids, coverage) and lists the most similar description pairs. A pair above the overlap threshold (default 0.45 cosine) is a warning that two descriptions may compete. Currently the highest pair is `hibernate-orm-engineering` ~ `spring-data-jpa-engineering` at 0.35, below the threshold; that boundary is deliberate and its real behaviour should be checked with `claude`.

### `lexical` (offline heuristic)
Ranks skills for each prompt by TF-IDF cosine similarity with the descriptions (within the top 3 and at least 40% of the best score). **This is not how agents choose skills** - it ignores semantics and paraphrase. Use it only as a quick signal that a description lacks the vocabulary a user would use. Failures here are hints, not defects; negative cases are skipped.

### `claude` (real activation)
Creates a scratch project from `tests/triggers/fixture/` (a small Spring Boot Maven project) plus these skills, runs each prompt with `claude -p` (stream-json), and records which skills the agent invoked through the `Skill` tool. By default only `Skill`, `Read`, `Glob` and `Grep` are enabled (`--tools ''` for `Skill` only; `--no-fixture` for an empty project) so the agent can look around but cannot edit or run anything, and project-level settings only are loaded (`--setting-sources project`), so personal skills and memory do not leak in. There is no per-case cost cap by default (`--budget 0`): with a cap the agent skipped skills "to stay within budget" and under-triggered. Use `--budget` only as a safety net, and expect about $0.2-0.5 per case. These sessions also count against your own Claude usage limit; a full run can hit it (a full run was cut off once). Without `--yes` it only prints the plan. Output is saved to `tests/triggers/results/<timestamp>-claude.json`.

Caveats:
- Results depend on the model, the Claude Code version and the other skills installed. Claude Code also bundles generic skills (for example a code-review skill) that can win over `java-code-review`; the case notes say so.
- The fixture is tiny. A real project could change behaviour; `FIXTURE_DIR` in the script can point at a copy of one. (Batch 1 gave identical results with an empty project and with the fixture, so the empty-project worry did not hold for those cases.)
- `--bootstrap` copies `adapters/claude/CLAUDE.md` into the scratch project. With it the agent loads `java-engineering-core` first; without it, generic prompts often load nothing. Test both configurations: description-only measures the descriptions, `--bootstrap` measures the recommended deployment.
- Agent behaviour is non-deterministic; re-run failures before changing a description, and change descriptions based on patterns across several cases, not one miss.
- GitHub Copilot activation is not covered: the harness drives Claude Code only.

## Recommended workflow
1. `lint` after editing descriptions or cases.
2. `claude` on the changed skills' case ids (`--ids`), then the full set before a release.
3. For each repeated miss: add the user's real vocabulary to that skill's description (what the user says, not internal jargon); for repeated over-activation: narrow the description or add an explicit "Not for ..." clause.
4. Record the run (date, model, pass rate, failures) in `docs/validation-report.md`.
