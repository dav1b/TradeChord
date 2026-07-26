# Repository improvement plan

This plan records the July 2026 repository review and the changes made from it.
The goal is to keep the brand kit opinionated while making it reproducible,
self-validating, and independent of any one coding agent.

## 1. Make examples truthful and self-validating

Problem:

- The README said `carousel/briefs/` contained only the example, but four
  project-specific briefs were also committed.
- `example-brief.yaml` used an obsolete string hook and failed the current
  validator.

Changes:

- Keep only one generic, valid brief in `carousel/briefs/`.
- Validate every bundled brief in automated tests and CI.
- Add `--validate-only` so briefs can be checked without Chrome.

Acceptance criteria:

- `python3 carousel/generate.py carousel/briefs/example-brief.yaml --validate-only`
  succeeds.
- The test suite fails if a bundled brief stops matching the schema.

## 2. Use a repo-only integration model

Problem:

- The README called Git subtree the canonical integration method while
  `install.sh` still copied files and mutated consuming projects.
- Claude-specific templates made the brand kit look tied to one agent.

Changes:

- Remove `install.sh` and the generated-agent templates.
- Treat this repository as the complete canonical artifact.
- Document Git subtree as the default integration, with clone/submodule as
  alternatives where independent history is preferred.
- Keep consumer-specific CSS imports, font publication, and agent instructions
  in the consuming repository.

Acceptance criteria:

- No setup script copies or synchronizes this repository.
- Updates flow through Git.
- No required workflow depends on Claude Code.

## 3. Make dependencies and generated files explicit

Problem:

- PyYAML was required but not declared.
- Root-level generated files and Python caches were not ignored.

Changes:

- Add `requirements.txt` for runtime dependencies.
- Add `requirements-dev.txt` for test/render inspection dependencies.
- Add a root `.gitignore` for generated PDFs, temporary render pages, caches,
  and local environments.

Acceptance criteria:

- A new environment can install declared dependencies and run the test suite.
- Normal generator output does not appear in `git status`.

## 4. Document licensing rather than guessing it

Problem:

- The repository and bundled fonts had no licensing statement.
- PP Neue Machina is a commercial typeface and its redistribution rights cannot
  be inferred from the font file alone.

Changes:

- Add `LICENSES.md` describing the current licensing status and the evidence
  required before public redistribution.
- Do not assign a repository-wide open-source license without owner approval.
- Require the commercial font licence or replace the file before distributing
  the kit outside its authorised organisation.

Acceptance criteria:

- Consumers are not led to assume that “present in Git” means “licensed for
  arbitrary redistribution.”

## 5. Add automated checks and CI

Problem:

- No tests or CI protected the validator, examples, output naming, or render
  path.

Changes:

- Add standard-library unit tests for validation, naming, and safe template
  injection.
- Add a render smoke test that creates a PDF and verifies its page count and
  portrait dimensions.
- Run validation and unit tests on every push and pull request.
- Run the Chrome-backed render smoke test in CI.

Acceptance criteria:

- `python3 -m unittest discover -s tests -v` succeeds.
- `python3 tests/render_smoke.py` succeeds where Chrome is installed.

## 6. Make renderer cleanup failure-safe

Problem:

- The generator created a temporary HTML file before locating Chrome.
- Errors or interrupts could leave build files behind.
- Raw JSON embedded in a `<script>` element could terminate that element if a
  brief contained `</script>`.

Changes:

- Locate Chrome before writing the build page.
- Use `try/finally` cleanup.
- Escape script-closing characters in injected JSON.
- Use a slugified temporary filename.

Acceptance criteria:

- Failed renders do not leave `.build-*.html` behind unless `--keep-html` was
  explicitly requested.
- Brief text cannot close the bootstrap `<script>` element.

## Deferred decisions

- Choose a repository-wide licence. This requires the copyright holder.
- Add pixel-baseline visual regression after a representative output is
  approved as the canonical baseline. The current smoke test verifies rendering,
  pagination, and canvas geometry but deliberately does not bless today’s pixels.
- Consider splitting global CSS resets from tokens before importing the kit into
  established applications.
- Decide whether root-relative `/fonts/...` URLs remain the supported web
  contract or should become a consumer-configurable layer.

