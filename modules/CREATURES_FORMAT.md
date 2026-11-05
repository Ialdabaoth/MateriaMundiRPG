# E9 Characters and Encounters format (draft)

How a module describes *who* the party meets (creatures, named NPCs and the factions behind them) and *what* an encounter with them looks like, and how the E9 Companion runs them on the Referee tab.
Designed with Heph on 2026-11-05. Status: **draft, nothing built yet**. Companion to EVENTS_FORMAT.md, which decides *when* something happens and *how* it resolves, and to ENCOUNTER_FORMAT.md (the Encounter map level of the Atlas), which decides *where everyone stands*. This file replaces the draft referee creature spec (project files, `companion-app/referee-creatures-spec.md`), whose seven open questions are answered in section 8.

## 1. The idea in one paragraph

Creatures are split the same way events are. A module's **`encounters.json`** is the **fiction layer**: who the creatures and NPCs are (local names, descriptions, faction, wants, what they know), how they turn up (troupe sizes, lairs, related events), and the encounters that bring them on stage. It never holds a number that only one ruleset understands. Each **`bestiary/<ruleset>.json`** is the **mechanics layer**: it says what each creature id means in that ruleset, as a stat block that **starts from a template and then replaces or adjusts** what differs. The template can be a bestiary entry, an NPC template, another creature, or a full player character sheet for the occasional NPC who needs PC-level detail. So the same module runs its Fomhóire under Materia Mundi, E9 or OSE, and Beyond the Pale prints Materia Mundi and OSE blocks side by side from one source.

## 2. Files

```
modules/<module-id>/
  encounters.json                  fiction: creatures, factions, encounters (rule-generic; any *.json with an "encounters" block also counts)
  bestiary/<ruleset-id>.json       mechanics: this module's stat blocks for one ruleset
  bestiary/<ruleset-id>/<id>.json  full character sheets for PC-level NPCs (CHARACTER_FORMAT.md)
companion-app/src/rules/
  bestiary/<ruleset-id>.json       the ruleset's own bestiary (today's mm-bestiary.json moves here)
campaign/                          in a referee's fork (MODULE_FORMAT.md section 7)
  encounters.json                  the referee's own creatures and changes, same format
  bestiary/<ruleset-id>.json       their stats; per-creature play state in creatures/<id>.json
```

A campaign's entry overrides a module's entry with the same id, in both layers, so a referee can change an NPC without touching the module and still pull upstream fixes.

`encounters.json` is a convention, not a requirement. **Any `*.json` file in the module folder (at any depth) that has a top-level `"encounters"` block is merged into the module's encounters**, whatever its name, exactly as `"events"` blocks are (EVENTS_FORMAT.md section 2, "Multiple files", which owns the rules). One file may hold both blocks. An `"encounters"` block holds any of `creatures` and `scenes` (each keyed by id) and `factions` (a list keyed by `id`):

```json
{"encounters": {"creatures": {"fomhoire-scout": {...}}, "factions": [{"id": "kells-priory", ...}], "scenes": {"fomhoire-scouts": {...}}}}
```

The collision rules are the same as for events: files load in path order; a duplicate id inside one layer (the module, or the campaign) is flagged on load and the first file in path order keeps it; the campaign layer replaces a module id on purpose, and the load report lists every replacement; to remove a module creature, faction or scene, the campaign gives the same id with `"off": true`.

Every bestiary file declares the rulesets it serves, as procedures do: `{"format": "e9-bestiary/1", "rules": ["mm", "e9mm"], "creatures": {...}}`.

## 3. The fiction layer: creatures (`encounters.creatures`)

The names and story in the examples below are placeholders to show the fields, not canon.

