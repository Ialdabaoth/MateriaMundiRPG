# E9 Atlas map format (draft, Atlas 0.2.x)

How the E9 Atlas stores a region so the browser can draw any hex at any zoom on demand.
Designed with Heph on 2026-11-05. Status: **draft**. The converter (`tools/atlas_convert.py`, Atlas 0.2.2) writes this format from today's maps on every build, into `atlas/` next to the viewer; the browser renderer (`tools/atlas.html`, Atlas 0.2.3) draws it at `atlas/index.html` as a preview next to the current viewer. Rule (Heph 2026-11-05): a click always zooms in one level, centred on the hex clicked; at Field level only a point of interest zooms further (to an Encounter map, not built yet). The build tools still read `module.json` (see MODULE_FORMAT.md).

A map is one JSON file plus one 8-bit indexed PNG per March. You paint terrain in any image editor; everything else is in the JSON.

## Units and zoom levels

The mile is exactly 5000 ft. Every hex is flat-topped and is measured flat to flat.

| Level | Hex size | 100-ft hexes across |
|---|---|---|
| Region | a collection of Marches | |
| March | 24 miles | 1200 |
| League | 3 miles | 150 |
| Field | 1/2 mile | 25 |
| 100-ft hex | 100 ft | 1 |
| Encounter | 5-ft squares, keyed to a point of interest | |

## The lattice

The whole region shares one grid of 100-ft hexes, with flat tops and **odd columns shifted down half a hex**. A hex's global address is `(C, R)`, and its centre in feet is

    x = C * 86.6025   (100 * sqrt(3) / 2)
    y = (R + 0.5 * (C mod 2)) * 100

with x running east and y running south from the map's `origin` (see the JSON). Because the mile is 5000 ft, every larger hex centre falls exactly on a lattice hex:

| Level | Hex (i, j) has its centre at lattice hex |
|---|---|
| March | C = 1200 i, R = 1200 j + 600 (i mod 2) |
| League | C = 150 i, R = 150 j + 75 (i mod 2) |
| Field | C = 25 i, R = 25 j + 12 (i mod 2) |

A lattice hex belongs to the March, League or Field whose centre is nearest. On an exact tie, the **higher** i wins, then the higher j. With that rule every March owns columns Cm − 800 to Cm + 799 and rows Rm − 600 to Rm + 599, so its hexes fit its PNG exactly, and every March holds exactly 64 Leagues and 2304 Fields (by their centres), all of which fit the summary blocks below (checked by the converter on 2026-11-05; the first draft said "lower", which left one row of each March's hexes outside every PNG).

## Terrain PNGs: one per March

Each March is a **1600 × 1200** 8-bit indexed PNG. Pixel (x, y) is lattice hex

    C = Cm - 800 + x,   R = Rm - 600 + y

where (Cm, Rm) is the March's centre hex. Pixel columns keep the global odd/even parity, so odd pixel columns sit half a hex lower. In an ordinary image editor the map therefore looks about 15% too wide and slightly staggered. The Atlas editor will show it true to shape.

Neighbouring March PNGs overlap at the corners. Only pixels that belong to this March (nearest-centre rule) are read. The four corners outside the March hexagon are each about 400 × 600 pixels of dead space, and they hold the summaries:

| Pixels | Holds |
|---|---|
| (0, 0) | the March's own terrain |
| x 2–12, y 2–10 (11 × 9), upper left | one pixel per League. Block pixel (u, v) is League i = iL − 5 + u, j = jL − 4 + v, where (iL, jL) is the League under the March centre |
| x 1533–1597, y 1149–1197 (65 × 49), lower right | one pixel per Field. Block pixel (u, v) is Field i = iF − 32 + u, j = jF − 24 + v, where (iF, jF) is the Field under the March centre |

A block pixel for a League or Field whose centre belongs to a neighbouring March is left as colour 0 ("none"). The converter gives each 100-ft hex seeded detail on top of the source maps: borders between parent hexes wander up to 900 ft, and each terrain becomes a natural mix (glades in forest, copses in grassland), repeatable because the noise is keyed to the global lattice. The tools fill each summary with the **most common** terrain among all its member hexes (a League or Field can straddle two Marches), never a colour average, and colour 0 never wins while any terrain is present. A painter may then edit a summary by hand, and the renderer uses each level's own summary. That lets you paint a coarse map first and refine it later.

### Palette

Terrain is matched by **colour**, not by palette index, because some editors reorder palettes when they save. Colour 0 (`#000000`) means none or outside. Up to 255 other colours can each name a terrain type in the JSON.

## Projection: Dymaxion, one face per region

Decided by Heph on 2026-11-05: the Atlas uses **Buckminster Fuller's Dymaxion projection** (the icosahedral layout, using Robert W. Gray's published transform), so one scheme covers every setting from Leinster to Francia to Barsoom. Two rules:

1. **Each major region gets its own centroid.** The icosahedron is turned so that one face's centre (where the triangle touches the planet) sits on the region's centroid, with true north pointing up the page there. That whole region then lives on one flat face with one 100-ft lattice.
2. **Seams always fall in the middle of the ocean.** A face reaches about 21° of arc (about 2,300 km) from its centre before the nearest edge, so a region the size of Ireland never touches a seam. Separate regions (Britain, Francia) get their own centroids and faces, and maps join them across water.

