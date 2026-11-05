# Sources

- The Nyan Cat GIF is the exact file requested by the user: [GIPHY source page](https://giphy.com/gifs/cat-pixel-art-nyan-7lsw8RenVcjCM). `assets/nyan-cat.gif` was downloaded directly over HTTP, unchanged. Its source metadata is retained in `assets/nyan-cat-source.json`. It is not original artwork by this project.
- `assets/nyan-cat-still.png` is a first-frame accessibility fallback extracted from that GIF, used only when motion is paused or reduced.
- Space Grotesk is self-hosted; its SIL Open Font License is included in `assets/Space-Grotesk-OFL.txt`.
- Repository counts, stars, languages and project links come from the unauthenticated public GitHub API. Contribution counts come from the public GitHub contribution calendar, parsed from its labeled day cells. No private repository metadata is used.
- The site is static. `python scripts/update_profile.py` refreshes the public snapshot and the shared README assets. `python scripts/build_offline.py` rebuilds the standalone offline page. No package installation is required.

- The revised art direction was developed with the installed Antigravity CLI: asymmetric midnight console, original pixel companion and distinct capability diagrams for each featured project. The diagrams are illustrations of documented functionality, not screenshots of running software.
- Sora is self-hosted and embedded in generated SVGs. Its SIL Open Font License is retained in `assets/Sora-OFL.txt`.
- Language bars count each public non-fork repository once by its primary GitHub language. They are not proficiency ratings or code-byte percentages. Active days count calendar dates with at least one public contribution; the calendar includes zero-contribution dates as well.
