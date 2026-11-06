# E9 Encounter map format (draft)

How a module stores its **Encounter maps** (the 5-ft-square battle maps below the Field level of the E9 Atlas), how points of interest and scenes point into them, and how they can grow into a virtual tabletop later.
Designed with Heph on 2026-11-05. Status: **draft**. Map files, the drawing tool and the checker exist (section 12); the Atlas and the module viewer open maps from points of interest (Atlas 0.2.12). Atlas 0.4.x is VTT and referee-tool integration (Heph 2026-11-06): 0.4.0 fills in walls, doors and lights and tidies the format for Universal VTT import, export and links into VTTs (sections 7, 11 and 13). Sits under ATLAS_FORMAT.md (the hex levels) and beside CREATURES_FORMAT.md (who is there) and EVENTS_FORMAT.md (what happens).

## 1. The idea in one paragraph

An Encounter map is **its own file**, a grid of 5-ft squares of any size whose picture is made of one or more **image layers** of any size: a Dungeon Scrawl export, a Dungeondraft render, a scanned hand drawing, or several of them stitched together. Points of interest and scenes don't own maps. They **point into** one, naming a map and a rectangle of its squares, so five rooms of one dungeon can share a map while a crossroads ambush gets its own. A map may be **anchored** to the world so the Field view can outline it, or float free (a dungeon level). Where a map has no image, the Atlas draws **generated ground** from the 100-ft terrain underneath, so a point of interest is never blank. Tokens, light and fog are **reserved, not built**: the file already has room for walls, doors and lights in the shape Universal VTT uses, so a later Companion play surface, and import and export with other VTTs, need no format change (Heph 2026-11-05).

## 2. Files

```
modules/<module-id>/
  encounter-maps/
    <map-id>.json            one Encounter map (this spec)
    <map-id>/...             its images, any names, any sizes (PNG, JPG or WebP)
campaign/
  encounter-maps/<map-id>.json        a referee's own maps, or a replacement for a module map with the same id
  encounter-maps/<map-id>.state.json  play state, later: tokens, revealed squares, open doors (section 8)
```

One map per file keeps git diffs small and lets a referee drop in a single map. Ids are lower-case slugs, unique within the module. The campaign layer replaces a module map with the same id on purpose, as with events (EVENTS_FORMAT.md section 2), and the load report lists each replacement.

## 3. The map file

```json
{
  "format": "e9-encounter-map/1",
  "id": "kells-priory",
  "title": "Kells Priory, the walled town",
  "size": [80, 60],
  "grid": {"ft": 5, "show": true},
  "layers": [
    {"src": "kells-priory/ground.jpg", "at": [0, 0], "px": 70},
    {"src": "kells-priory/tower-house.png", "at": [52, 8], "px": 100, "rotate": 90}
  ],
  "ground": "generate",
  "anchor": {"hex": [812, 410], "ft": [12, -30], "square": [40, 30], "rotate": 0},
  "areas": {
    "gatehouse": {"squares": [36, 52, 8, 8], "title": "Gatehouse"},
    "prior-tower": {"squares": [52, 8, 12, 12], "title": "Prior's tower"}
  },
  "links": [{"from": [60, 12], "to": {"map": "kells-priory-cellars", "square": [4, 4]}, "label": "Stair down"}],
  "walls": [], "doors": [], "lights": [], "environment": {},
  "licence": "CC0", "credit": ""
}
```

