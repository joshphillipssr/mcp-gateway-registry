## Summary

Describe what changed and why.

## Scope

- Upstream target intent: `<yes/no>`
- Fork-only customization intent: `<yes/no>`

## Validation

- [ ] `./credentials-provider/generate_creds.sh`
- [ ] `./tests/run_all_tests.sh --skip-production`
- [ ] `./tests/run_all_tests.sh` (required for merge-ready changes)

## Checklist

- [ ] Change is focused and avoids unrelated refactors.
- [ ] Commit message and PR text are clear and professional.
- [ ] Security-sensitive changes follow project guidance (`CONTRIBUTING.md`, `CLAUDE.md`, `docs/llms.txt`).
- [ ] If this PR introduces fork-only divergence, `customizations.md` is updated in the same PR.
- [ ] If this PR is intended for upstream, fork-only customizations are excluded.
