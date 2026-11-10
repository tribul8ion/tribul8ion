# TRBL8 black-death editorial / deployment

This repository is the public profile for `tribul8ion`. The README uses only locally hosted SVG and PNG image assets. All imagery remains dark regardless of the GitHub site theme.

## Deploy

1. Review and merge the v5 PR after CI succeeds. The `main` push automatically runs **TRBL8 / Public telemetry** to regenerate the eight public-data SVGs with the new renderer and update versioned README URLs.
2. Check **Actions → TRBL8 / Public telemetry**. Both **Validate SVG and rendering** and **Synchronize public data** must be green on the merge-triggered run.
3. Open the profile in desktop and mobile view. The first successful refresh will show actual public counts, contributions for Jan–Dec, and languages with tiny auxiliary file types omitted.
4. Scheduled telemetry refresh remains 05:19 UTC daily. GitHub may delay scheduled workflows under load; if necessary use **Run workflow** on `main`.

## Local validation

```bash
python -m unittest discover -s tests -v
python scripts/render_static.py
python scripts/render_widgets.py --fixture tests/preview-fixture.json --out /tmp/trbl8-demo
# Optional for regenerating identity PNG (the repo includes the actual wordmark PNG):
pip install Pillow
python scripts/render_hero.py
```

**Do not run the fixture command with `--out assets/widgets` and commit the results.** The fixture has synthetic counts meant solely for visual testing. In production, the actual GitHub Actions token is used and README revisions are written only after a successful API fetch.

## Source files

- `assets/wordmark-blackdeath.png`: transparent user-approved gothic wordmark extract
- `assets/hero-blackdeath-v5.png` and `assets/mobile/hero-blackdeath-v5-mobile.png`: dark imagery
- `assets/operator-panel.svg`, `assets/project-*-v5.svg`, `assets/stack-v5.svg`, `assets/footer-v5.svg` and mobile equivalents: local static SVGs
- `assets/widgets/{signal,heatmap,languages,activity}.svg` and `assets/widgets/mobile/*.svg`: telemetry generated on the default branch
- `scripts/render_widgets.py`: safe public GitHub data ingestion, SVG output, and cache-busting README updates
- `DESIGN.md`: explicit design tokens, hierarchy and accessibility guidance

## Notes

The profile measures public repository metrics only. A 365-day public contribution counter is not equal to calendar-year contribution cells. Calendar-year SVG uses **Jan → Dec** with future cells drawn as disabled; mobile summarizes months because 53 tiny weekly columns would be unreadable.
