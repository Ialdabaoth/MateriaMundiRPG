# Beyond the Pale: Leinster, 1422 — changelog

This module's version is its own. It does not follow the E9 Atlas (`modules/tools/ATLAS_VERSION`) or the E9 Companion; a change to the tools or apps alone never bumps it. Bump it only for changes to this module's content (text, sites, creatures, encounters, maps), using the rules in [WORKFLOWS.md](../WORKFLOWS.md#versioning).

## 0.4.0 (2026-11-06)

All of Ireland in the E9 Atlas (Heph: "available for exploration", not yet tied to books). The print maps stay on the four book counties.
- `atlas.land: "island"`: the Atlas covers the whole island, 104 Marches. 89 new real-data terrain masters (ESA WorldCover + SRTM, 1420s rules, tools/realmap.py), with rivers from the island's own drainage.
- New region `eire-1422`: 328 places that stood in 1422 (45 towns, 153 castles, 68 abbeys and friaries, 31 hills, 18 ruins, 10 tombs, 3 caves). Religious houses inside a town are in the town's note.
- Sources: towns, abbeys and old places from general history (Claude), town positions checked against GeoNames (all within about 2 km); most castles (Anglo-Norman stone castles and hall-houses) from Canonical Castles (bussetech/canonical-castles, CC BY 4.0), whose positions come from the Archaeological Survey of Ireland's Sites and Monuments Record (CC BY 4.0). Tower houses are left out: most are later than 1422.
- To check before print: Irish names for the minor castles (still English) and a few less common Irish forms (for example Seanchaisleán for Olderfleet), and which castles were ruined or held by Gaelic lords by 1422.
- `modules/geo/admin1.geojson` gains Northern Ireland's districts (Natural Earth, public domain) so the island's outline is complete.

## 0.3.0 (2026-11-06)

Baseline set by Heph after the E9 Atlas split into its own sub-project. Earlier builds printed 0.1.0 to 0.3.6 while the module and the map tools shared one number; none was released, so the count restarts here. Contents: the Leinster quartet (An Mhí B2, Cill Chainnigh B3, Ceatharlach B5, Cill Dara B4), real-data E9 Atlas terrain masters, sites, creatures and the first encounter maps.