```json
"creatures": {
  "fomhoire-scout": {
    "name": "Fomhóire scout", "names": {"ga": "Scabhta Fomhórach"},
    "is": "goblin",
    "kind": "monster",
    "look": "Bent, grey-skinned, one eye too many; smells of bog-myrtle and old blood.",
    "faction": "crom-cruach",
    "troupe": {"wandering": "d6", "lair": "2d6+6"},
    "lair": {"terrain": "bog", "march": "an-mhi"},
    "disposition": "wary", "threat": "minor",
    "events": ["crom-tithe", "bog-entry"],
    "page": 44
  },
  "brother-ailill": {
    "name": "Brother Ailill", "names": {"ga": "An Bráthair Ailill"},
    "is": "acolyte", "kind": "npc",
    "look": "Tonsured, ink-stained, never without his satchel of quires.",
    "faction": "kells-priory", "rank": "sub-prior",
    "wants": "To get the Book of the Mist out of Kells before the Ard-Rí's men find it.",
    "fears": "The Crom pact; his brother signed it.",
    "knows": [{"site": "kells-priory"}, {"creature": "the-grey-abbot"}, {"text": "The causeway floods at the dark of the moon."}],
    "relations": {"the-grey-abbot": "afraid of", "maol-ruain": "brother"},
    "disposition": "wary",
    "portrait": "art/ailill.png"
  }
}
```

- **is** names a common creature in plain words (`goblin`, `wolf`, `acolyte`, `ogre`) for a ruleset to fall back on when the module's own bestiary has no entry (section 4). The fiction says *a Fomhóire scout is a kind of goblin*; each ruleset decides what a goblin is.
- **kind**: `monster`, `npc`, `follower`, `beast`.
- **troupe** gives group sizes by situation (`wandering`, `lair`, or any word the module uses), in d6 and d20 only: `3`, `d6`, `2d6`, `d6÷2`, `d20÷2`, `2d6+6`.
- **lair** is where they live, in the same `where` shape as encounters (section 7).
- **events** lists the triggers and tables in `events.json` that bring this creature on stage, so the Companion can show "where does this turn up" and the module check can warn about creatures nothing ever calls.
- **disposition** and **threat** are macro words (EVENTS_FORMAT.md section 5); the ruleset's `reaction` and `morale` procedures expand them.
- **knows** points at sites, creatures, or plain rumour text, so the Companion can show "who knows about this place" on a site and "what can she tell us" on an NPC.
- Other story fields: `names` (the Language box), `look`, `faction`, `rank`, `wants`, `fears`, `relations`, `portrait`, `page`.

## 4. The mechanics layer: `bestiary/<ruleset>.json`

```json
{"format": "e9-bestiary/1", "rules": ["mm", "e9mm"], "creatures": {
  "fomhoire-scout": {"from": "mm:goblin", "replace": {"movement": "Normal / Swim Normal"}, "adjust": {"saves": {"curse": -2}, "attacks": {"add": [{"name": "Hooked spear", "damage": "d6"}]}}},
  "brother-ailill": {"from": "pc", "sheet": "brother-ailill.json"}
},
"macros": {"threat": {"minor": {"level": [1, 2]}, "deadly": {"level": [7, 9]}}},
"aliases": {"fomhoire-hound": "mm:wolf-mastiff"}}
```

**Lookup.** A creature id resolves for the campaign's ruleset in this order: the campaign's `bestiary/<ruleset>.json`, the module's, the ruleset's own bestiary by the fiction's `is` word, then `aliases` in any of these and lookup again. **The contract:** every creature in `encounters.json` must resolve for the campaign's ruleset. When a module loads, the app lists anything missing, as it does for procedures, and still shows the fiction for it.

### 4.1 Templates: start with X, then replace or adjust

Each entry is `{"from": <template>, "replace": {...}, "adjust": {...}}`, applied in that order.

| `from` | Starts with | Use for |
|---|---|---|
| `<bestiary>:<id>`, e.g. `mm:wolf-mastiff`, `ose:acolyte` | that bestiary entry, copied | monsters, animals, stock NPCs |
| `npc:<class>`, e.g. `npc:warrior`, or `npc` alone | a level 1 person of that class, primes at +1, hit points per level and saves from ability + level; `npc` alone rolls the ruleset's quick NPC table. Replace `level` to make them more. | ordinary named people |
| `<creature-id>` | another creature in this layer, resolved first | variants: "as Ailill, but undead" |
| `pc` + `"sheet": <file or id>` | a **full character sheet** (CHARACTER_FORMAT.md) in `bestiary/<ruleset>/`, or in the Companion a sheet with `"owner": "referee"` | the occasional NPC who needs full PC detail: class, spells, gear, Panoply, talents |
| `blank` | nothing | something wholly new; every field is in `replace` |

