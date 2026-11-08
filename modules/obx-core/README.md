# OBX (`obx-core`)

A root rules module (PROPOSALS.md P2) for classic B/X play: `provides: "obx"`. A campaign that picks OBX as its root uses these rules and nothing from E9.

- **Licence: OGL 1.0a**, not CC BY 4.0. The tables are Open Game Content from an OGL source, so the module stays under the OGL; the licence, the Open Game Content designation and the copyright notice are in [LICENSE.OGL.md](LICENSE.OGL.md).
- **No rules text is copied.** Numbers and tables only; every rule is worded by Heph ([text/](text/README.md)).
- **No trademark use.** OBX is not called, and must not be presented as, compatible with any trademarked game. Other publishers' names appear only in the OGL copyright notice.

| File | Holds |
| --- | --- |
| `rules.json` | the seven classes: requirements, prime requisites, hit die, maximum level |
| `derive.json` | tables (ability modifiers, prime requisite XP, each class's level progression with XP, HD, THAC0, attack bonus, saves and spell slots, thief skills, turning) and the named values a sheet layout shows (SHEET_LAYOUT.md) |
| `equipment.json` | weapons (cost, weight, damage, qualities, ranges) and armour (AC, ascending AC) |
| `text/` | Heph's rules text, one file per rule |
| `tools/extract_srd.py` | rebuilds the three JSON files from a checkout of the Markdown SRD, so every number can be traced and checked |

Rebuild: `git clone https://github.com/oldmanumby/ose.srd /tmp/srd && python3 -I tools/extract_srd.py /tmp/srd .`

The Companion reads this module once its sheet layout engine lands (SHEET_LAYOUT.md, Companion 0.5.X). Until then no app loads it.
