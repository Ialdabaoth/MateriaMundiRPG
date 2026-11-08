# Materia Mundi open module protocol (`mm-module/1`)

An open way to publish adventures, regions and campaigns for **Materia Mundi** and **E9** so they can be played entirely in a web browser or the Companion app, with no VTT, and printed as books from the same source.

The rules are simple. A module is a **git repository**. Building it produces a **static website**: a map viewer, print-ready PDFs and a `module.json` manifest the Companion reads. GitHub with GitHub Pages is the default host, but any git host and any static web host will do. A referee runs a **campaign by forking** a module repository. The campaign's live record (sessions, explored hexes, character sheets) is committed to the fork, so git history becomes the campaign chronicle.

This repository is the reference implementation: `modules/isle-of-mists` (Beyond the Pale: The Isle of Mists, 1422) and the build tools in `modules/tools`.

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

A publisher may hold several modules in one repository. Module ids are lowercase ASCII with hyphens (`isle-of-mists`, `hansa-1`).

## 2. Discovery: `mm.json`

At the repository root, and copied to the root of the published site:

```json
{
  "format": "mm-repo/1",
  "name": "Materia Mundi: Beyond the Pale",
  "publisher": "Heph",
  "systems": ["materia-mundi", "e9"],
  "license": "CC-BY-4.0",
  "modules": [{ "id": "isle-of-mists", "path": "modules/isle-of-mists/" }]
}
```

The Companion adds a repository from its published URL. It reads `mm.json` and then each module's built `module.json`.

## 3. Module source: `modules/<id>/module.json`

| Field | Meaning |
| --- | --- |
| `id`, `title`, `short`, `version` | `version` is semver. Breaking changes to ids (section 5) need a new major version. |
| `license` | SPDX id. Required. |
| `credits` | Optional list of the data sources the module's maps use, `[{what, by, license, url?}]` (for example castle positions, CC BY 4.0). Copied to the built `module.json`; the E9 Atlas shows them under Credits in its footer and the module viewer in its footer (Atlas 0.5.0). Any CC BY source must be listed here. |
| `dem` | `[lat0, lat1, lon0, lon1]`: the SRTM 1° tiles (south-west corners) the terrain comes from. The build fetches them. |
| `admin` | Path to the GeoJSON boundaries (`properties.name` is the region name). |
| `books` | Ordered list: `{id, title, county, region, detail}`. `region` names the book's 3-mile region and `detail` its half-mile overview. |
| `world` | Terrain settings for the one 3-mile world map (`counties`, `forest`, `bog_east_of`, `bog_north_of` …). |
| `atlas` | `{hex_mi: 3, page_hex_mi: 24}`: the March hex and the Region (page) hex. Optional `centroid: [name, lat, lon]` and `extent: [minlon, minlat, maxlon, maxlat]` turn on the E9 Atlas format (ATLAS_FORMAT.md): the Dymaxion face centre, and the fixed area whose top-left March and League are labelled `00` and `0000`. Painted March PNGs in `<module>/atlas/terrain/<march>.png` are the masters and are used as they are (see REALMAP.md). Optional `travel` (ATLAS_FORMAT.md, Travel) and `roads: [{name, class, via, crossing?}]`, where `class` is `roman`, `local` or `trail` and `via` lists site names or `[lat, lon]` points (ATLAS_FORMAT.md, Roads). |
| `league` | `{hex_mi: 0.5, overrides: {county: {terrain settings}}}`. |
| `site_icons` | Optional `{site name: icon}` overrides; an icon is a file name (without `.png`) in `assets/tiles/icons/`. Without one, a site uses its kind's icon (grove = great tree, abbey = church). |
| `site_ranks` | Optional `{site name: 1, 2 or 3}`: the zoom a place first shows at in the Atlas. 1 = major (Region view), 2 = notable (March view), 3 = minor (League view down). Without one, towns are 1, abbeys 2 and other sites 3 (ATLAS_FORMAT.md, Place ranks). |
| `site_parents` | Optional `{sub-place name: parent name}`: PoI hierarchies (ATLAS_FORMAT.md). A sub-place (a cave mouth, a city gate) collapses into its parent when zoomed out, and the Atlas key lists it under its parent. Any depth; both names must be sites of the module. |
| `languages` | Optional `{code: label}`, e.g. `{"ga": "Gaeilge", "en": "English"}`, the language the names are drawn in first. The Language box in the Atlas, the viewer and the Companion offers these, and hides itself with fewer than two. Without it, a module with `names` gets the old Gaeilge/English pair. Changing it does not redraw the maps. |
| `names` | Optional label translations `{name as drawn: {<language code>: "..."}}`. The viewer's Language box swaps every map label, page title and list entry that matches a key; names without an entry stay as drawn. Copied to the built `module.json`. |
| `regions` | Named map regions. Each has `sites: [[name, lat, lon, kind, note?]]` plus terrain settings. |

