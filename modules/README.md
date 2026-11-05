# Modules

Playable Materia Mundi modules, built from one source into a web viewer, print PDFs and a Companion manifest. The protocol is in [MODULE_FORMAT.md](MODULE_FORMAT.md).

| Module | Source | Published |
| --- | --- | --- |
| Beyond the Pale: Leinster, 1422 | [isle-of-mists/module.json](isle-of-mists/module.json) | `https://ialdabaoth.github.io/MateriaMundiRPG/modules/isle-of-mists/` |

To build locally, see section 8 of the format. The build fetches SRTM terrain tiles into `modules/.cache/` the first time it runs.

Everything in `modules/` is CC0 1.0 (public domain dedication): fork it, change it, and republish it. The one exception is the map icons in `assets/tiles/`: [Hex Tiles: Fantasy](https://cmartins.itch.io/hex-tiles-fantasy) by cmartins, CC BY-SA 4.0. Credit them wherever the maps go.
