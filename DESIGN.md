# TRIBUL8ION / Editorial Black Metal

**Version:** 4.0 · **Surface:** GitHub profile README / static SVG · **Status:** implementation specification

## Design thesis

Treat the profile as a personal *engineering dossier*, not a gamified trophy wall. The primary influence is the exacting product-UI restraint documented in the `awesome-design-md` **Linear** reference: near-black planes, hairline separation, one chromatic accent and clear reading order. **Wired** contributes an editorial hierarchy that separates a distinctive serif display from functional body type; **IBM** contributes system-like modular grids and matter-of-fact labels. The distressed black-metal sigil and thorn motif are our original brand layer, reserved mainly for the hero.

This is an adaptation of principles, **not** copied assets or a claim that any reference represents the current live website.

## Principles

1. **One strong artifact per section.** The hero is the emotional element; telemetry is neutral and legible.
2. **Hierarchy beats density.** 3 information levels: primary title / data / explanatory note. No tiny decorative junk.
3. **Concrete claims only.** Public, verifiable repositories; activity never simulated in production.
4. **No shadows, glows or gradients in data cards.** Use subtle surface changes and 1 px rules instead.
5. **Accessibility is a constraint.** Alt text, real Markdown narrative, explicit data provenance and fallback copy.
6. **Responsive by design.** A phone / narrow GitHub layout uses specially composed 420-px SVGs; it never shrinks the full desktop chart to illegibility.
7. **No external rendering dependency.** Images are static SVG files generated in the repository; no CSS, JS or webfonts are injected into Markdown.

## Color tokens

| Token | Hex | Purpose |
| --- | --- | --- |
| `void` | `#09090B` | Main identity background |
| `panel` | `#100F12` | Data card surface |
| `secondary` | `#171519` | Reserved secondary surface |
| `grid` | `#302B30` | Chart skeleton / minor rules |
| `rule` | `#42383E` | Main card boundary |
| `bone` | `#F0E9DE` | Primary title and metric values |
| `body` | `#CCC1B9` | Body text |
| `muted` | `#AAA0A0` | Secondary descriptions |
| `subtle` | `#8F8588` | Timestamps, source labels |
| `oxide` | `#C17176` | One accent: section identity, short bars |
| `oxide_soft` | `#976166` | Reserved muted emphasis |

**Chart sequence:** `#28242A` → `#5C343E` → `#89505A` → `#B87877` → `#E7B7A4`. Never treat color as the only representation of meaning: a chart label and readable numerical value accompany comparisons.

## Typography

| Role | Desktop SVG | Mobile SVG | Typeface / fallback |
| --- | --- | --- | --- |
| Hero identity | Existing serif wordmark | 44px | Georgia → DejaVu Serif → serif |
| Main card heading | 32px / 700 | 23px / 700 | Arial → Liberation Sans → sans-serif |
| Main body / explainer | 17–20px | 13–16px | Arial → Liberation Sans → sans-serif |
| Metric numbers | 63px / 700 | 42px / 700 | Arial → Liberation Sans → sans-serif |
| Eyebrows / machine labels | 15–16px / 700 | 11–13px / 700 | Consolas → DejaVu Sans Mono → monospace |
| Minor caption | 13–14px | 11px | Monospace, subdued color |

User-agent rendering of GitHub is outside our control. **Do not rely on a specific installed proprietary font.** The SVG must look intentional with its fallbacks and must not attempt to embed font files. The README body uses GitHub's own text rendering, not a custom font hack.

## Layout grid

- **Desktop:** 1120 SVG units, 36-unit horizontal content inset, 84-unit section marker, 4-point micro rhythm, 273-unit data columns. Every full-width SVG stands alone.
- **Mobile:** 420 SVG units, 20-unit inset, layout reflows to 2×2 metrics and up to 22 weeks of contribution cells, labelled accurately.
- **Spacing:** desktop 12–20 between line items, 30–40 between content bands; primary data baseline is aligned within its grid.
- **Shapes:** squared corners; 1 px strokes; almost no decorative container nesting; chart squares with no radius.
- **Contrast:** `bone`, `body`, `muted`, `subtle`, `oxide` are all tested for at least 4.5:1 against `panel` using WCAG relative luminance.

## Content / hierarchy

1. **Hero:** `TRIBUL8ION` and the short systems/automation/engineering identity statement.
2. **About:** real paragraph in GitHub Markdown; not an SVG-only biography.
3. **Operator strip:** automate → build → operate → verify.
4. **Work in the open:** two externally verifiable public items. The Frigate PR is merged; the startpage is described as a customization, not an original invention.
5. **Public telemetry:** 4 individually legible, vertical full-width cards. Fallbacks show no fictional stats.
6. **Toolchain:** role-grouped, not 30 colored logos or unqualified skill levels.
7. **Footer:** a single piece of brand language, no automatic music or trackers.

## Data / privacy policy

`render_widgets.py` may query GitHub REST and GraphQL using Actions' ephemeral `GITHUB_TOKEN`. It gathers only public-profile stats, search results accessible to the profile-repository token, public non-fork repository language breakdowns and the public events feed. It must not request private repository names, serialize arbitrary payloads into SVG, or log credentials. User-provided strings are XML-escaped and constrained before insertion.

**Semantics:** public merged PRs are not the same as contributions; language footprint is size-based, not proficiency; event feeds are incomplete by design. The phone graph shows the **most recent 22 weeks**, while the annual count still refers to the calendar's rolling year.

## Rendering constraints / quality gates

- SVG `<title>` and README `<img alt>` must be present.
- No `<foreignObject>`, executable JavaScript, embedded base64 images or external font/image references.
- Desktop and mobile snapshots at 1440 px and 390 px viewport widths.
- No clipped text or chart labels, no horizontal scrolling on mobile, no malformed XML.
- Automated unit tests check DOM, escaping, paths, contrast, placeholder state and the API fixture.
- Production SVGs remain blank or explicitly unavailable before the first successful authenticated fetch. Synthetic fixture numbers appear **only** in the documented visual demo.
- Scheduled workflow updates only generated widget files; PR workflows run local tests and have read-only permission.

## Deliberate exclusions

No GitHub trophies, random badges, public music status, visitor tracker or unsupported «all languages» claims. No endless widgets added just for decoration. Features should reflect verifiable work and justified user value, not template completeness.
