# TRBL8 / Black Metal Telemetry

## What is this?

Custom GitHub-profile SVG widgets with a strict black-metal / industrial visual language. No third-party image CDN or counter services. All widgets are rendered by a local Python script using public GitHub REST + GraphQL data and committed as SVG assets through GitHub Actions.

## Deployment

1. Copy `README.md`, `assets/`, `scripts/`, and `.github/workflows/` into `tribul8ion/tribul8ion`.
2. Commit to `main` (or merge a PR). Under repository **Settings → Actions → General → Workflow permissions**, allow the workflow's `GITHUB_TOKEN` to write contents, if your repository policy does not permit it by default.
3. Go to **Actions → TRBL8 // Refresh public telemetry → Run workflow**. No PAT or third-party API key required.
4. The action fetches GitHub public data and commits four widgets to `assets/widgets/`. Runs daily thereafter. GitHub Actions schedule timing is best effort, not guaranteed precisely.
5. If a workflow run fails, examine its log (API limits / token permissions). The existing graphics remain unchanged. First-run placeholders deliberately show `AWAITING FIRST SYNC` rather than fictional metrics.

## Source provenance

* `signal.svg`: public repositories and followers from `/users/{login}`; merged public PR count from `/search/issues`; annual contributions from GitHub GraphQL calendar.
* `heatmap.svg`: contribution calendar from GraphQL; respects GitHub's visibility rules. No private repository names or metadata fetched.
* `languages.svg`: language byte counts from PUBLIC OWNED NON-FORK repositories (up to 30 most recently pushed); NOT a measure of programming skill or commit share.
* `activity.svg`: public event feed, which GitHub limits to a recent window. Older activities may not appear. No scraping.

## Design tokens

Background `#09090b`, surface `#111013`, paper `#ece5d9`, muted `#b0a7a3`, aged border `#373034`, rust/blood `#ab575c` and `#d49c91`.

No executable SVG scripts, embedded fonts, external image references, animated gimmicks, third-party renderers or tracking counters. GitHub removes/does not support scripting and animation in SVG.

## Customizing

Edit color variables and the `signal()`, `heatmap()`, `langs()`, and `recent()` functions in `scripts/render_widgets.py`. For offline preview:

`python scripts/render_widgets.py --fixture tests/preview-fixture.json --out /tmp/trbl8-preview`

This fixture contains **synthetic design-preview numbers only** and must never be copied into production SVGs. The committed widgets intentionally begin as empty/pending until the first successful API sync.

## Security

`GITHUB_TOKEN` is the sole credential, injected by GitHub and not printed or committed. The workflow has `contents: write` only to commit the generated SVGs, with no broad-scope PAT. Avoid linking private projects or corporate/internal systems in README. API errors cause the workflow to fail and preserve previous render results.

## Further upgrade ideas

1. A project showcase fed by an explicitly approved public repository allowlist.
2. A "build ritual" timeline fed from selected public releases rather than fabricated CI statuses.
3. Dual theme variants via GitHub `<picture>` sources while preserving the black-metal core.
4. A custom generative badge system for milestones (no bogus trophies).
5. Compact responsive versions of cards for mobile and an RSS-based "now building" update.