# TRIBUL8ION profile / maintainers' note

The public profile is a Markdown document with local static SVG artwork. No Node app, web server, external image API or external font dependency is required.

## Deploy / verify

1. Review and merge the v4 PR into `tribul8ion/tribul8ion` after its **Validate SVG and rendering** job succeeds.
2. In repository **Settings → Actions → General**, ensure workflow token permissions permit `contents: write` for the scheduled refresh. GitHub repository or organisation policies may override this.
3. Open **Actions → TRBL8 / Public telemetry → Run workflow** on the default branch. This triggers the first real public-data refresh. Until it succeeds, cards deliberately say that the data is not yet available.
4. Inspect logs for `OK: refreshed 8 SVG cards` and the resulting `chore(profile): refresh public telemetry` commit. Confirm the profile images now show current public data. GitHub image caching can delay visual changes briefly.
5. Daily scheduled refresh runs at 05:19 UTC, subject to GitHub's best-effort scheduling.

## Local QA

```bash
python -m unittest discover -s tests -v
python scripts/render_static.py
python scripts/render_widgets.py --fixture tests/preview-fixture.json --out /tmp/trbl8-demo
```

Use `tests/preview-fixture.json` **only** for previews. The tracked production SVG files contain no synthetic statistics. A failed GitHub API fetch exits before writing any image. Each SVG is written using a temporary file and replace operation.

## Scope / provenance

- Signal: public profile REST fields, merged PR search and contribution calendar.
- Activity: the public events feed, limited by GitHub's public-event retention.
- Languages: GitHub-reported language bytes for up to 30 recently pushed public repositories owned by this account, excluding forks.
- Contributions: GitHub GraphQL calendar. The visible count can differ from a user's total private work.
- Mobile: distinct SVG viewports. The mobile heatmap explicitly covers 22 weeks, not a full year.

## Troubleshooting

If refresh fails with `403` or a push error, verify that Actions is enabled, the bot has `contents: write`, the branch permits Actions commits and GitHub API is not rate-limiting the run. If the GraphQL step fails, verify the ephemeral token can query the user contribution calendar. Existing SVG remains on display until the next successful refresh.

Read [`DESIGN.md`](DESIGN.md) for tokens, layout, accessibility rules and rationale.
