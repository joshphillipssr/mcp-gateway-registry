# Customizations Ledger

This file tracks all intentional divergence between fork `production` and upstream `main`.

Purpose:
- Preserve a clear record of fork-only behavior.
- Keep upstream PRs focused on upstream-eligible fixes/features.
- Reduce rework during upstream sync and conflict resolution.

## Update Rules

1. Add or update an entry in the same commit/PR that introduces the customization.
2. Mark `Upstream Eligible` as `Yes`, `No`, or `Partial`.
3. If `Partial`, describe exactly what subset is safe for upstream.
4. When upstream accepts a change, set status to `Merged Upstream` and include PR link.
5. When a customization is removed, set status to `Retired` and reference the removing commit.

## Current Customizations

| ID | Status | Area | Summary | Key Paths | Upstream Eligible | Notes |
|---|---|---|---|---|---|---|
| CUST-001 | Active | Branding | Rebrand platform naming to `JoshSr.AI Unified Agentic Integration Platform (UAIP)` in fork-owned docs/messaging. | `README.md`, docs where UAIP appears | No | Fork identity decision; keep out of upstream PRs unless upstream requests it. |
| CUST-002 | Active | Branch Workflow | Maintain dual-branch model: `main` mirrors upstream, `production` carries operational customizations. | Branch policy/process | No | Use `main` for upstream PR branches; never submit upstream PRs from `production`. |

## Candidate Queue (Optional)

Use this section for potential upstream contributions discovered while implementing fork customizations.

| Candidate ID | Source Customization | Proposed Upstream Change | Status | Link |
|---|---|---|---|---|
| (add as needed) |  |  |  |  |
