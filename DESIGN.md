# TRIBUL8ION / BLACK-DEATH EDITORIAL

**Design system:** v5 · **Surface:** GitHub profile README, generated static raster hero and SVG cards.

## Direction

A death-metal wordmark sits on an *ink-black*, textured editorial surface. The surrounding cards are functional, deliberate and readable: think underground metal sleeve art executed with the hierarchy of a careful systems dashboard. This visual approach is adapted from the user's supplied reference board and user-approved dark palette. The layout principles draw from the `awesome-design-md` Linear reference (one accent, dense information, hairline rules) and Wired editorial analysis (large serif headlines, smaller functional metadata).

**Every profile visual has an opaque black surface.** There is no white, parchment or cream canvas. Bone is used for typography and engraving highlights, not as a background. GitHub's own surrounding website theme is controlled by GitHub and outside the README's control.

## Palette

| Token | Value | Usage |
|---|---|---|
| Void | `#080809` | Main hero background, deepest black |
| Panel | `#101013` | Cards, dark editorial modules |
| Secondary | `#171417` | Future/unavailable chart cells |
| Grid | `#30292D` | Hairlines and empty heatmap units |
| Rule | `#524044` | Frame, panel separators |
| Bone | `#F1E9DE` | Headlines and metric figures |
| Body | `#D8CCC2` | Narrative/body copy |
| Muted | `#BDAEAA` | Supporting text |
| Subtle | `#AB9A98` | Timestamps/footnotes |
| Rust | `#D28466` | Short accents, section numbers, ornaments |
| Rust muted | `#A56661` | Small ornament highlights |
| Blood | `#A24D55` | Graph data accents |

The heatmap uses five restrained ink tones, from charcoal to warm bone/rust. **No gradients, neon glows or colorful technology badges.**

## Typography & rhythm

The original supplied blackletter wordmark is isolated as a transparent raster engraving. It remains a display asset only, not an all-purpose font.

- **Primary panel headlines:** Georgia / DejaVu Serif 37–42 units, medium weight, compact two-line rhythm. Mobile 26–31.
- **Body text:** Arial / Liberation Sans 16–21, regular. Mobile 13–17.
- **Metrics:** Georgia/DejaVu Serif 59 on desktop, 46 on mobile, with larger line height.
- **Machine labels:** Consolas / DejaVu Sans Mono 11–15, uppercase, rust accent.
- **Grid:** 1120 viewBox desktop, 420 mobile. Desktop left narrative / right data. Mobile reflow is purpose-made, never a CSS scaled-down desktop panel.
- **Spacing:** 4px microgrid, strong 20–40px content padding, 1px frame and section hairlines.

No font files are bundled. The glyph rendering uses standard fallbacks; the bitmap wordmark remains visually exact without a runtime font requirement.

## Modules

1. **Hero:** identity-first dark sleeve with ornate lettering and tiny industrial metadata.
2. **Operator:** real professional summary, not overlong personal questionnaire.
3. **Public work:** two checked public links, with reserved space and genuine contribution claims.
4. **Public signal:** four public metrics, deliberately unlabeled synthetic totals.
5. **Contribution archive:** year ALWAYS runs January to December; months after the latest data date are shown as unavailable, never zero activity.
6. **Code footprint:** share of public non-fork code bytes; zero-percent slivers, `Just` file type and under-0.5% entries are omitted.
7. **Transmissions:** latest public API events, not a complete history or private audit stream.
8. **Toolchain:** four purposeful domains; no badge wall.

## Accessibility & quality gates

- Each SVG has a descriptive `<title>`/`aria-label`; README images have `alt` text.
- First rendered profile load has no third-party hosted images, tracking URLs, external CSS/fonts or executable scripts.
- Text and grid colors are measured against opaque panel backgrounds; secondary text must meet 4.5:1 for body-size use.
- Safe XML escaping, directional-control stripping and length constraints for untrusted API values.
- Production failure preserves previous image data; fixture mode does not rewrite README.
- Two independent layouts: desktop 1120 and mobile 420; hero desktop+mobile are raster assets rendered from one transparent wordmark.
- GitHub HTML restrictions require static images; no client-side scripting or SVG animation.

## Generated assets & privacy

`render_static.py` generates the fixed editorial SVG components. `render_hero.py` builds dark PNG identity banners from the local extracted wordmark. `render_widgets.py` queries GitHub public metadata on schedule, renders eight desktop/mobile SVGs and updates the README's content-addressed cache keys. Fixtures are test-only. No private repository detail or environment secret becomes visible inside generated SVGs.

## Exclusions

No visitor trackers, Spotify widgets, GitHub Trophies, arbitrary unverified skill badges, fake contributions or promotional copy. Design details must support the user's real work rather than bury it.