Site `kind` is one of `castle town abbey tomb hill cave ruin grove camp lair mist dead`. A new kind needs an icon in `assets/tiles/icons` and an entry in the build's icon table.

Every site has a **real latitude and longitude**. Distances in the text must agree with the maps. A **mile is exactly 5,000 feet** (1.524 km), so a 3-mile hex is 4.572 km across its flats.

## 4. Zoom levels, scales and pages (fixed for every module)

Every map is a flat-top hex grid, odd columns shifted down, hexes numbered `CCRR` from `0101`. A mile is 5,000 feet. Each level divides one hex of the level above it.

| Level | What it is | Hex | Printed | Page |
| --- | --- | --- | --- | --- |
| **Region** | the whole module, a collection of 24-mile hexes | 24 mi | web only | the `#world` map, with the 24-mile hexes drawn over it |
| **March** | one 24-mile hex divided into 3-mile hexes (8 across) | 3 mi (1 league, about 1 hour on foot) | 1 in per hex | one atlas page per 24-mile hex that contains module land |
| **League** | one 3-mile hex divided into half-mile hexes (6 across) | ½ mi (2,500 ft, about 10 minutes on foot) | 1 in per hex | one page per 3-mile hex that holds a point of interest; every site in that hex shares the page |
| **Field** | one half-mile hex divided into 100-foot hexes (25 across) | 100 ft | 1 in per hex | planned |
| **Encounter** | a map of 5-foot squares of any size, keyed to a point of interest inside a Field hex | 5 ft square | 1 in per square | planned |

The page layout is 11 × 8.5 in landscape with a ¼ in border, the map (8.75 × 8 in) on the left and the legend on the right. A page outlines its own hex and veils everything outside it; the neighbouring hexes still render in full, with their numbers and page references at the edges. Hexes beyond the module's boundary render wherever they fall on a page, but they don't get pages of their own.

A League page is built from its March hex: the half-mile grid is centred on the 3-mile hex's centre, and in each 3-mile hex on the page (the League and its neighbours) the best-suited three in five half-mile hexes take that hex's March terrain (the highest ground for hills, the flattest for bog, and so on), so the two maps agree.

Travel: forest and light woods both double travel time, and a Survival roll finds a path at normal speed (Easy in light woods, Hard in forest).

## 5. Identifiers and links (stable within a major version)

