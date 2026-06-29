# Final Artifact Manifest

Last updated: 2026-06-29 UTC.

## Final Zip

```text
CommitBench_final_anonymous_artifact_20260629.zip
```

The final zip is built from a scrubbed staging directory. It is intended for
reviewers as an anonymous experiment artifact, not as a raw workstation backup.

## Included

- Source code, scripts, tests, configs, schemas, and manifests.
- Paper-facing local/open-weight outputs, canonical certificates, runtime
  artifacts, reports, tables, figures, metrics, and witness bundles.
- Rebuttal-2 fresh no-system-prompt v3 shared-proposal audit artifacts.
- Final Markdown handoff docs and paper rewrite scaffold.

## Excluded

- Secrets and environment files.
- Git history and local virtual environments.
- Model caches and cloned upstream repositories.
- Generated smoke-test and dry-run outputs.
- Old zip files.
- Stale historical PDF and presentation deck.
- Historical planning memos and archived paid-provider notes.

## Verification

The final package is checked for:

- zip integrity;
- absence of local identity paths and Google presentation links;
- absence of stale large-grid/frontier/human-evaluation claims in included
  Markdown and text files;
- absence of generated smoke-test/dry-run artifact folders;
- presence of Rebuttal-2 v3 artifacts and full stress replay evidence.

Exact size and checksum are reported in the final handoff.
