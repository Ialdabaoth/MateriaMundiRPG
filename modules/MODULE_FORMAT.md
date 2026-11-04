# Materia Mundi open module protocol (`mm-module/1`)

An open way to publish adventures, regions and campaigns for **Materia Mundi** and **E9** so they can be played entirely in a web browser or the Companion app, with no VTT, and printed as books from the same source.

The rules are simple. A module is a **git repository**. Building it produces a **static website**: a map viewer, print-ready PDFs and a `module.json` manifest the Companion reads. GitHub with GitHub Pages is the default host, but any git host and any static web host will do. A referee runs a **campaign by forking** a module repository. The campaign's live record (sessions, explored hexes, character sheets) is committed to the fork, so git history becomes the campaign chronicle.

This repository is the reference implementation: `modules/season-1` (Leinster, 1422) and the build tools in `modules/tools`.

---

## 1. Repository layout

```
mm.json                      discovery file: what this repository publishes (section 2)
modules/
  <module-id>/
    module.json              the module source (section 3)
    text/                    optional: prose keyed by site slug, Markdown
    tables/                  optional: random tables, JSON (section 6)
    creatures/               optional: stat blocks or references (section 6)
  assets/tiles/icons/        map icons (PNG, transparent, flat-top hex proportions)
  geo/                       boundary shapes the maps clip to (GeoJSON)
  tools/                     the build (build.py and helpers)
campaign/                    only in a referee's fork (section 7)
.github/workflows/           the build-and-publish Action
```

A publisher may hold several modules in one repository. Module ids are lowercase ASCII with hyphens (`season-1`, `hansa-1`).

## 2. Discovery: `mm.json`

At the repository root, and copied to the root of the published site:

```json
{
  "format": "mm-repo/1",
  "name": "Materia Mundi: Season 1",
  "publisher": "Heph",
  "systems": ["materia-mundi", "e9"],
  "license": "CC0-1.0",
  "modules": [{ "id": "season-1", "path": "modules/season-1/" }]
}
```

The Companion adds a repository from its published URL. It reads `mm.json` and then each module's built `module.json`.

## 3. Module source: `modules/<id>/module.json`

| Field | Meaning |
| --- | --- |
| `id`, `title`, `short`, `version` | `version` is semver. Breaking changes to ids (section 5) need a new major version. |
| `license` | SPDX id. Required. |
| `dem` | `[lat0, lat1, lon0, lon1]`: the SRTM 1° tiles (south-west corners) the terrain comes from. The build fetches them. |
| `admin` | Path to the GeoJSON boundaries (`properties.name` is the region name). |
| `books` | Ordered list: `{id, title, county, region, detail}`. `region` names the book's 3-mile region and `detail` its half-mile overview. |
| `world` | Terrain settings for the one 3-mile world map (`counties`, `forest`, `bog_east_of`, `bog_north_of` …). |
| `atlas` | `{hex_mi: 3, page_hex_mi: 24}`. |
| `exploration` | `{hex_mi: 0.5, cluster_mi: 1.2, overrides: {county: {terrain settings}}}`. |
| `regions` | Named map regions. Each has `sites: [[name, lat, lon, kind, note?]]` plus terrain settings. |

Site `kind` is one of `castle town abbey tomb hill cave ruin grove camp lair mist dead`. A new kind needs an icon in `assets/tiles/icons` and an entry in the build's icon table.

Every site has a **real latitude and longitude**. Distances in the text must agree with the maps.

## 4. Scales and pages (fixed for every module)

| Product | Hex | Printed size | Page |
| --- | --- | --- | --- |
| World map | 3 mi (1 league, about 1 hour on foot) | 1 in | the whole module, on the web only |
| Atlas | 24-mile page hex of 3-mile hexes | 1 in per 3-mile hex | one 11 × 8.5 in page per 24-mile hex that contains module land |
| Exploration map | ½ mi (about 10 minutes on foot) | 1 in per ½-mile hex, about 2 mi each way | one page per point of interest; sites closer than `cluster_mi` share a page |

The page layout is 11 × 8.5 in landscape with a ¼ in border, the map (8.75 × 8 in) on the left and the legend on the right. Hexes beyond the module's boundary still render in full wherever they fall on a page, but they don't get pages of their own. Travel: forest and light woods both double travel time, and a Survival roll finds a path at normal speed (Easy in light woods, Hard in forest).

Hex grids are flat-top, with odd columns shifted down, and are numbered `CCRR` from `0101`. 24-mile page hexes are numbered the same way on their own grid.

## 5. Identifiers and links (stable within a major version)