- **Site slug**: the site name, accents stripped, lowercase, non-alphanumerics → `-` (`Dinn Ríg` → `dinn-rig`).
- **League key**: `l-` + the number of its 3-mile hex (`l-1330`).
- **March page**: its number, `1…n`, ordered north to south and then west to east.
- **Viewer links**: `#world`, `#march-7`, `#l-1330`, `#l-1330--droichead-leithghlinne`. Links from version 0.1 (`#atlas-7`, `#p-<site>`, `#p-<site>--<site>`) still open the matching page, through the manifest's `aliases`.
- **Hex addresses**: `<map>:<hex>`, where map is `world` or a League key: `#world:1330` (a 3-mile hex), `#l-1330:0607` (a half-mile hex in that League; the League's centre hex is 0907 on every League page). These are the same keys as `campaign/state/hexes.json`. Every map uses the world map's hex geometry (`world.hex_px`, `world.col_px`, `world.origin_px`).
- **Render modes**: `?mode=map` shows only the map, with zoom buttons; `?mode=atlas` shows only the page list and search. The plain viewer shows both. An app could show the two modes in separate frames (the Companion did until 0.5.2; it now embeds the E9 Atlas, and the viewer forwards to the Atlas when the module has an Atlas map unless `?mode=` or `?viewer=` is set): a pick in the atlas frame posts `{"event": "select", "hash"}` instead of navigating, the app sends `{"show": hash}` to the map frame, and sends `{"current": hash}` back to the atlas frame so it highlights the page being shown. `?mode=key` shows only the map key, drawn like the Atlas app's side panel (terrain in view, places in view with their icons, creatures here); the map frame posts `{"event": "key", "hash", "terrain", "places", "creatures"}` whenever the view changes, the app forwards `{"key": {...}}` to the key frame, and a place picked there posts `{"event": "select", "hash"}`. Adding `&tools=host` to a map frame hides its own language, hex-edge and zoom controls so the app can draw them: the viewer posts `{"event": "tools", "lang", "langs": [{"value", "label"}], "edges", "zoom"}` (zoom in percent) on load and on every change, and takes `{"tools": true}` (send state now), `{"lang": "en"}`, `{"edges": false}` and `{"zoom": "in" | "out"}`.
- **Embedding**: the viewer can sit in an iframe. It posts `{"type": "mm-viewer", "event": "view" | "hex" | "select", "module", "version", "hash", "map"?, "title"?, "small"?, "hex"?, "scale"?, "sites"?, "terrain"?, "terrainName"?}` to its parent whenever the reader moves or taps a hex. The parent may post `{"type": "mm-viewer", "show": "#world:0706"}` to open a link, and `{"type": "mm-viewer", "marks": [{"map": "world", "hex": "0706", "label": "P"}]}` to place markers, such as where a party stands.

If a later version renames a site, add `"aliases": {"old-slug": "new-slug"}` to `module.json` so old links and campaign notes keep working. If a module changes its id, list the old ids in `"moved_from"`: the build leaves a page at each old address that forwards to the new one, with its query and link intact.

## 6. Tables and creatures

- Random tables use **d20 and d6 only**. A big table is a d6 choosing among d20 sub-tables, 120 entries in all. JSON: `{"id", "title", "die": "d20" | "d6", "rows": [{"roll": [lo, hi], "text", "site"?: slug}], "sub"?: {"1": table, …}}`.
- Creatures reference the Materia Mundi Compendium by name and page wherever possible (`{"name": "Athach", "base": "Ogre", "page": <Compendium page>, "changes": "…"}`). Give a full stat block only for something new.
- Creatures, NPCs, factions and encounters (fiction in encounters.json, mechanics in bestiary/<ruleset>.json, templates with replace and adjust) are drafted in CREATURES_FORMAT.md.

## 7. Campaigns: fork, play, commit

A referee **forks** a module repository and adds a `campaign/` folder. Module authors never write to `campaign/`, so the referee can pull upstream fixes (`git pull upstream main`) without conflicts.

```
campaign/
  campaign.json              {"format": "mm-campaign/1", "modules": ["isle-of-mists"], "start": "1422-05-01", "referee": "…"}
  chronicle/2026-11-08-session-01.md   what happened, written after each session
  state/hexes.json           {"<map>:<hex>": {"explored": true, "notes": "…"}}   map = "world" or a League key
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
<id>/maps/world.svg, maps/l-*.svg
<id>/print/atlas.pdf (March pages), print/leagues.pdf  (only with build.py --pdf: print PDFs are paused until the print process is settled, Heph 2026-11-07)
<id>/atlas/map.json, atlas/terrain/<march>.png (E9 Atlas format, when atlas.centroid is set)
<id>/atlas/tiles/ (the tiles the E9 Atlas draws this module with)
<id>/atlas/index.html       forwards to the E9 Atlas app at <site>/atlas/?module=<id>, keeping the #link
```

The **E9 Atlas** (Atlas 0.3.0) is one app for the whole site, at `<site>/atlas/` (`tools/atlas_app.py` writes it). It reads the site's `mm.json`, shows which module is loaded, and its Modules button loads another one. `?module=<id>` picks a module; links are `#world`, `#march:MMMM`, `#world:LLLL[:HHHH]`.

The manifest contains `format`, `id`, `title`, `version`, `license`, `scales`, `books`, `world`, `marches`, `leagues`, `sites`, `aliases`, `links` and `print`, and `atlas_map` (`atlas/map.json`) when the module has an E9 Atlas map. `scales` gives `mile_ft` (5000) and the hex size of each zoom level. `world` holds the Region map, its pixel geometry and every 3-mile hex's terrain. `marches` has one entry per atlas page, with its 24-mile hex, centre, radius, neighbours and sites. `leagues` has one entry per League page, with its 3-mile hex, map, title, book, March terrain, centre and sites with their pixel positions. `sites` gives each site's slug, kind, book, county, latitude and longitude, world hex, March page and League. `aliases` maps old page keys to League keys. A module with creatures (CREATURES_FORMAT.md) also has `encounters` (the merged fiction file, `encounters.json`) and `bestiary` (`{"<ruleset>": "bestiary/<ruleset>.json"}`); the Companion's Creatures › Add list offers them, and the viewer and the E9 Atlas list who lives in a tapped hex, each name opening an index card (`atlas/creatures.json` holds the resolved list for the Atlas). The web viewer, the PDFs and the manifest come from one build and carry the same `version` (semver, plus the commit and the date), printed in each page footer. If the versions match, the three agree.

Build locally:

```
pip install -r modules/requirements.txt && npm install --prefix modules/tools playwright@1.48.2 && npx --prefix modules/tools playwright install chromium
python3 -I modules/tools/build.py modules/isle-of-mists dist/modules/isle-of-mists
```

## 9. Compatibility and licence

A module states its licence in `mm.json` and `module.json`. Materia Mundi's own modules are **CC BY 4.0**: fork, change and republish freely, as long as you credit Heph (Bakagaijin Productions). A third-party module may use any licence, but a module that says it is "Materia Mundi compatible" must follow sections 3 to 6, so that the Companion and the viewer can read it.

The map icons in `assets/tiles` are [Hex Tiles: Fantasy](https://cmartins.itch.io/hex-tiles-fantasy) by cmartins, licensed CC BY-SA 4.0. The viewer and the Companion credit them; keep that credit in anything built from them.
The bonus Desert, Forest, Mountain and Tundra packs in `assets/tiles/packs` (and their keyed-out copies in `assets/tiles/features`) are art by C. Martins, licensed CC BY. Credit "Art by C. Martins" wherever they appear.