For Ireland the centroid is the **Hill of Uisneach**, Westmeath (53.489° N, 7.561° W), the traditional centre of the island. Every Irish coast lies within 2.5° of it. Measured with the converter's transform (tools/dymaxion.py), the local scale error is under 0.1% around Dublin, under 0.5% anywhere in Leinster and under 0.8% at the island's far tips (Malin Head, Mizen Head), and distances from Uisneach are true to within 0.4%. Equirectangular, by contrast, reaches 2.4% across Leinster alone. One face vertex points due north.

`origin` names the centroid and gives the position of lattice hex (0, 0) in feet on that face. The scale is set so that distances at the centroid are true (mean Earth radius 6,371,008.8 m).

`labels` gives the March and League lattice (i, j) that are labelled `00`/`0000`: the top-left March and League of the region's fixed extent (module.json `atlas.extent`, for Ireland the whole island), so labels never shift when a map grows. March PNGs are named by their label, e.g. `terrain/0807.png`.

## The map JSON

Sections appear in this order: base terrain, then rivers and roads, then region names, then points of interest.

```json
{
  "format": "e9-atlas/1",
  "id": "isle-of-mists",
  "title": "Beyond the Pale: Leinster, 1422",
  "names": {"An Life": {"en": "Liffey"}},
  "origin": {"projection": "dymaxion", "centroid": {"name": "Uisneach", "lat": 53.489, "lon": -7.561}, "x_ft": 0, "y_ft": 0},
  "labels": {"march": [-7, -7], "league": [-55, -49]},

  "terrain": {
    "types": [
      {"color": "#7fae4e", "id": "grass", "name": "Grassland", "tile": "bg-green", "travel": 1},
      {"color": "#2e6b2e", "id": "forest", "name": "Forest", "tile": "bg-green", "icon": "forest", "travel": 2},
      {"color": "#6e6a5a", "id": "bog", "name": "Bog", "tile": "bg-grey", "icon": "swamp", "travel": 2},
      {"color": "#4f86a8", "id": "sea", "name": "Sea", "tile": "bg-blue", "travel": null}
    ],
    "marches": [{"id": "0708", "i": 0, "j": 1, "png": "terrain/0708.png"}],
    "overrides": {"0302:1506": "forest"}
  },

  "rivers": [{"name": "An Life", "class": 3, "points": [[41250, 88010], [41320, 88400]]}],
  "roads": [{"name": "Slí Chualann", "class": "roman", "points": [[50100, 60200], [50900, 61000]]}],
  "crossings": [{"hex": [640, 512], "kind": "ford"}],

  "regions": [{"name": "Cill Dara", "kind": "county", "label": [62000, 140000], "outline": [[0, 0]]}],

  "pois": [{"id": "ceanannas-mor", "name": "Ceanannas Mór", "kind": "abbey", "icon": "church", "hex": [812, 410], "ft": [12, -30], "book": "B2"}]
}
```

- **Points are in feet** from `origin`: `[x east, y south]`. Rivers and roads are polylines that the renderer smooths, so their points need no splines. A river's `class` sets its drawn width.
- **Roads** come in three classes (Heph 2026-11-05): `roman` (a size class named for familiarity, not history: any great paved or engineered highway; in Ireland, the five ancient slighe from Tara), `local` and `trail`. Where a road crosses a river the renderer draws a crossing icon: a bridge on a `roman` road, a ford on the others, unless a `crossings` entry names the hex and the kind (`bridge` or `ford`). Heph is supplying the bridge and ford icons.
- **POI positions** (Heph 2026-11-05) are a lattice hex `"hex": [C, R]` plus an optional `"ft": [east, south]` offset in feet from that hex's centre (omitted = the centre). The hex gives every level its address for free (which Field, League and March the place is in); the offset places it exactly, for Encounter maps. Tools keep the offset within the hex (at most 50 ft from the centre) by moving the point to the nearest hex.
- **`names`** holds the Language box's translations, keyed by the name as drawn, as in module.json today.
- **`overrides`** fixes a single hex at any level without repainting (`<march>:<league>`, and later deeper addresses).
- An optional **elevation PNG** per March, 16-bit greyscale with the same geometry, can come later for hill shading.

## Hex addresses

Decided by Heph on 2026-11-05: **`#world:CCRR:CCRR`**. The first `CCRR` is the League (3-mile hex), and the second is the 100-ft hex inside that League. `#world:CCRR` alone means the whole League.

**Labels.** Each column or row label is exactly two characters: `00`–`99`, then `A0`–`A9`, `B0`–`B9` and so on. The letters `I`, `O` and `Q` are never used, so 23 letters give 330 values (0–329). For example, 100 = `A0`, 147 = `E7`, 200 = `L0`.

| Part | Counts | Range used |
|---|---|---|
| League column, row | League lattice (i, j), shifted so the region's top-left League is `0000` | Ireland needs about 70 columns × 100 rows |
| 100-ft hex in the League | lattice hexes from the League's bounding box: column 0 = League centre C − 100, row 0 = centre R − 75 | columns `00`–`K9` (0–199), rows `00`–`E9` (0–149), 22,500 hexes per League; the centre hex is column `A0`, row `75` → `A075` |

Parity carries through: column 0 is an even global column, so odd columns sit half a hex lower, as everywhere else. With the tie rule above every League owns exactly columns 0–199 and rows 0–149 of its box (checked with a script). Tools write the canonical form (upper case, with the hex inside the League that owns it), and the viewer reads either case. Field and March are derived from the address, so they need no address of their own.

**Old links.** Today's `#world:CCRR`, `#march-N` and `#l-CCRR` addresses count 3-mile hexes on the old grid. When the switch happens, each one becomes an alias to the new League whose centre is nearest, so links already in the Companion and the books keep working.

## Open questions

None at the moment.
