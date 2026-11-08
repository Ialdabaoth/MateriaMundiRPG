# Building a hexcrawl module, step by step

A hands-on procedure for making your own hexcrawl that opens in the **E9 Atlas** (zoomable maps) and the **E9 Companion** (characters, creatures, dice). It describes the tools **as they exist today** (E9 Atlas 0.5.1). It is written for people who are comfortable on a command line, or who will hand it to an AI coding assistant.

The reference implementations are `modules/isle-of-mists` (Beyond the Pale: The Isle of Mists, 1422) and `modules/hansa`. The formats are in [MODULE_FORMAT.md](MODULE_FORMAT.md), [ATLAS_FORMAT.md](ATLAS_FORMAT.md) and [REALMAP.md](REALMAP.md); this file ties them into one path. The tools are CC BY 4.0 ([tools/LICENSE.md](tools/LICENSE.md)).

## What works today, and what does not

**Works:**
- A module on the **real Earth**, pushed back to a period such as 1422. Terrain comes from public elevation data (SRTM) and, optionally, land cover (ESA WorldCover). Your sites have real latitude and longitude.
- The whole zoom ladder (Region, March 24 mi, League 3 mi, Field ½ mi, Furlong 500 ft, 100-ft hex), roads, rivers, places, credits, Irish/English-style name translations, creatures, encounter maps.
- Publishing as a static website on GitHub Pages, and loading the module in the Atlas and the Companion by its web address.

**Not built yet** (specified in ATLAS_FORMAT.md, "Map scales per module"):
- Fantasy worlds with no real-Earth data, other mile lengths, other bottom hex sizes (for example 60 ft) and other level ladders (for example ACKS-style 24 / 6 / 1 mile). Today every module uses a 5000-ft mile, a 100-ft bottom hex and the standard levels.
- Print PDFs are off by default (`build.py --pdf` still makes them and needs Playwright).
- The creator app (Scribe). You edit JSON by hand, so an AI assistant is a good partner (see the end).

A fantasy map **may** be possible today by painting the March PNGs yourself over a real region used as a canvas, because painted PNGs are used as they are (step 7). That route is untested.

## 0. What you need

- A GitHub account, and a **fork** of this repository (it holds the tools, the apps and the publishing workflow).
- Python 3.10 or newer, and `pip install -r modules/requirements.txt`. For step 7 also `pip install tifffile`.
- Internet access to `s3.amazonaws.com` (elevation tiles) while the build runs. Step 7 also needs `esa-worldcover.s3.eu-central-1.amazonaws.com`.
- About 6 GB of free memory for step 7. The plain build is light (a one-county test module builds in about a minute).

## 1. Fork and clone

Fork the repository on GitHub, clone your fork, and work from its root. Keep `modules/tools`, `modules/assets`, `modules/geo`, `companion-app/`, `.github/workflows/site.yml`, `mm.json` and `links.json`. You can delete the example modules later; leave them in for now as models.

## 2. Choose your region and its borders

Pick a region that fits on one flat map and decide its period.

- **`dem`** is `[lat0, lat1, lon0, lon1]`: the 1° elevation tiles (named by their south-west corner) that cover it. The build downloads them into `modules/.cache/geo`.
- **`admin`** is a GeoJSON file of the lands you want drawn (each feature has `properties.name`). `modules/geo/admin1.geojson` already holds the Irish counties. For anywhere else, cut period lands from Natural Earth's admin-1 file with `tools/admin_lands.py`:

  ```
  python3 -I modules/tools/admin_lands.py modules/<id>/lands.json modules/geo/<id>-lands.geojson
  ```

  `lands.json` names each land and the modern regions it is made of (see `modules/hansa/lands.json`). Download `ne_10m_admin_1_states_provinces.geojson` (Natural Earth, public domain; the `natural-earth-vector` repository on GitHub carries it) into `modules/.cache/ne/`.
- **`centroid`** is a name, latitude and longitude near the middle of your land, with every coast within about 20° of it. **`extent`** is `[minlon, minlat, maxlon, maxlat]` for everything the module could ever cover. Choose it generously and once: it fixes where addresses `00`/`0000` sit, so addresses never shift as you grow the map.

## 3. Write `module.json`