- **Squares** are counted from the top-left corner: `[x, y]` with x to the right and y down, 0-based. A rectangle is `[x, y, w, h]`. A square is `grid.ft` feet (5 by default; a module may use 10 for a big outdoor map).
- **size** is `[w, h]` in squares. Each PoI sets its own size (Heph 2026-11-05), so there is no default. If `size` is left out, it is the bounding box of the layers.
- **layers** are drawn in order, first at the bottom. Each one has a `src` path relative to `encounter-maps/`, `at` (the square its top-left corner sits on, fractions allowed), and `px` (its pixels per square). Optional fields are `rotate` (degrees clockwise), `opacity` (0–1) and `show` (`"all"`, `"referee"` for a GM-only annotation layer, or `"players"`). An image may be bigger than the map or hang off it. Only the part inside `size` is drawn.
- **ground** is `"generate"` (draw generated ground under and around the layers, section 6), `"none"` (blank parchment), or a colour. It defaults to `"generate"` when the map has an anchor and `"none"` when it doesn't.
- **anchor** (optional) pins the map to the world: the map square `square` sits on lattice hex `hex` plus an optional `ft` offset in feet from that hex's centre (a PoI has no offset; an anchor may), turned `rotate` degrees clockwise from north. Without an anchor the map floats free, like a dungeon level or a dream.
- **areas** name rectangles of squares so PoIs, scenes and keyed text can point at a room by name instead of numbers. An area may instead list several rectangles: `"squares": [[...], [...]]`.
- **links** are stairs, trapdoors and paths to another map (or another square of the same one). They let a dungeon be a stack of maps, one per level, with no extra "level" field.
- **walls, doors, lights, environment** are the play surface, in the shapes of section 7. `walls` are polylines that block sight; `doors` are `{"at": [[x, y], [x, y]], "closed": true, "secret": false}` with an optional `"locked": true`; `lights` are `{"at": [x, y], "range": squares, "colour": "#rrggbb", "intensity": 1}`. Since Atlas 0.4.0 the drawing tool fills them in for its own maps (section 12); a dropped-in picture gets them from a Universal VTT import or by hand. The Atlas map view has a **Walls** button that draws them over the picture, for checking before an export. Nothing plays on them yet (section 8).
- **licence** and **credit** belong to the map's art, because a dropped-in image can carry a different licence from the module (for example CC BY-SA if it uses Hex Tiles Fantasy art). The Atlas shows them under the map.

## 4. Pointing into a map

A point of interest in the Atlas map JSON (ATLAS_FORMAT.md, `pois`) gains an optional **`encounter`** list. Each entry is a **pointer**:

```json
{"id": "ceanannas-mor", "name": "Ceanannas Mór", "kind": "abbey", "hex": [812, 410],
 "encounter": [
   {"map": "kells-priory", "area": "gatehouse", "label": "The gate"},
   {"map": "kells-priory", "squares": [0, 0, 80, 60], "label": "Whole town"},
   {"map": "kells-priory-cellars", "label": "Cellars"}
 ]}
```

- A pointer names a `map` and either an `entrance`, an `area`, a `squares` rectangle, or neither (the whole map). `label` is what the picker shows. **A point of interest's pointer should name an entrance** (section 14.3, Heph 2026-11-06); an area pointer still works and the area acts as the entrance.
- Several PoIs may point into the same map, at the same or different squares, and one PoI may point into several maps (Heph 2026-11-05).
- A **scene** (CREATURES_FORMAT.md section 7) uses the same pointer in its `map` field instead of a bare id: `"map": {"map": "kells-priory", "area": "gatehouse"}`. A bare string still means the whole map.
- Keyed adventure text can link a room by address: **`#<module>:<map-id>`**, **`#<module>:<map-id>/<area>`**, or **`#<module>:<map-id>/x,y`** for one square. The Companion's page links and the Atlas both read these.

**In the Atlas.** At Field level a PoI with pointers can be clicked (the rule that clicks always zoom in one level, ATLAS_FORMAT.md). One pointer opens straight onto its map, centred and zoomed to the pointed squares. Several pointers show a short picker. An anchored map is also outlined on the Field view, so the referee sees how far the battle map reaches. A PoI with no pointer opens a generated map of its own 100-ft hex (section 6), so every PoI still zooms in.

## 5. Bringing in images

