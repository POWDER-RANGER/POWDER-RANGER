# POWDER-RANGER CRT Badge Assets

These are repository-owned SVG badges used by the profile README. They are decorative labels for technologies and verified work, not third-party-issued certifications, GitHub achievements, or official project logos.

## Style contract

- Background: near-black `#060709` with restrained dark-red plate gradient.
- Outline and edge: crimson `#E43A48`, with a narrow bright red upper rail.
- Text: off-white `#F5E6E6`, amber secondary `#E7AD76`.
- Monospace typefaces: `Consolas`, `Menlo`, system monospace.
- Glow: inline SVG Gaussian blur, limited to short glyphs for readability.
- Accessibility: a literal `<title>` and `aria-label`; readable without glow, external fonts, scripts, or network services.
- Motion: none in technology badges. The terminal styling must not compromise readability or trigger reduced-motion concerns.
- Individual badges should remain 290×52 and render without remote styles or image dependencies.

## Attribution and status

- Technology badges describe areas represented in linked code, not credentials.
- The `claude-mem-merged-5324.svg` badge records an upstream pull request merged on 2026-11-04; it is not a GitHub-issued achievement.
- The self-curated milestone board lives at `../../.github/assets/trophy.svg` and explicitly distinguishes an accepted contribution from submitted patches and original work.
- New `MERGED` or `ACCEPTED` badges require verification of the exact upstream PR state.
- Do not label a contribution as merged based only on fork commits, green local tests, or a successful build.

To update the set, edit the SVG sources and the relevant image links in the profile `README.md`. Keep each badge link pointed at the directly relevant repository, pull request, or evidence page.

The official GitHub achievements view remains at https://github.com/POWDER-RANGER?tab=achievements.