- **replace** overwrites a field outright: `level`, `armor`, `movement`, `hd`, `hp`, `saves.fear`, `attacks` (the whole list), `talentThreshold`, `behavior`, `special`.
- **adjust** changes a field relative to the template. Numbers add (`"hp": 3`, `"abilities": {"str": 1}`, `"saves": {"curse": -2}`). Lists take `add` and `remove` (`"attacks": {"add": [...]}`, `"talents": {"remove": ["sneak"]}`).
- Chains are allowed (a variant of a variant) and share the depth limit of 6 used by procedures.
- A `pc` sheet is an ordinary character file with `"owner": "referee"`, so everything the character sheet does (spell slots, hold roll, gear, encumbrance) works for that NPC unchanged. It can still take `replace` and `adjust`, for example a level 9 lord built from a level 5 sheet.
- **macros** expand the fiction's macro words for this ruleset where the procedures don't already, for example what level band a `deadly` threat means when the Companion builds a quick NPC.
- The dice rule (d20 and d6 only) binds the fiction layer. A bestiary rolls whatever its own system rolls.

The resolved creature is computed when it is used, and the file keeps only the template and the differences, so a bestiary fix reaches every creature built on it. A creature taken into play (section 7) is a **copy**, with its HP rolled once, and later edits to that copy never change the module.

### 4.2 Writing stat blocks for print

The print book shows the resolved block for each ruleset the module ships, side by side where there are two (as Beyond the Pale does with Materia Mundi and OSE), under the fiction's name and description. The build resolves templates, so the Affinity Publisher text and the Companion always agree.

## 5. In the Companion

The Referee tab's creature list holds the campaign's creatures: referee creatures first, then players' followers grouped by owner, filterable by kind and faction. A creature card shows name and level, HP with +/- and a hold roll (an HP pip per member for a troupe), armor, attack rows with roll buttons, a save row for each track, one roll button per trained talent with the threshold shown, attitude and notes, and for NPCs the story fields. A `pc`-template NPC opens as a full sheet instead of a card.

**Add** offers: from the bestiary, from a module creature, from the quick NPC table, from a character sheet, or blank. Rolls are logged with the creature's name in the Who field.

## 6. Factions (`encounters.factions`)

```json
"factions": [
  {"id": "kells-priory", "name": "Kells Priory", "kind": "church", "seat": "kells-priory", "leader": "the-grey-abbot",
   "relations": {"crom-cruach": "enemy", "lords-of-meath": "uneasy ally"}}
]
```

- `kind` is free text the module chooses (`court`, `lordship`, `church`, `clan`, `cult`...). The fey courts and mortal lords of the Leinster political drafts become factions here.
- Relations are words, not numbers, so they stay rule-generic. A ruleset or a later procedure may read them, for example to bend a reaction roll.
- The Companion shows a faction's members, its seat on the Atlas, and its relations. Events may move a faction's standing through a region ratchet (EVENTS_FORMAT.md section 7); this file only names who stands where.

## 7. Encounters (`encounters.scenes`)

An encounter record is called a **scene** in the file (`encounters.scenes`), so the block does not read `"encounters": {"encounters": ...}`. Scenes are keyed by id.

```json
"scenes": {
  "fomhoire-scouts": {"title": "Fomhóire scouts",
   "where": {"terrain": "bog", "march": "an-mhi"},
   "who": [{"creature": "fomhoire-scout", "count": "d6"}, {"creature": "fomhoire-hound", "count": "d6÷2", "chance": "1-3 on d6"}],
   "disposition": "aggressive", "threat": "dangerous",
   "wants": "To see who is crossing Crom's ground, and report it.",
   "tactics": "Shadow the party at bowshot; flee if one falls.",
   "treasure": "Each carries a bronze token marked with the bent knee.",
   "players": "Shapes in the reeds keep pace with you.",
   "map": null}
}
```