- **Any size, any source.** Export from Dungeon Scrawl, Dungeondraft, Inkarnate or a scanner, put the file in `encounter-maps/<map-id>/`, and set `px` to the export's pixels per square (Dungeon Scrawl and Dungeondraft both say this when exporting). Nothing has to be cut to a fixed tile size.
- **Stitching.** Several images become one map by giving each its own `at`. A ruined chapel drawn separately can sit on a generated meadow, or two halves of a big dungeon can sit side by side.
- **Universal VTT files** (`.uvtt` / `.dd2vtt`, section 7) import as a map with one layer, and their walls, doors and lights fill the reserved fields.
- **The Atlas editor** (later) gets an "Add image" button that places the layer by eye and works out `at` and `px` from two clicked grid corners, so authors never type them.
- Images are served as they are. The build may make a smaller WebP copy for phones, as it does for terrain tiles, but never changes the source.

## 6. Generated ground

When `ground` is `"generate"`, the Atlas draws the squares from the world under the map: each square takes the terrain of the 100-ft hex its centre falls in (with the seeded mix that hex already has), rivers and roads are traced across the squares from their smoothed lines, and small scatter (trees, boulders, reeds, brambles) is placed from the terrain.

- The scatter is **seeded by the square's world position**, so every viewer and every reload draws the same ground, and two overlapping maps agree where they overlap.
- Scatter comes from **d6/d20 tables** per terrain (d6 picks the subtable, d20 the feature), in an ordinary `events`-style table that a module can override. The generator rolls them with a seeded die, so a referee with the printed table can scatter a clearing by hand in the same way.
- An unanchored map has no world under it, so `"generate"` there uses the map's own `terrain` field (`"terrain": "forest"`) as if the whole map stood in one hex.
- Art for generated ground is drawn by the Atlas in its own simple top-down ink style. The cmartins hex tiles are hex-scale icons, not battle-map art, so they are not used at this level. The Atlas code and its drawing style are CC0 like the rest of the tools.

## 7. Room to grow: Universal VTT

**Universal VTT** is the JSON format that Dungeondraft exports (`.dd2vtt`, also `.uvtt`) and that Foundry VTT, Fantasy Grounds Unity, Arkenforge and others import. It holds one image, the grid size in pixels, wall lines that block sight, doors ("portals") and lights. The reserved fields in section 3 follow it on purpose so it maps almost one to one:

| Encounter map | Universal VTT (`format: 0.3`) |
|---|---|
| `size` `[w, h]` | `resolution.map_size` `{"x": w, "y": h}`, with `resolution.map_origin` `{"x": 0, "y": 0}` |
| the largest layer `px` | `resolution.pixels_per_grid` (a whole number) |
| layers, flattened to one picture (`show: "referee"` left out) | `image`: base64 PNG |
| `walls`: polylines `[[x, y], ...]` | `line_of_sight`: `[[{"x": x, "y": y}, ...], ...]` (and `objects_line_of_sight`, empty) |
| `doors`: `{"at": [a, b], "closed": true, "secret": false}` | `portals`: `{"position": midpoint, "bounds": [a, b], "rotation": radians, "closed": true, "freestanding": false}` |
| `lights`: `{"at": [x, y], "range": squares, "colour": "#rrggbb", "intensity": 1}` | `lights`: `{"position", "range", "intensity", "color": "ffrrggbb", "shadows": true}` |
| `environment`: `{"ambient": "#ffffff", "baked": false}` | `environment`: `{"baked_lighting": false, "ambient_light": "ffffffff"}` |

