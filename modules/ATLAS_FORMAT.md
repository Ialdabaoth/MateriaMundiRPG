# E9 Atlas map format (draft, Atlas 0.2.x)

How the E9 Atlas stores a region so the browser can draw any hex at any zoom on demand.
Designed with Heph on 2026-11-05. Status: **draft**; the build tools still read `module.json` (see MODULE_FORMAT.md) until the converter and renderer land.

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

A lattice hex belongs to the March, League or Field whose centre is nearest. On an exact tie, the lower i wins, then the lower j. With that rule every March holds exactly 64 Leagues and 2304 Fields, all of which fit the summary blocks below (checked with a script on 2026-11-05).

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

A block pixel for a League or Field that belongs to a neighbouring March is left as colour 0 ("none"). The tools fill each summary with the **most common** terrain among its member hexes, never a colour average. A painter may then edit a summary by hand, and the renderer uses each level's own summary. That lets you paint a coarse map first and refine it later.

### Palette

Terrain is matched by **colour**, not by palette index, because some editors reorder palettes when they save. Colour 0 (`#000000`) means none or outside. Up to 255 other colours can each name a terrain type in the JSON.

## The map JSON

Sections appear in this order: base terrain, then rivers and roads, then region names, then points of interest.

```json
{
  "format": "e9-atlas/1",
  "id": "isle-of-mists",
  "title": "Beyond the Pale: Leinster, 1422",
  "names": {"An Life": {"en": "Liffey"}},
  "origin": {"lat": 53.4, "lon": -7.6, "projection": "local-equirectangular"},

  "terrain": {
    "types": [
      {"color": "#7fae4e", "id": "grass", "name": "Grassland", "tile": "bg-green", "travel": 1},
      {"color": "#2e6b2e", "id": "forest", "name": "Forest", "tile": "bg-green", "icon": "forest", "travel": 2},
      {"color": "#6e6a5a", "id": "bog", "name": "Bog", "tile": "bg-grey", "icon": "swamp", "travel": 2},
      {"color": "#4f86a8", "id": "sea", "name": "Sea", "tile": "bg-blue", "travel": null}
    ],
    "marches": [{"id": "0302", "i": 0, "j": 1, "png": "terrain/0302.png"}],
    "overrides": {"0302:1506": "forest"}
  },

  "rivers": [{"name": "An Life", "class": 3, "points": [[41250, 88010], [41320, 88400]]}],
  "roads": [{"name": "Slí Chualann", "class": "highway", "points": [[50100, 60200], [50900, 61000]]}],

  "regions": [{"name": "Cill Dara", "kind": "county", "label": [62000, 140000], "outline": [[0, 0]]}],

  "pois": [{"id": "ceanannas-mor", "name": "Ceanannas Mór", "kind": "abbey", "icon": "church", "at": [70310, 41020], "book": "B2"}]
}
```

- **Points are in feet** from `origin`: `[x east, y south]`. Rivers and roads are polylines that the renderer smooths, so their points need no splines. A river's `class` sets its drawn width.
- **`names`** holds the Language box's translations, keyed by the name as drawn, as in module.json today.
- **`overrides`** fixes a single hex at any level without repainting (`<march>:<league>`, and later deeper addresses).
- An optional **elevation PNG** per March, 16-bit greyscale with the same geometry, can come later for hill shading.

## Open questions

1. **Origin and projection:** use one local equirectangular projection at the region's centre (fine at county scale), or the DEM's own grid?
2. **Hex addresses:** today's `#world:CCRR` addresses count 3-mile hexes from the old grid's corner. They need a fixed mapping to (March, League) before the switch, kept as aliases.
3. **Road classes and widths**, and whether roads get their own icons for bridges and fords.
4. **POI positions:** an `at` in feet, or a lattice hex `(C, R)`?