- **where** is a site slug (`"site": "kells-priory"`, with an optional `"room"` key for keyed locations), a hex address (`"hex": "<map>:<hex>"`), or a terrain within a March (`"terrain"` plus `"march"`). A keyed encounter at a site shows as a marker on that point of interest in the Atlas; terrain encounters show nowhere until rolled.
- **who** lists creatures with a `count` (a number, d6/d20 dice, or a `troupe` word such as `"wandering"` to use the creature's own size) and an optional `chance` (`"1-3 on d6"`, `"1-5 on d20"`) for members who are only sometimes there. One line with a count is one troupe; it gets one card with a pip per member, and a member can be split off into its own card if the fight needs it.
- **disposition** and **threat** override the creatures' own. For Materia Mundi, a creature's bestiary behaviour line ("1-2 fearful, 3-5 wary, 6 aggressive") is its reaction table when neither layer sets a disposition.
- **map** (optional) points into an Encounter map: a map id, or a pointer `{"map": id, "area": name}` / `{"map": id, "squares": [x, y, w, h]}` (ENCOUNTER_FORMAT.md section 4). Where everyone stands is that map's business, not this file's.
- Event tables (EVENTS_FORMAT.md section 5) call an encounter with `{"call": "encounter", "with": {"encounter": "fomhoire-scouts"}}`, or an ad hoc one with `creature` and `count`. The `encounter` procedure rolls counts and chances, runs the reaction, and ends with a `scene` effect.
- **Run encounter** (from a site marker, a table result, or the Referee tab) puts copies of everyone into the current scene: one card per troupe or individual, HP rolled, with the encounter's `wants`, `tactics` and `treasure` pinned above them. Ending the scene logs survivors and loot to the Events log; named NPCs keep their HP and notes in `campaign/creatures/<id>.json`.

## 8. Decisions (from the draft referee creature spec, Heph 2026-11-05)

1. **A referee creature can move across to a player's party** as a follower: its `owner` changes to that character, and it keeps its id, history and notes.
2. **The creature list is per campaign**, not global on the device.
3. **A troupe is one record with a count**, with an HP pip per member; members can be split off.
4. **Players' followers** can be viewed and rolled from the Referee tab, but they are edited only on the player's own sheet.
5. **One roll button per trained talent.**
6. **The NPC threshold table is a rules option** (in `<ruleset>-options.json`), so E9 and Materia Mundi can differ. The referee can still overwrite `talentThreshold` per creature.
7. **Creature data lives in the campaign** (`campaign/encounters.json` and `campaign/bestiary/`, with play state in `campaign/creatures/<id>.json`), as characters and rules do. Player followers stay inside their character file, as `Follower` does today; existing sheets keep working.

Also agreed: creatures have a fiction layer and a mechanics layer, like events and procedures (sections 3 and 4); named NPCs tie into the political layer now (section 6), and **Beyond the Pale is written in this format first**, by converting its existing keyed encounters and stat blocks.

## 9. Build order

Each slice is usable at the table on its own:

1. This spec.
2. Template resolver (bestiary, NPC template, module creature, replace and adjust) with tests, and creature cards on the Referee tab, including Add from the bestiary.
3. Move the Materia Mundi bestiary to `rules/bestiary/mm.json` in the new format (with `is` words), `pc`-template NPCs opening as full sheets; moving a creature across to a player's party.
4. Beyond the Pale's creatures, factions and keyed encounters converted into `encounters.json`, `bestiary/mm.json` and `bestiary/ose.json`, with the print stat blocks generated from them.
5. Run encounter and the `scene` effect, with encounter markers on Atlas points of interest (after EVENTS_FORMAT.md slice 2).
6. Faction view in the Companion and on the Atlas.
