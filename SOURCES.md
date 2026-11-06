# Sources

- The work showcase uses actual product artifacts. `work-bridge.png` is the unmodified UmiBridge Corp office frontend rendered in an isolated preview with role-only idle demo staff, not production activity. `work-quietshare.png` is a real QuietShare QA capture with English controls and sample presentation notes, corresponding to the interface documented in its public visual guide. The Automation Studio panel shows an illustrative sample using the documented `MOVE`, `CLICK` and `WAIT` DSL commands; it is not a screenshot or an executed workflow. Exact image hashes and source commits are recorded in `assets/work-sources.json`.

- The additional pixel GIFs are downloaded originals, self-hosted with this profile. The [ringed planet](https://pixor.art/library/scifi/sci-planet/) and [tin toy robot](https://pixor.art/library/toys/toy-robot/) come from Pixor's CC0 library. The [blue flame](https://opengameart.org/content/fire-0) is by Spring Spring (Julie Damsgaard), CC0. `assets/pixel-assets-source.json` records the original download URLs, byte sizes and SHA-256 hashes. Static PNGs are first-frame motion fallbacks. No GIF frames, colors or timing were changed.
- The current design is an open pixel night, with three directly linked project posters. The previous generated Workbench image was a rejected concept and is not used in the site or README.

- The Nyan Cat GIF is the exact file requested by the user: [GIPHY source page](https://giphy.com/gifs/cat-pixel-art-nyan-7lsw8RenVcjCM). `assets/nyan-cat.gif` was downloaded directly over HTTP, unchanged. Its source metadata is retained in `assets/nyan-cat-source.json`. It is not original artwork by this project.
- `assets/nyan-cat-still.png` is a first-frame accessibility fallback extracted from that GIF, used only when motion is paused or reduced.
- Space Grotesk is self-hosted; its SIL Open Font License is included in `assets/Space-Grotesk-OFL.txt`.
- Repository counts, stars, languages and project links come from the unauthenticated public GitHub API. Contribution counts come from the public GitHub contribution calendar, parsed from its labeled day cells. No private repository metadata is used.
- The site is static. `python scripts/update_profile.py` refreshes the public snapshot and the shared README assets. `python scripts/build_offline.py` rebuilds the standalone offline page. No package installation is required.

- The revised art direction was developed with the installed Antigravity CLI: asymmetric midnight console, original pixel companion and distinct capability diagrams for each featured project. The diagrams are illustrations of documented functionality, not screenshots of running software.
- Sora is self-hosted and embedded in generated SVGs. Its SIL Open Font License is retained in `assets/Sora-OFL.txt`.
- Language bars count each public non-fork repository once by its primary GitHub language. They are not proficiency ratings or code-byte percentages. Active days count calendar dates with at least one public contribution; the calendar includes zero-contribution dates as well.