- **Site slug**: the site name, accents stripped, lowercase, non-alphanumerics → `-` (`Dinn Ríg` → `dinn-rig`).
- **Exploration key**: `p-` + the slug of the page's lead site (`p-an-caislean-dubh`).
- **Atlas page**: its number, `1…n`, ordered north to south and then west to east.
- **Viewer links**: `#world`, `#atlas-7`, `#p-an-caislean-dubh`, `#p-an-caislean-dubh--dinn-rig`.
- **Hex addresses**: `<map>:<hex>`, where map is `world` or an exploration key: `#world:0706` (a 3-mile hex), `#p-an-uaimh:0304` (a half-mile hex on that page). These are the same keys as `campaign/state/hexes.json`. Every map uses the world map's hex geometry (`world.hex_px`, `world.col_px`, `world.origin_px`).
- **Render modes**: `?mode=map` shows only the map, with zoom buttons; `?mode=atlas` shows only the page list and search. The plain viewer shows both. An app can show the two modes in separate frames (the Companion does): a pick in the atlas frame posts `{"event": "select", "hash"}` instead of navigating, the app sends `{"show": hash}` to the map frame, and sends `{"current": hash}` back to the atlas frame so it highlights the page being shown.
- **Embedding**: the viewer can sit in an iframe. It posts `{"type": "mm-viewer", "event": "view" | "hex" | "select", "module", "version", "hash", "map"?, "title"?, "small"?, "hex"?, "scale"?, "sites"?, "terrain"?, "terrainName"?}` to its parent whenever the reader moves or taps a hex. The parent may post `{"type": "mm-viewer", "show": "#world:0706"}` to open a link, and `{"type": "mm-viewer", "marks": [{"map": "world", "hex": "0706", "label": "P"}]}` to place markers, such as where a party stands.

If a later version renames a site, add `"aliases": {"old-slug": "new-slug"}` to `module.json` so old links and campaign notes keep working.

## 6. Tables and creatures

- Random tables use **d20 and d6 only**. A big table is a d6 choosing among d20 sub-tables, 120 entries in all. JSON: `{"id", "title", "die": "d20" | "d6", "rows": [{"roll": [lo, hi], "text", "site"?: slug}], "sub"?: {"1": table, …}}`.
- Creatures reference the Materia Mundi Compendium by name and page wherever possible (`{"name": "Athach", "base": "Ogre", "page": <Compendium page>, "changes": "…"}`). Give a full stat block only for something new.

## 7. Campaigns: fork, play, commit

A referee **forks** a module repository and adds a `campaign/` folder. Module authors never write to `campaign/`, so the referee can pull upstream fixes (`git pull upstream main`) without conflicts.

```
campaign/
  campaign.json              {"format": "mm-campaign/1", "modules": ["season-1"], "start": "1422-05-01", "referee": "…"}
  chronicle/2026-11-08-session-01.md   what happened, written after each session
  state/hexes.json           {"<map>:<hex>": {"explored": true, "notes": "…"}}   map = "world" or an exploration key
  state/sites.json           {"<slug>": {"status": "cleared", "notes": "…"}}
  state/ratchets.json        {"<region>": 7}   the d20 region ratchets
  characters/<name>.json     character sheets, Companion CHARACTER_FORMAT
```

- **One commit per session** (`Session 1: the bridge at Leighlin`), plus a tag `session-01`. The git log is the chronicle, and any earlier state is a checkout away.
- **Players** can keep their sheets in the fork and send changes as pull requests, or the referee commits sheets exported from the Companion.
- **Publishing the fork** with the same Action gives the table a live campaign site. A later viewer version will overlay `state/` (explored hexes, cleared sites) on the module maps.
- **Privacy**: a fork can be private. Referee-only notes go in `campaign/secret/`, and the build never publishes that folder.

## 8. The built site

Building `modules/<id>` writes:

```
<id>/index.html              the viewer
<id>/module.json             the manifest (format "mm-module/1")
<id>/maps/world.svg, maps/p-*.svg
<id>/print/atlas.pdf, print/exploration.pdf
```

The manifest contains `format`, `id`, `title`, `version`, `license`, `scales`, `books`, `world`, `atlas`, `exploration`, `sites`, `links` and `print`. `world` holds the map, its pixel geometry and every hex's terrain. `atlas` has one entry per page, with its centre, radius, neighbours and sites. `exploration` has one entry per page, with its map, title, book and sites with their pixel positions. `sites` gives each site's slug, kind, book, county, latitude and longitude, world hex, atlas page and exploration page. The web viewer, the PDFs and the manifest come from one build and carry the same `version` (semver, plus the commit and the date), printed in each page footer. If the versions match, the three agree.

Build locally:

```
pip install -r modules/requirements.txt && npm install --prefix modules/tools playwright@1.48.2 && npx --prefix modules/tools playwright install chromium
python3 -I modules/tools/build.py modules/season-1 dist/modules/season-1
```

## 9. Compatibility and licence

A module states its licence in `mm.json` and `module.json`. Materia Mundi's own Season 1 modules are **CC0**: fork, change and republish freely. A third-party module may use any licence, but a module that says it is "Materia Mundi compatible" must follow sections 3 to 6, so that the Companion and the viewer can read it.

The map icons in `assets/tiles` are a CC0 hex tile set.