- **Coordinates** in these fields are in squares (fractions allowed), the same unit Universal VTT uses, so only the point shape changes (`[x, y]` against `{"x", "y"}`). Universal VTT colours are ARGB hex without `#`.
- **Map origin.** Dungeondraft exports may start at a `map_origin` other than 0, 0. Import subtracts it from every point.
- **Secret and locked doors** have no Universal VTT field, so they ride in the `"e9"` block and are exported as ordinary closed doors.
- The field names above were checked on 2026-11-06 against a sample Dungeondraft `.dd2vtt` (the uvtt2fgu project's `sampleMap.dd2vtt`) and the published Universal VTT notes. Check again against Foundry's Universal Battlemap Importer and Fantasy Grounds Unity's importer when the exporter is built.
- **Export** (Atlas 0.4.1, `tools/vtt_export.html`): the **Export for VTT** button on the map view saves one `<module>-<map>.uvtt` (Heph 2026-11-06: E9 always writes `.uvtt`; the content is the same as a `.dd2vtt`): the players' layers flattened at the largest layer `px` (smaller if the picture would pass 16 megapixels, the iOS canvas limit), plus walls, doors and lights. Fields Universal VTT lacks (areas, links, anchor, secret and locked doors, licence and credit) go in an `"e9"` block that other tools ignore and E9 reads back. A second option saves the picture alone as PNG, named with its pixels per square, for VTTs that only take images (Roll20, Owlbear Rodeo). `E9VTT.uvtt(map)` gives the same object from script.
- **Import** (Atlas 0.4.2): `python3 -I modules/tools/uvtt_import.py <file.uvtt> modules/<module>/encounter-maps [--id <map-id>] [--title ...] [--ft 5]` reads a `.uvtt`, `.dd2vtt` or `.df2vtt` into `<id>.json` and saves its picture, bytes unchanged, as `<id>/map.png` (or `.jpg`, `.webp`). `line_of_sight` and `objects_line_of_sight` both become `walls`; points are moved by `map_origin`. An E9 export's `e9` block brings back title, grid, areas, links, anchor, secret and locked doors, licence and credit, so export then import gives the same map file. A file from elsewhere gets an empty `licence`, to set before publishing; areas, links, scenes and the `site_encounters` pointer are the module author's to add.

## 8. Play state (later)

Tokens, light and fog are coming, but not for a while (Heph 2026-11-05). When they come:

- **Play state lives in the campaign**, never in the module: `campaign/encounter-maps/<map-id>.state.json`, holding tokens (a creature or character id, a square, a facing), revealed squares, and which doors are open. It is a separate file, so the module's map stays clean and a session's moves become one commit, like the Events log (MODULE_FORMAT.md section 7).
- **Tokens** link to creature cards and character sheets (CREATURES_FORMAT.md section 5), so Run encounter can place a scene's troupes on its pointed squares.
- **Fog and light** come from `walls`, `doors` and `lights`. Until a map has walls, fog is revealed by hand, square by square.
- **The referee view and the player view** are the same map, with `show: "referee"` layers, unrevealed squares and hidden doors held back from players.

Nothing in this section is built or promised for a version yet. It is here so that sections 3 to 7 don't paint the play surface into a corner.

## 9. Print

- Each map prints as an **overview page** (the whole map on one landscape 11 × 8.5 page, with area labels and a scale bar) and, on request, a **tiled battle mat** at 1 inch per square, split across as many pages as it needs, with page numbers and overlap marks.
- Layers marked `show: "referee"` print only on the referee's overview.
- Print pages carry the map's `licence` and `credit` and the Atlas version, like the League pages.

## 10. Decisions (Heph 2026-11-05)

1. Each PoI sets its own Encounter size. Several PoIs may point into squares of the same map, or into different maps.
2. Encounter maps get their own backgrounds of any size, or are stitched from assets of any size, so a Dungeon Scrawl PNG or JPG can simply be dropped in.
3. Tokens, light and fog are coming later. The format leaves room to grow into a VTT and to integrate with other VTTs.
4. (Heph 2026-11-06) A referee who uses a VTT account can link each map to its scene in that VTT. The links live in the campaign, not the module (section 13).

## 11. Build order (see section 12 for what exists)

Each slice is usable on its own:

1. This spec.
2. Map files load in the Atlas: a PoI pointer opens its map, the layers are drawn on a 5-ft grid, and there's a picker for several pointers. One Beyond the Pale site gets a real map as the test.
3. Generated ground and scatter tables for anchored maps and for PoIs without a pointer. Map outlines on the Field view.
4. Print: overview page and tiled battle mat.
5. Universal VTT import, then export.
6. Atlas editor "Add image" and area drawing.
7. Play state in the Companion: tokens, then hand-revealed fog, then walls, doors and light.
8. VTT links (section 13): pasted links and the Open button first, then an Export for VTT button, then account connections one VTT at a time.

Done so far: 1 (spec), 2 (maps open in the Atlas and the module viewer, Atlas 0.2.12). **Atlas 0.4.x is slices 5 and 8** (Heph 2026-11-06: "VTT and referee-tool integration"):

- **0.4.0, cleanup.** Walls, doors and lights from the drawing tool; `encounter_check.py` in the build; the viewer fills in the format's defaults in one place (`E9Map.load`), honours layer `rotate`, `opacity` and multi-rectangle areas, shows the play surface (Walls button) and has a hook for map buttons (`E9Map.actions`); the section 7 table checked against a real file; campaign links keyed by module (section 13).
- **0.4.1** Export for VTT: `.uvtt` for Foundry, Fantasy Grounds Unity and Arkenforge, plus picture + grid size for Roll20 and Owlbear Rodeo. Done.
- **0.4.2** Universal VTT import into a map file (`tools/uvtt_import.py`, a creator tool for now). Done.
- **0.4.3** Entrances, spawn points and the VTT adapter protocol, spec only (section 14).
- **0.4.4 on** The adapter pieces in the apps (section 14.5), then one adapter per VTT with its **Open in …** links: spool up the scene, spawn the mobs, move the party to its entrance.

## 12. Drawing maps: `tools/encounter_draw.py`

Beyond the Pale's maps are drawn by our own tool from hand-written plans; since 2026-11-06 the plans may follow Heph's traced layouts (Heph: "tracing isn't going to be a problem"). The hex tiles are hex art, so they are not used here.

- Each map has a hand-written plan, `encounter-maps/<id>/plan.json`, in squares: shapes for open floor (`rect`, `blob`, `path`, `poly`), water, roads, mounds, cliffs, curtain walls, towers, roofed buildings, seeded tree scatter, and marks (room numbers, cave letters, doors, secret doors, pit traps, stairs, webs, tents, nests, bones and so on). The tool's docstring lists every key.
- `python3 -I modules/tools/encounter_draw.py modules/<module>/encounter-maps [id ...]` draws `<id>/map.jpg` in the E9 ink style and writes `<id>.json` in this format, with the plan's areas, links and notes. The same plan and seed always draw the same picture.
- Any map can later swap its drawn layer for real art (a Dungeon Scrawl export, say) by editing `layers`; areas, links and scenes keep working.
- **Play surface.** The same run writes `walls` (the edge of cave and dug floors, and the outline of curtain walls, towers and buildings), `doors` (one per `door`, `locked` and `secret` mark, one square across) and `lights` (one per `fire` mark, 6 squares). Cliffs and water don't block sight. The plan key `openings` lists shapes that cut the walls without drawing anything, for gate passages and archways. `--json` rewrites only the map files and leaves the pictures alone, since JPEG bytes differ between Pillow builds even when the drawing is the same. A plan may set its own `credit` and `licence`.
- **Checks.** `python3 -I modules/tools/encounter_check.py modules/<module>` checks every map file (format, size, layer files, areas, links, walls, doors, lights) and every pointer from `site_encounters` and scenes. `build.py` runs it and stops on any problem.
- **Pointers.** `module.json` key `site_encounters` maps a site name, as drawn, to its pointer list (section 4). The Atlas converter copies it onto that point of interest as `encounter`, and the build copies `encounter-maps/` to the site (without the plans) and lists the maps in the published module manifest under `encounter_maps`.
- **Scenes.** Keyed rooms are scenes (CREATURES_FORMAT.md section 7) whose `where.room` and `map.area` share the area id.

## 13. Links into a referee's VTT (Heph 2026-11-06)

A referee who runs play in a VTT (Foundry, Roll20, Owlbear Rodeo, Fantasy Grounds, and so on) can link each Encounter map to the matching scene there. The Atlas and the Companion then open that scene directly. This section is a spec only: nothing is built yet.

**Where the links are stored.** The module's map file stays the same for every referee and carries only VTT-neutral data (layers, grid, walls, doors, lights). The links belong to the **campaign**, because every referee has a different account, and a scene or room link often works as a join key that shouldn't ship inside a published module. They go in one file, `campaign/vtt.json`, keyed by map id:

```json
{
  "format": "e9-vtt-links/1",
  "accounts": {
    "foundry": {"app": "foundry", "base": "https://my-table.example.com"},
    "owlbear": {"app": "owlbear"}
  },
  "maps": {
    "isle-of-mists:pale-keep":   [{"account": "foundry", "url": "https://my-table.example.com/game", "scene": "Pale Keep"}],
    "isle-of-mists:crom-grotto": [{"account": "owlbear", "url": "https://www.owlbear.rodeo/room/..."}]
  }
}
```

- `accounts` names each VTT the referee uses: `app` is one of a short list (`foundry`, `roll20`, `owlbear`, `fgu`, `other`), and `base` is the server address for self-hosted apps. Logins, passwords and API keys are never stored here. A later account connection keeps its token on the referee's device, not in the campaign repo.
- `maps` lists links per map, keyed `<module>:<map-id>` like the `#<module>:<map-id>` address (section 4), because a campaign can use several modules and two of them may both have a `cellar`. A map may have several links, one per VTT.
- Only `http:` and `https:` links are followed; anything else is ignored. `url` is what the Open button follows. `scene`, `page` or `id` are optional labels or ids that a connection can use to jump straight to the scene, and the button shows them.
- The file can be referee-only, so players don't see join links, or shared, so players can open the table from their Companion. The campaign decides (campaigns-as-git: the file sits in the campaign repo like any other).

**How they're opened.**

1. A map with a link in the current campaign shows **Open in Foundry** (or Roll20, or Owlbear) in the Atlas map view, the Companion's Run encounter screen, and a scene's card. It opens `url` in a new tab.
2. A map with no link shows **Export for VTT**. It writes the `.uvtt` file from section 7 and then offers a box to paste the new scene's link back, which saves it to `vtt.json`.
3. Later, with a connected account, **Send to Foundry** (and so on) creates the scene through that VTT's API and fills in the link itself. That is separate work for each VTT and comes last (section 11).

**Module creators** can still ship ready-made VTT content, such as a Foundry adventure pack, as a separate download. The module points to it with an ordinary link in `module.json`, which is not a campaign link.


## 14. Entrances, spawn points and VTT adapters (Heph 2026-11-06, Atlas 0.4.3, spec only)

A `.uvtt` file is only the scene. To run an encounter in a VTT the E9 apps also have to **spawn the mobs** and **move everyone to their entrances**, and that needs code running inside each VTT: a per-VTT **adapter** (Heph: "we'll need a per-VTT wrapper anyways"). This section adds the map data adapters need and the one protocol every adapter speaks, so the Atlas and the Companion never carry VTT-specific code.

### 14.1 Entrances and spawn points in the map file

A map file may have a `spawns` block, keyed by id like `areas`:

```json
"spawns": {
  "east-gate":  {"kind": "entrance", "squares": [60, 52, 3, 6], "title": "Over the drawbridge", "facing": "w"},
  "cellar-up":  {"kind": "entrance", "squares": [12, 40, 2, 2], "title": "Up from the cellars"},
  "guard-room": {"kind": "spawn", "area": "guard-tower"},
  "wolf-den":   {"kind": "spawn", "squares": [4, 4, 5, 4], "hidden": true}
}
```

- **kind** is `entrance` (where the party arrives) or `spawn` (where creatures appear). An entrance can also take creatures, for an ambush that follows the party in.
- **Where**: `squares` (a rectangle, or a list of them, as for areas) or `area` (an area id; the area's squares). A spawn with neither uses its scene's area.
- **facing** (optional, `n`, `ne`, `e` … `nw`) is the way tokens face on arrival. **hidden** spawns put tokens down hidden from players, for the referee to reveal.
- **Placement** is the same in every app and adapter (`E9Map.place`, Atlas 0.4.4): free squares nearest the rectangle's centre come first (ties: top to bottom, then left to right), a square is skipped if a wall crosses its middle (the central 0.4 × 0.4 of it; a wall may clip a corner) or a token already stands there, and a creature of `size` n (in squares, from the bestiary; default 1) takes an n × n block. When the rectangle is full, tokens spill into the ring of squares around it, then the next ring, but only into squares a token could walk to from the open square nearest the rectangle's centre, stepping square to square without a wall or closed door crossing the line between their centres, (so a cave spawn never spills into solid rock, and a rectangle drawn a little over the rock still fills only its floor). The same input always places the same way.
- **Pointers and links** may name an entrance: `{"map": "pale-keep", "entrance": "east-gate"}`. A PoI pointer with an entrance says where the party arrives when it opens the map from the world; a link (`links[].to`) with one says where a stair or path comes out on the other map.
- **Scenes** (CREATURES_FORMAT.md section 7) may say where their `who` stand: `"map": {"map": "pale-keep", "area": "guard-tower", "spawn": "guard-room"}`, or per line, `{"creature": "fomhoire-scout", "count": "d6", "spawn": "wolf-den"}`. Without one, they spawn in the scene's area.
- A map with no `spawns` still works: the party arrives in the pointed area (or the centre of the map) and creatures in their scene's area.
- `encounter_check.py` checks `spawns` (kind, squares on the map, area ids) and every `entrance` and `spawn` reference. A Universal VTT export carries `spawns` in its `e9` block.

### 14.2 The adapter protocol (`e9-vtt/1`)

An adapter is a small piece of code inside one VTT: a Foundry module, an Owlbear Rodeo extension, a Roll20 API script, a Fantasy Grounds extension. The E9 app (Atlas map view, Companion Run encounter) sends it **commands** and gets back **results** and **events**, all JSON:

| Command | What the adapter does | Result |
|---|---|---|
| `hello` `{"protocol": "e9-vtt/1", "app": "atlas", "campaign": id}` | says what it can do | `{"vtt": "foundry", "version", "can": ["scene", "walls", "lights", "tokens", "move", "hide", "activate"]}` |
| `scene.open` `{"map": "<module>:<map-id>", "uvtt": file or URL}` | finds the scene it made for this map before, or builds one from the `.uvtt` | `{"scene": vtt scene ref, "link": URL}`; the app saves the link in `vtt.json` (section 13) |
| `scene.activate` `{"scene"}` | shows the scene to the players (Foundry: activate; Owlbear: open) | `ok` |
| `tokens.spawn` `{"scene", "tokens": [{"id", "name", "creature", "img", "square": [x, y], "size": 1, "hidden": false, "disposition": "hostile"}]}` | creates tokens at those squares | `{"tokens": {e9 id: vtt token ref}}` |
| `party.place` `{"scene", "entrance", "squares": [[x, y], ...], "actors": [character ids]}` | moves each player character's token there (creating it from the actor if missing): the "teleport" | `{"tokens": {...}}` |
| `tokens.move` / `tokens.remove` / `tokens.reveal` | as named | `ok` |
| `bye` | lets go | `ok` |

- **The app works out the squares.** Placement (14.1) runs in the E9 app, so every adapter puts tokens in the same squares and an adapter stays small.
- **Token ids** are E9's: `<scene id>/<creature id>#<n>` for creatures, the character id for player characters. The adapter keeps its own map from E9 ids to VTT refs, and the campaign's `vtt.json` gains `"actors": {character id: {account: vtt actor ref}}` so a character is always the same VTT actor.
- **Events back** (later, for EVENTS_FORMAT.md triggers): `token.moved` `{"id", "square"}`, `door.opened`, `token.removed`. An adapter may send none.
- **Transport.** Same machine, no server: the adapter opens or embeds the E9 app (a Foundry popout window, an Owlbear extension popover) and the two talk with `window.postMessage`, each checking the other's origin, after the referee confirms a short pairing code shown on both sides. Where a VTT can't host a page (Roll20 API scripts, Fantasy Grounds), the fallback is a **file drop**: the app saves one `.e9vtt` bundle (the `.uvtt` plus the commands as a list) and the adapter's import button runs it.
- **Never stored or sent**: VTT logins, passwords or API keys (section 13).

### 14.3 Points of interest are entrances (Heph 2026-11-06, Atlas 0.4.5)

Heph: "Each PoI is an Entrance into an Encounter Map. One encounter map might correspond to multiple PoI." A vast underground megadungeon or underdark cavern can be **one map** with a mouth under each of several PoIs, each in its own hex.

1. **A PoI enters through an entrance.** Its pointer is `{"map": "<map>", "entrance": "<spawn id>"}` (in `module.json` `site_encounters`). Opening the map from that PoI centres on that entrance, and Run encounter places the party there (14.1).
2. **Entrances lead back out.** The map view lists **Ways out**: every place whose pointer enters this map, by entrance (or pointed area). "Out to <place>" closes the map and goes to that place: its 100-ft hex in the Atlas, its site in the module viewer. Leaving by another mouth comes out in another hex. Pages hand the places to the viewer as `E9Map.places` `[{name, pointers, go()}]`; the map file itself never names its PoIs, so the pointer in `site_encounters` is the one source of the link.
3. **One map, many entrances; one entrance, one place.** `encounter_check.py` warns when two places claim the same entrance, and when an entrance is used by no place and no link (maps in progress may have both, so these are warnings, not errors).
4. **Size.** An entrance can be as big as the 100-ft hex its PoI stands in: up to **25 × 20 squares** (paces). The checker warns past that.
5. **Where it sits in the world.** Each entrance stands under its own PoI: the entrance's centre is the centre of the PoI's hex (a PoI is always one whole 100-ft hex, ATLAS_FORMAT.md), north up. So a megadungeon needs no `anchor` for the whole map, and the Field view can outline each entrance's footprint in its own hex (to build with the Field outlines, section 11 slice 3). An entrance may set `"rotate"` (degrees clockwise) when the mouth faces another way on the map.

### 14.4 The Foundry adapter (Atlas 0.4.6)

`vtt/foundry/e9-bridge/` is a Foundry VTT module (v12, v13; README there). The GM presses *Open the E9 Atlas* in Foundry's token controls; the Atlas opens with `?vtt=foundry&pair=<code>`, shows "Linked to Foundry · code …", and every encounter map gains **Send to Foundry** (`tools/vtt_bridge.html`): pick the scenes whose creatures to place and the entrance the party arrives at, then the Atlas sends `scene.open` (the `.uvtt`), `tokens.spawn`, `party.place` (`actors: "players"`, each player's assigned character) and `scene.activate`.

- **Counts.** The Atlas rolls each `who` line's dice (`3`, `d6`, `2d6`, `d6+1`, `d6÷2`) and its `chance` (`1-3 on d6`); a troupe word counts as 1 until the bestiary is wired in.
- **Where.** A `who` line's `spawn`, else the scene's `map.spawn`, else its `map.area`, placed with 14.1; all tokens of one send avoid each other and the party.
- **Reuse.** The scene is marked with `<module>:<map-id>`; sending the same map again reuses it and only places tokens.
- **Creatures are actorless tokens** for now; making Foundry actors from the bestiary is per game system and comes later.
- **Untested in a live Foundry world** at 0.4.6: the module was run against a stand-in for Foundry's API.

### 14.5 Order of work

1. This spec. Atlas 0.4.3.
2. `spawns` in the checker, the viewer (entrances and spawn points drawn with the Walls overlay) and the `.uvtt` `e9` block, and the shared placement function `E9Map.place`. Done in Atlas 0.4.4.
3. The first adapter: **Foundry VTT** (Heph 2026-11-06), an E9 Foundry module (14.4, Atlas 0.4.6). Open in links from section 13 still to come.
4. More adapters, one VTT at a time.

Module threads supply real `spawns` for their maps (Heph 2026-11-06: the Atlas provides capabilities, the module threads provide implementations and test data).
