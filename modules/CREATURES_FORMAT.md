# E9 Characters and Encounters format (draft)

How a module describes *who* the party meets (creatures, named NPCs and the factions behind them) and *what* an encounter with them looks like, and how the E9 Companion runs them on the Referee tab.
Designed with Heph on 2026-11-05. Status: **draft, nothing built yet**. Companion to EVENTS_FORMAT.md, which decides *when* something happens and *how* it resolves, and to the Encounter map level in ATLAS_FORMAT.md, which decides *where everyone stands*. This file replaces the draft referee creature spec (project files, `companion-app/referee-creatures-spec.md`), whose seven open questions are answered in section 7.

## 1. The idea in one paragraph

There is **one creature record** for everything with stats: bestiary monsters, a module's named NPCs, a referee's homebrew, and players' followers and beasts. A record rarely starts from nothing. It names a **template** (a bestiary entry, an NPC template, or a full player character sheet) and then **replaces or adjusts** what differs. Story fields (name, look, faction, wants, what they know) are shared by every ruleset, while stats are given **per ruleset**, so one module can carry Materia Mundi and OSE stat blocks side by side. An **encounter** is a small, fiction-only record: who comes, how many, in what mood, wanting what, and where. Event tables call encounters, and running one puts creature cards on the Referee tab.

## 2. Files

```
modules/<module-id>/
  creatures/<id>.json      one creature or NPC per file
  creatures/factions.json  factions and their relations (section 5)
  encounters.json          encounter records (section 6)
campaign/                  in a referee's fork (MODULE_FORMAT.md section 7)
  creatures/<id>.json      the referee's own creatures and changed copies, same format
```

A campaign's file overrides a module's file with the same id, so a referee can change Brother Ailill without touching the module, and still pull upstream fixes.

## 3. The creature record

The names and story in the examples below are placeholders to show the fields, not canon.

```json
{
  "format": "e9-creature/1",
  "id": "brother-ailill",
  "name": "Brother Ailill",
  "names": {"ga": "An Bráthair Ailill"},
  "kind": "npc",
  "look": "Tonsured, ink-stained, never without his satchel of quires.",
  "faction": "kells-priory", "rank": "sub-prior",
  "wants": "To get the Book of the Mist out of Kells before the Ard-Rí's men find it.",
  "fears": "The Crom pact; his brother signed it.",
  "knows": [{"site": "kells-priory"}, {"creature": "the-grey-abbot"}, {"text": "The causeway floods at the dark of the moon."}],
  "relations": {"the-grey-abbot": "afraid of", "maol-ruain": "brother"},
  "disposition": "wary",
  "portrait": "art/ailill.png",
  "page": 41,
  "stats": {
    "mm":  {"from": "pc", "sheet": "ailill.mm.json"},
    "ose": {"from": "ose:acolyte", "replace": {"level": 4, "hd": "4"}, "adjust": {"hp": 3}}
  }
}
```

- **kind**: `monster`, `npc`, `follower`, `beast`. A troupe is not a kind: it is any creature run with a count (section 6).
- **Story fields** (`name`, `names`, `look`, `faction`, `rank`, `wants`, `fears`, `knows`, `relations`, `disposition`, `portrait`, `page`) are rule-generic. `disposition` is a word from the module's macro vocabulary (EVENTS_FORMAT.md section 5), for example `fearful`, `wary`, `friendly`, `aggressive`; each ruleset's reaction procedure expands it.
- **knows** points at sites, creatures, or plain rumour text, so the Companion can show "who knows about this place" on a site and "what can she tell us" on an NPC.
- **stats** is keyed by ruleset id (`mm`, `e9`, `e9mm`, `ose`, ...). A ruleset with no entry falls back to the nearest listed one only when the ruleset's options say it can read that format (`e9mm` can read `mm`); otherwise the Companion shows the story fields and says that stats are missing.

### 3.1 Templates: start with X, then replace or adjust

