# Code Consolidation Reviews

Periodic reviews to ensure code hygiene after significant changes.

## When to trigger
- After ~30+ commits since the last review
- Before a major release
- After large feature work or dependency upgrades
- If it's been 6+ weeks since the last review

## Scope
All source code, tests, build configuration, CI/CD, and project metadata.

## Review Checklist

**Correctness & safety (review first):**
1. **Security** — input validation gaps, credential handling, OWASP patterns
2. **Error handling** — inconsistent patterns, swallowed exceptions, missing
   user-facing messages
3. **Robustness** — race conditions, resource leaks, missing cleanup
4. **Compatibility** — CLI argument/flag changes, config schema changes,
   cache/data format migration, breaking changes to public interfaces

**Code quality:**
5. **Dead code** — unused functions, classes, modules, imports, config keys
6. **Dead/stale dependencies** — unused libraries, outdated packages with
   known CVEs, license concerns, or unmaintained status
7. **Duplication** — repeated or near-identical logic that should be shared
8. **Naming & consistency** — mixed conventions, unclear names, stale comments
9. **Type safety** — missing annotations, `Any` overuse, type errors

**Testing & docs:**
10. **Test gaps** — untested code paths, stale tests, missing edge cases
11. **Documentation drift** — specs, docstrings, or README sections that no
    longer match the code

**Efficiency:**
12. **Performance** — unnecessary work, avoidable allocations, slow patterns
13. **Build & packaging** — PyInstaller reproducibility, unnecessary bundled
    files, exe size regression

**Hygiene:**
14. **TODO/FIXME/HACK audit** — resolve or remove stale markers
15. **Log quality** — actionable error messages for both GUI and CLI users

## Deliverable
A review document in `docs/` named `Code-Review-YYYY-MM.md` containing:

- **Regression check**: compare against previous review — note any deferred
  items that are still relevant, and any previously-fixed issues that
  have regressed
- **Summary table**: each finding with Category, Description, Action
  (Remove/Refactor/Replace/Add), Impact (High/Med/Low), Effort (H/M/L),
  Risk (H/M/L)
- **Detailed findings**: grouped by category, ordered by impact descending
  then effort ascending within each group. Each finding must include:
  - Evidence (file path + line, or command to reproduce)
  - Recommendation (specific action to take)
- **Out of scope**: new feature ideas or large refactors that belong in
  `TODO.md`. Criteria: if it adds new user-facing functionality or would
  take more than ~1 hour, it's out of scope for the review.

## Finding statuses
Each finding gets one of these statuses during triage:
- **Implement** — approved, will be done in this cycle
- **Defer** — valid but low priority; carry forward to next review
- **Reject** — investigated, no action needed (include rationale to
  prevent re-raising in future reviews)
- **Out of scope** — belongs in `TODO.md`, not this review

## Process
1. **Discovery** — produce the review document; do NOT implement changes
2. **Triage** — review findings with the user, assign statuses
3. **Implementation** — implement approved items in focused commits, one
   logical change each; re-run tests and linting after each change
4. **Verification** — run full test suite + lint + build smoke test;
   update the review doc's summary table with final statuses
