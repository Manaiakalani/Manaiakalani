# Profile automation

This repo is the GitHub profile README for [@Manaiakalani](https://github.com/Manaiakalani).
Everything below the fold is generated; only `README.md` prose and `assets/` are hand-edited.

## Branch layout

| Branch     | Written by                 | Contents                                        |
| ---------- | -------------------------- | ----------------------------------------------- |
| `master`   | you + `projects.yml`       | README, scripts, workflows, static assets       |
| `projects` | `projects.yml`             | `<repo>-{dark,light}.svg` cards                 |
| `views`    | `views.yml`                | `views-{dark,light}.svg` badge + `count.json`   |
| `stats`    | `stats.yml`                | github-profile-summary-cards output             |
| `output`   | `snake.yml`                | contribution snake SVGs                         |

Generated branches are force-pushed (`keep_history: false`) every 12 hours; never commit to them by hand.
The README references them via `raw.githubusercontent.com/manaiakalani/manaiakalani/<branch>/...`.

## Workflows

All four run on `0 */12 * * *`, on `workflow_dispatch`, and on pushes that touch their own
inputs. Third-party actions are pinned by commit SHA; Dependabot bumps them weekly.

| Workflow       | What it does                                                                                               |
| -------------- | ---------------------------------------------------------------------------------------------------------- |
| `projects.yml` | Runs `update_currently_building.py`, commits the README block, pushes cards to `projects`.                  |
| `views.yml`    | Runs `update_views.py` using `PROFILE_TOKEN` (traffic API needs a PAT). Fails loudly if traffic is 403.     |
| `stats.yml`    | Computes the current `America/Los_Angeles` UTC offset (DST-aware), runs summary-cards, pushes to `stats`.   |
| `snake.yml`    | Platane/snk → `output`.                                                                                     |

### Secrets

- `PROFILE_TOKEN` — classic PAT with `repo` scope (or fine-grained with *Administration: read*
  on this repo). Required for `/traffic/views`. If it expires, `views.yml` goes red instead of
  silently freezing the counter at the seed value.

## Scripts (`.github/scripts/`)

| Script                         | Purpose                                                                                  |
| ------------------------------ | ---------------------------------------------------------------------------------------- |
| `fonts.py`                     | Emits `@font-face` CSS with base64 woff2. Subsets to the glyphs actually used when given `text=`. |
| `build_banners.py`             | Writes `assets/{header,footer,wave}[-light].svg`. Run after editing copy or colors.      |
| `update_currently_building.py` | Picks repos, renders cards to `dist/`, rewrites the README between the `CURRENTLY_BUILDING` markers. |
| `update_views.py`              | Merges 14-day traffic into `count.json`, renders the badge to `dist-views/`.             |

### Running locally

```sh
python3 -m pip install -r .github/scripts/requirements.txt   # fonttools + brotli for subsetting
gh auth login                                                # scripts shell out to `gh api`

python3 .github/scripts/build_banners.py                     # regenerates assets/*.svg (commit these)
OWNER=Manaiakalani python3 .github/scripts/update_currently_building.py
OWNER=Manaiakalani REPO=Manaiakalani VIEWS_STRICT=0 python3 .github/scripts/update_views.py
```

`dist/`, `dist-views/`, and `profile-summary-card-output/` are gitignored; they're only pushed
to their branches by CI. Without `fonttools` the scripts still run, embedding the full
pre-subset fonts (~30 KB per SVG instead of ~3 KB).

### Tuning "Currently Building"

In `update_currently_building.py`:

- `FEATURED` — repo names to always show first, in order.
- `SKIP_REPOS` — repo names to hide. Forks, archived, private, `CxE*`, and this repo are
  always hidden.
- `ACTIVITY_WINDOW_DAYS` / `MAX_CARDS` — ranking is commits in the window, then `pushed_at`.

## Fonts

`assets/fonts/*.woff2` are pre-subset Latin builds of Doto, Space Grotesk, and Space Mono
(all SIL OFL 1.1; see `assets/fonts/OFL.txt` and `NOTICE`). They are embedded as data URIs
because GitHub's image proxy blocks external font requests inside `<img>`.