Each `stats` entry is `{"from": <template>, "replace": {...}, "adjust": {...}}`, applied in that order.

| `from` | Starts with | Use for |
|---|---|---|
| `<bestiary>:<id>`, e.g. `mm:wolf-mastiff`, `ose:acolyte` | that bestiary entry, copied | monsters, animals, stock NPCs |
| `npc:<template>`, e.g. `npc:veteran`, `npc:expert` | an NPC template from the ruleset's options (the quick NPC table, by level band) | ordinary named people |
| `<module>:<creature-id>` | another creature record, resolved first | variants: "as Ailill, but undead" |
| `pc` + `"sheet": <file>` | a **full character sheet** (CHARACTER_FORMAT.md), stored next to the record | the occasional NPC who needs full PC detail: class, spells, gear, Panoply, talents |
| `blank` | nothing | something wholly new; every field is in `replace` |

- **replace** overwrites a field outright: `level`, `armor`, `movement`, `hd`, `hp`, `saves.fear`, `attacks` (the whole list), `talentThreshold`, `behavior`, `special`.
- **adjust** changes a field relative to the template. Numbers add (`"hp": 3`, `"abilities": {"str": 1}`, `"saves": {"curse": -2}`). Lists take `add` and `remove` (`"attacks": {"add": [{"name": "Silver knife", "damage": "d6"}]}`, `"talents": {"remove": ["sneak"]}`).
- Chains are allowed (a variant of a variant) and share the depth limit of 6 used by procedures.
- `pc` is an ordinary character file with `"owner": "referee"`, so everything the character sheet does (spell slots, hold roll, gear, encumbrance) works for that NPC unchanged. It can still take `replace` and `adjust`, which is handy for a "Lord of Kilkenny at level 9" built from a level 5 sheet.

The resolved creature is computed when it is used; the file keeps only the template and the differences, so a bestiary fix reaches every creature built on it. A creature taken into play (section 6) is a **copy**, with its HP rolled once, and later edits to that copy never change the module.

### 3.2 Writing stat blocks for print

The print book shows the resolved block per ruleset, side by side where the module carries two (as Beyond the Pale does with Materia Mundi and OSE). The build resolves templates, so the Affinity Publisher text and the Companion always agree.

## 4. In the Companion

The Referee tab's creature list holds the campaign's creatures: referee creatures first, then players' followers grouped by owner, filterable by kind and faction. A creature card shows name and level, HP with +/- and a hold roll (an HP pip per member for a troupe), armor, attack rows with roll buttons, a save row for each track, one roll button per trained talent with the threshold shown, attitude and notes, and for NPCs the story fields. A `pc`-template NPC opens as a full sheet instead of a card.

**Add** offers: from the bestiary, from a module creature, from the quick NPC table, from a character sheet, or blank. Rolls are logged with the creature's name in the Who field.

## 5. Factions

```json
{"format": "e9-factions/1", "factions": [
  {"id": "kells-priory", "name": "Kells Priory", "kind": "church", "seat": "kells-priory", "leader": "the-grey-abbot",
   "relations": {"crom-cruach": "enemy", "lords-of-meath": "uneasy ally"}}
]}
```

- `kind` is free text the module chooses (`court`, `lordship`, `church`, `clan`, `cult`...). The fey courts and mortal lords of the Leinster political drafts become factions here.
- Relations are words, not numbers, so they stay rule-generic. A ruleset or a later procedure may read them, for example to bend a reaction roll.
- The Companion shows a faction's members, its seat on the Atlas, and its relations. Events may move a faction's standing through a region ratchet (EVENTS_FORMAT.md section 7); this file only names who stands where.

## 6. Encounters

`encounters.json` holds the module's encounters. Like `events.json`, it speaks in fiction only.

