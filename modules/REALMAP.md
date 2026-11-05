# Making a campaign map from real-world data

How to start a new mytho-historical campaign module's E9 Atlas map (ATLAS_FORMAT.md) from real land cover and elevation, pushed back to the module's period. This is the first step of every new campaign module in the E9 development arc. The tools are plain Python and the result is ordinary PNGs you can repaint.

## What you need

The tools are CC0 (tools/LICENSE.md): use them for your own modules freely.

- Python 3.10+ with `pip install -r modules/requirements.txt tifffile`
- A module folder with a `module.json` (see MODULE_FORMAT.md): books, regions with sites, `dem` (the 1° elevation tiles to fetch), `admin` (county borders), and the `atlas` block below.
- Internet access to `elevation-tiles-prod.s3.amazonaws.com` (SRTM) and `esa-worldcover.s3.eu-central-1.amazonaws.com` (WorldCover). The tools fetch and cache the tiles in `modules/.cache/`. WorldCover tiles cover 3° × 3° and are 30–50 MB each.

## module.json

```json
"atlas": {
  "hex_mi": 3, "page_hex_mi": 24,
  "centroid": ["Uisneach", 53.489, -7.561],
  "extent": [-10.7, 51.4, -5.4, 55.45],
  "real": {"modern_water": [[53.13, -6.55, 4]], "bog_east_of": -6.75}
}
```

- `centroid` is the region's Dymaxion face centre: a traditional or geographic centre, with every coast of the region within about 20° of it. Separate landmasses get their own module and centroid.
- `extent` is the whole land the region could ever cover (`[minlon, minlat, maxlon, maxlat]`). It fixes where the labels `00` and `0000` sit, so addresses never shift as the map grows. Choose it once.
- `real` (optional) tunes the period rules for this region. It takes any key of `RULES` in `tools/realmap.py`, and `modern_water`, which lists reservoirs and other water that did not exist in the period as `[lat, lon, radius in miles]`.

## Run it

```
python3 -I modules/tools/build.py modules/<id> /tmp/out --no-pdf      # builds the old-style maps and the rivers, sites and regions
KEEP_WORK=1 ... (same)                                                 # keep /tmp/out/_work for the next step
python3 modules/tools/atlas_convert.py modules/<id>/module.json /tmp/out/_work /tmp/out/atlas --real
```

`/tmp/out/atlas` then holds `map.json` and `terrain/<march>.png`. Open `atlas/index.html` through any local web server, for example `python3 -m http.server` in `/tmp/out`.

## The period rules (realmap.py)

For each 100-ft hex the tool reads WorldCover over the hex (25 samples, so hedgerow trees don't count as forest), the elevation and a smoothed slope, and the distance to the module's own settlements (its castle, town, abbey and camp sites). Then:

| Real data | Becomes |
|---|---|
| no data offshore, or water at sea level | sea |
| water above sea level | lake or river (unless listed in `modern_water`) |
| wetland, moss, bare ground (mostly cut-over peat in Ireland) | bog |
| flat, low, open ground in the bog belt (`bog_slope`, `bog_max_m`, `bog_east_of`) | bog, in patches |
| tree cover | forest |
| shrubland, or farmland that is a third trees | light woods |
| farmland and modern towns near settlements (`clear_mi`) | grassland (farmland) |
| farmland far from settlements (`wild_mi`, `wild_forest`) | more and more forest and light woods, in patches |
| above `hills_m` or steeper than `hills_slope` | hills (forest stays forest) |
| above `mount_m` | mountains |

These rules suit Ireland around 1420. Another region or period needs its own values: a drier land might drop the bog belt, and an older period might push `wild_forest` up.

## Then edit by hand

The PNGs are the map. Paint them in any editor that keeps 8-bit indexed colour (terrain is matched by colour, so the palette order doesn't matter). Repaint the League and Field summary corners too if you change a lot, or rerun the converter on your painted PNGs. To make the map yours, copy the PNGs into `modules/<id>/atlas/terrain/` and commit them. From then on every build uses those masters as they are, including their summary corners (so after a big repaint, repaint the corners too, or delete a master and rerun `--real` to regenerate that March). Beyond the Pale's masters were made this way on 2026-11-05.

## Credits and licences

Credit the sources wherever the map is shown:
- ESA WorldCover 2021 v200 (© ESA WorldCover project / contains modified Copernicus Sentinel data, CC BY 4.0)
- SRTM elevation (NASA, public domain)
- Hex tile art by C. Martins (CC BY-SA 4.0; edited icons by Heph)

If you add OpenStreetMap data later (rivers, coast, roads), it is ODbL. That share-alike licence applies to map data derived from OSM, so keep those derived files open.

## Not yet

- **Rivers.** They still come from the elevation data. OpenStreetMap rivers need `download.geofabrik.de` to be reachable.
- **Other worlds.** Mars (MOLA/HRSC elevation) and Venus (Magellan) are planned, with much more invented detail.