Make `modules/<id>/module.json`. The id is lowercase letters, digits and hyphens. This one builds as it stands (tested): replace the names and numbers.

```json
{
  "id": "louth-test",
  "title": "Louth Test",
  "short": "Louth test",
  "version": "0.1.0",
  "license": "CC-BY-4.0",
  "credits": [
    {"what": "Elevation", "by": "SRTM, NASA", "license": "public domain"},
    {"what": "County outlines", "by": "Natural Earth", "license": "public domain"}
  ],
  "dem": [53, 54, -7, -6],
  "admin": "../geo/admin1.geojson",
  "books": [{"id": "L1", "title": "Louth", "county": "Louth", "region": "louth", "detail": "dundalk"}],
  "world": {"counties": ["Louth"], "forest": 0.3},
  "atlas": {"hex_mi": 3, "page_hex_mi": 24, "centroid": ["Ardee", 53.86, -6.54], "extent": [-7.2, 53.5, -5.9, 54.2]},
  "league": {"hex_mi": 0.5},
  "regions": {
    "louth": {"county": "Louth", "title": "Louth", "subtitle": "A test county",
              "sites": [["Dundalk", 54.0, -6.4, "town"], ["Ardee", 53.86, -6.54, "castle"], ["Monasterboice", 53.78, -6.55, "abbey"]]},
    "dundalk": {"bbox": [-6.55, 53.9, -6.2, 54.1], "hex_mi": 0.5, "agg": 3, "px": 40, "river_km2": 20, "forest": 0.3, "hill_rel": 60,
                "title": "Dundalk", "subtitle": "The town and its bay", "sites": [["Dundalk", 54.0, -6.4, "town"]]}
  }
}
```

How it fits together:
- Each **book** is one county or district. Its `region` is a key in `regions` holding that county's sites (the 3-mile map). Its `detail` is a second key in `regions` holding a half-mile overview of the area around the book's main place: a `bbox` of `[lon0, lat0, lon1, lat1]` plus the same sites. Copy the tuning numbers (`agg`, `px`, `river_km2`, `forest`, `hill_rel`) until you need to change them; `tools/hexmap.py` explains them.
- **Sites** are `[name, latitude, longitude, kind, optional note]`. Kinds: `castle town abbey tomb hill cave ruin grove camp lair mist dead`. Use real coordinates and keep distances in your text consistent with the map.
- Optional keys: `site_icons`, `site_ranks` (1, 2 or 3: how zoomed out a place first shows), `site_parents` (a gate collapses into its castle), `names` (translations), `atlas.roads` (named roads through your sites), `world`/`league` terrain tuning. All are described in MODULE_FORMAT.md section 3.

## 4. Build it

From the repository root:

```
python3 -I modules/tools/build.py modules/<id> dist/modules/<id>
```

It prints `Atlas 0.5.1 · <id> ...: N March pages, N League pages, N sites` when it works. The first run downloads the elevation tiles. Later runs reuse a build cache (`modules/.cache/build/`): editing creatures, bestiaries and encounter maps is fast, and editing `module.json` or the map inputs redraws the maps. `BUILD_CACHE=0` turns the cache off.

## 5. Preview it

Put the module in a site layout and open the Atlas through any local web server:

```
python3 -I modules/tools/build.py modules/<id> dist/modules/<id>
cp mm.json dist/mm.json
python3 -I modules/tools/atlas_app.py dist
cd dist && python3 -m http.server 8000
```

Open `http://localhost:8000/atlas/?module=<id>` for the Atlas and `http://localhost:8000/modules/<id>/` for the module viewer. (`atlas_app.py` reads `links.json` at the repository root: that is where the Patreon link in the footer comes from. Change it or set it to an empty string in your fork.)

## 6. Register the module

Add it to the repository's `mm.json` so the apps can find it:

```json
{ "id": "<id>", "path": "modules/<id>/" }
```

in the `modules` list. The publishing workflow builds every `modules/*/module.json` it finds, so you do not edit the workflow.

## 7. Make the terrain yours (optional but recommended)

The default build gives each 100-ft hex seeded, repeatable detail from the half-mile maps. For period-correct terrain from real land cover (forest, bog, farmland pushed back toward 1422) and for hand-painted maps, use the real-data route in [REALMAP.md](REALMAP.md):

