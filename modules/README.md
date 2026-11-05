# Modules

Playable Materia Mundi modules, built from one source into a web viewer, print PDFs and a Companion manifest. The protocol is in [MODULE_FORMAT.md](MODULE_FORMAT.md). The planned E9 Atlas map format (one terrain PNG per March plus a JSON) is drafted in [ATLAS_FORMAT.md](ATLAS_FORMAT.md), the Events and Procedures layer (triggers, tables and per-ruleset procedures) is drafted in [EVENTS_FORMAT.md](EVENTS_FORMAT.md), creatures, NPCs, factions and encounters (a fiction layer and a per-ruleset bestiary) are drafted in [CREATURES_FORMAT.md](CREATURES_FORMAT.md), and [REALMAP.md](REALMAP.md) shows how to start a new campaign map from real-world data. The tools are CC0 ([tools/LICENSE.md](tools/LICENSE.md)). How creators, referees and players use modules, and how modules are versioned, depend on each other and get trusted, is in [WORKFLOWS.md](WORKFLOWS.md).

| Module | Source | Published |
| --- | --- | --- |
| Beyond the Pale: Leinster, 1422 | [isle-of-mists/module.json](isle-of-mists/module.json) | `https://ialdabaoth.github.io/MateriaMundiRPG/modules/isle-of-mists/` |

To build locally, see section 8 of the format. The build fetches SRTM terrain tiles into `modules/.cache/` the first time it runs.

Everything in `modules/` is CC0 1.0 (public domain dedication): fork it, change it, and republish it. The one exception is the map icons in `assets/tiles/`: [Hex Tiles: Fantasy](https://cmartins.itch.io/hex-tiles-fantasy) by cmartins, CC BY-SA 4.0. Credit them wherever the maps go.
