# Source map

This repository builds the GitHub profile README and its self-contained artwork. The native profile works directly on GitHub; it does not require the companion website or JavaScript.

## Edit the native GitHub profile

| Module | What it controls |
| --- | --- |
| [hero.py](../scripts/native_profile/hero.py) | Owner monogram, headline, original Nyan and planet scene |
| [projects.py](../scripts/native_profile/projects.py) | Three project compositions, purposes and capability rails |
| [activity.py](../scripts/native_profile/activity.py) | Flame placement, dated calendar, active-date orbit and summaries |
| [analytics.py](../scripts/native_profile/analytics.py) | Monthly bars, weekday averages, repository comparison and active-date share |
| [details.py](../scripts/native_profile/details.py) | Language distribution and footer actions |
| [readme.py](../scripts/native_profile/readme.py) | GitHub picture elements, links and cache versions |
| [core.py](../scripts/native_profile/core.py) | Shared SVG primitives, embedded media and reduced-motion fallbacks |
| [ornaments.py](../scripts/native_profile/ornaments.py) | Stars, meteors, bidirectional messages, projection sequence, process actions and bar glints |

[render_profile.py](../scripts/render_profile.py) is the small command-line entry point. Each section exposes `render(data)`. Desktop and mobile layouts live together in their section, so changing a component does not require searching one large renderer.

## Edit sprite motion

The [sprite_motion](../scripts/sprite_motion) package contains one module per character: `bridge.py`, `quiet.py` and `automation.py`. `core.py` embeds the original PNG and provides shared SVG construction. The package entry point writes the three rigs and their source manifest.

Only the native SVG geometry and animation change. The approved PNG artwork and original downloaded GIFs retain their exact bytes. Still images provide the system reduced-motion state.

## Build and check

Run from the repository root with Python 3. No third-party Python packages are required:

```powershell
python scripts/build_sprite_motion.py
python scripts/render_profile.py
python scripts/build_offline.py
python scripts/native_profile/check.py
python scripts/check_assets.py
```

`assets/profile-data.json` is the dated public-data input. Generated SVGs and README are committed so GitHub can render them directly. Edit the modules and rebuild instead of editing the large base64 SVG outputs.

[profile_metrics.py](../scripts/profile_metrics.py) derives the chart data. It preserves zero-count dates, flags incomplete calendar months and divides weekday totals by their observed date counts. Run `python scripts/test_profile_metrics.py` to check date boundaries and reconciliations. Repository metadata comes from the unauthenticated public API; the calendar contains publicly displayed contribution totals.

Use `python scripts/update_profile.py --data-only` to refresh the inputs without rendering. `--date YYYY-MM-DD` selects the snapshot cutoff. Raw public responses are retained under the ignored `output/analytics-review` directory for verification.

After committing generated artwork, run the renderer with `--asset-ref COMMIT_SHA`, replacing `COMMIT_SHA` with that commit. Commit the resulting README. This pins every native image to immutable artwork, so GitHub cannot serve an older branch image under a new cache query. The default `main` reference is convenient while editing locally.

The companion website remains in `index.html`, `styles.css` and `profile.js`. Its separate motion controls do not run inside the GitHub README.