```
KEEP_WORK=1 python3 -I modules/tools/build.py modules/<id> /tmp/out
python3 modules/tools/atlas_convert.py modules/<id>/module.json /tmp/out/_work /tmp/out/atlas --real
```

The first run downloads WorldCover tiles (3° squares of 30–50 MB each; a one-county test took a few minutes). `/tmp/out/atlas/terrain/*.png` holds one 8-bit indexed picture per March. Paint on them in any editor that keeps indexed colour (terrain is matched by colour). Then copy the pictures you want to keep into `modules/<id>/atlas/terrain/` and commit them. From then on every build uses them as they are, including their summary corners (repaint those too after a big change, or delete a picture and rerun `--real` to regenerate it). Tune the period rules with `atlas.real` in `module.json` (REALMAP.md lists them).

## 8. Add content

Everything below is optional and builds with the module:
- **Creatures, NPCs, factions, scenes:** any `*.json` in the module folder with a top-level `"encounters"` block, plus `bestiary/<ruleset>.json` for each ruleset's stats ([CREATURES_FORMAT.md](CREATURES_FORMAT.md)). They show in the Atlas key panel and the Companion's Campaign › Creatures.
- **Encounter maps** (5-ft squares, opened from a place): a plan file drawn with `tools/encounter_draw.py`, or your own picture ([ENCOUNTER_FORMAT.md](ENCOUNTER_FORMAT.md)). The build checks them with `encounter_check.py` and stops on a broken map.
- **Events and random tables:** d20 and d6 only ([EVENTS_FORMAT.md](EVENTS_FORMAT.md)).

## 9. Publish

1. In your fork on GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. Push to `main`. The workflow `.github/workflows/site.yml` builds the Companion app and every module, then deploys the site.
3. When it finishes you have:
   - Atlas: `https://<owner>.github.io/<repo>/atlas/?module=<id>`
   - Module viewer: `https://<owner>.github.io/<repo>/modules/<id>/`
   - Module list: `https://<owner>.github.io/<repo>/mm.json`

Pull requests build the same site without deploying, so you can check a change first.

## 10. Use it in the Companion

Open the Companion (your site's root, or the live app), go to **Campaign → Manage → Modules**, and paste your site address (`https://<owner>.github.io/<repo>/`, the place `mm.json` sits). The module's maps open under Campaign › Maps and stay usable offline once added.

## 11. Release hygiene

- Bump `version` in `module.json` (semver) and add a `CHANGELOG.md` entry in the module folder. Tool and app changes never bump a module's version.
- List every data source in `credits`. Any CC BY source must be there. The map icons in `modules/assets/tiles/` are CC BY-SA 4.0 (Hex Tiles: Fantasy by cmartins): credit them wherever the maps go. If you add OpenStreetMap data, it is ODbL.
- Keep to d20 and d6 for any random table you add.

## If something fails

- **The build stops on `fetching ...`:** the elevation download is blocked. Check your network can reach `s3.amazonaws.com`.
- **`FileNotFoundError: links.json`:** run from a full checkout; `atlas_app.py` reads `links.json` at the repository root.
- **`no admin-1 region named ...`:** a name in `lands.json` does not match Natural Earth's spelling. Look the region up in the downloaded file.
- **Out of memory in step 7:** WorldCover tiles are large (up to four at once). Use a machine with about 6 GB free, or a smaller region.
- **Your sites do not appear:** they must lie inside `extent` and inside a county in `admin`. Check latitude and longitude are not swapped.

## Working with an AI coding assistant

Hand it these files first: this one, [MODULE_FORMAT.md](MODULE_FORMAT.md), [ATLAS_FORMAT.md](ATLAS_FORMAT.md), [REALMAP.md](REALMAP.md) and `modules/hansa/module.json` as an example. Then give it a brief like:

> Make a new module in this repository called `<id>`, set in `<place>` in `<year>`. Follow `modules/BUILDING_A_MODULE.md`. Create `module.json` with real coordinates for these places: `<list>`. Build it, preview it, fix any errors, add it to `mm.json`, and tell me the local preview address.

Check what it produces: real coordinates, sensible site kinds, distances that agree with the map, credits for every data source, and a version bump when you change a published module.