```json
{"format": "e9-encounters/1", "encounters": [
  {"id": "fomhoire-scouts", "title": "Fomhóire scouts",
   "where": {"terrain": "bog", "march": "an-mhi"},
   "who": [{"creature": "fomhoire-scout", "count": "d6"}, {"creature": "fomhoire-hound", "count": "d6÷2", "chance": "1-3 on d6"}],
   "disposition": "aggressive", "threat": "dangerous",
   "wants": "To see who is crossing Crom's ground, and report it.",
   "tactics": "Shadow the party at bowshot; flee if one falls.",
   "treasure": "Each carries a bronze token marked with the bent knee.",
   "players": "Shapes in the reeds keep pace with you.",
   "map": null}
]}
```

- **where** is a site slug (`"site": "kells-priory"`, with an optional `"room"` key for keyed locations), a hex address (`"hex": "<map>:<hex>"`), or a terrain within a March (`"terrain"` plus `"march"`). A keyed encounter at a site shows as a marker on that point of interest in the Atlas; terrain encounters show nowhere until rolled.
- **who** lists creatures with a `count` in d6 and d20 only (`3`, `d6`, `2d6`, `d6÷2`, `d20÷2`, `d6+2`) and an optional `chance` (`"1-3 on d6"`, `"1-5 on d20"`) for members who are only sometimes there. One line with a count is one troupe; it gets one card with a pip per member, and a member can be split off into its own card if the fight needs it.
- **disposition** and **threat** are macro words; the ruleset's `reaction` and `morale` procedures expand them. For Materia Mundi, a creature's bestiary behaviour line ("1-2 fearful, 3-5 wary, 6 aggressive") is its reaction table, and a `disposition` on the encounter overrides it.
- **map** (optional) names a hand-made Encounter map. Where everyone stands is that map's business (ATLAS_FORMAT.md, Encounter level), not this file's.
- Event tables (EVENTS_FORMAT.md section 5) call an encounter with `{"call": "encounter", "with": {"encounter": "fomhoire-scouts"}}`, or an ad hoc one with `creature` and `count`. The `encounter` procedure rolls counts and chances, runs the reaction, and ends with a `scene` effect.
- **Run encounter** (from a site marker, a table result, or the Referee tab) puts copies of everyone into the current scene: one card per troupe or individual, HP rolled, with the encounter's `wants`, `tactics` and `treasure` pinned above them. Ending the scene logs survivors and loot to the Events log; named NPCs keep their HP and notes in `campaign/creatures/`.

## 7. Decisions (from the draft referee creature spec, Heph 2026-11-05)

1. **A referee creature can move across to a player's party** as a follower: its `owner` changes to that character, and it keeps its id, history and notes.
2. **The creature list is per campaign**, not global on the device.
3. **A troupe is one record with a count**, with an HP pip per member; members can be split off.
4. **Players' followers** can be viewed and rolled from the Referee tab, but they are edited only on the player's own sheet.
5. **One roll button per trained talent.**
6. **The NPC threshold table is a rules option** (in `<ruleset>-options.json`), so E9 and Materia Mundi can differ. The referee can still overwrite `talentThreshold` per creature.
7. **Creature data lives in the campaign** (`campaign/creatures/`, one file each), as characters and rules do. Player followers stay inside their character file, as `Follower` does today; existing sheets keep working.

Also agreed: named NPCs tie into the political layer now (section 5), and **Beyond the Pale is written in this format first**, by converting its existing keyed encounters and stat blocks.

## 8. Build order

Each slice is usable at the table on its own:

1. This spec.
2. Template resolver (bestiary, NPC template, module creature, replace and adjust) with tests, and creature cards on the Referee tab, including Add from the bestiary.
3. `pc`-template NPCs opening as full sheets; moving a creature across to a player's party.
4. Beyond the Pale's creatures, factions and keyed encounters converted into `creatures/`, `factions.json` and `encounters.json`, with the print stat blocks generated from them.
5. Run encounter and the `scene` effect, with encounter markers on Atlas points of interest (after EVENTS_FORMAT.md slice 2).
6. Faction view in the Companion and on the Atlas.
