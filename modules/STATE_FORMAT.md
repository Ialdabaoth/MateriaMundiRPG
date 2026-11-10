# Campaign state file (hexmarch-campaign-state/1)

One small JSON file holds the campaign's shared record between sessions: its parties (where each stands, its own game clock and session), what everyone knows, and who is playing. The Hexmarch Companion and the Hexmarch Atlas both read it. Only the referee writes it.

- **Where it lives.** For now each device keeps one per campaign (the Companion has one for "This device" too), and the referee can save and load it by hand (Campaign › State). With referee sign-in, **Update campaign** commits it to the campaign repository as `campaign/state.json` (MODULE_FORMAT.md section 7), and players read it from there.
- **The Hexmarch Atlas** (0.5.11) reads it from the Companion that embeds it: the Companion sends `{"type": "hexmarch-atlas", "state": <the file>}` when the map opens and after every change. On its own, the Atlas reads the Companion's saved file for the campaign in use on this device, since both apps share the site. Failing that, it keeps its own copy in the browser: a file loaded with **Load state file…**, or a party placed before 0.5.11. Party moves made in the Atlas follow "How it changes" below. They are written back to the device's file, or posted to the embedding app as party events. **Save state file** downloads the file. When the Companion's tab comes back into view, it reads the file again if a newer revision was saved meanwhile.
- **Since Companion 0.5.6** it replaces the Companion's `partyAt` setting. A party placed earlier moves into This device's state the first time the app opens.

```json
{
  "format": "hexmarch-campaign-state",
  "version": 1,
  "campaign": "kells-1422",
  "revision": 42,
  "updated": "2026-11-08T13:40:00.000Z",
  "rules": { "ruleset": "e9mm", "module": "mm-core", "option": "e9", "version": "0.1.0" },
  "parties": [
    {
      "id": "p-kells",
      "name": "The Kells company",
      "start": { "module": "isle-of-mists", "id": "arrive-at-the-keep" },
      "clock": { "start": "3507-05-01", "hours": 34.5 },
      "at": { "base": "https://ialdabaoth.github.io/MateriaMundiRPG/", "module": "isle-of-mists", "map": "atlas", "hex": "world:6947:25B2", "label": "6947:25B2", "hours": 2.5 },
      "session": { "number": 3, "open": false }
    }
  ],
  "active": "p-kells",
  "revealed": { "isle-of-mists": { "hexes": [], "places": ["baile-atha-troim"] } },
  "characters": [{ "id": "c-aldric", "name": "Aldric", "player": "", "party": "p-kells" }]
}
```

| Field | Meaning |
|---|---|
| `campaign` | The campaign file's `id`; `""` for This device. A file from another campaign is refused. |
| `revision`, `updated` | Every change adds one to `revision`. Loading a file older than the device's copy asks first. |
| `rules` | The ruleset the campaign plays with and the core rules module that provides it (format `hexmarch-rules/1`: `e9-core`, or `mm-core` and its `e9` option for Materia Mundi for E9), with that module's version. `module` is `""` when the campaign file links a ruleset file of its own. Written by the referee's device each time the file is saved. |
| `parties` | The campaign's parties (Heph 2026-11-10), in the order they were made. A new campaign has none. The referee makes them in the Atlas's Referee mode, after the campaign is built, and every invitation is to one of them. |
| `parties[].id`, `name` | A stable id (`p-` and a slug of the first name) and the name the referee gave it. |
| `parties[].start` | Where and when it began: one of the campaign's start positions, `{module, id}`, naming a `starts` entry of a module the campaign uses (SCRIBE.md section 2), or a start the referee placed by hand, `{module, site, date, hour}` (`site` a place slug, or `""` to place the party on the map). Kept once the party has moved on. |
| `parties[].clock.start` | The party's first day, `YYYY-MM-DD` in the setting's own years (Materia Mundi: AD + 2085, so 1 May 1422 is `3507-05-01`). Months and days run as in the Gregorian calendar. Each party keeps its own clock (Heph 2026-11-10). |
| `parties[].clock.hours` | Game hours since midnight of that day (from the start's `hour`; 8, 08:00, when it gives none). |
| `parties[].at` | Where the party stands, or `null` until the Atlas places it: the module's site (`base`) and `id`, and a 100-ft hex address (ATLAS_FORMAT.md "Party marker"). `hours` is the Atlas's running travel time since the party was placed. |
| `parties[].session` | The party's last session started (`0` before the first) and whether it is in play. Parties play their own sessions. |
| `active` | The party the referee used last, so the apps open on the same one; `""` when there are none. |
| `revealed` | Common knowledge, by module id: hexes and place slugs (module.json `sites`) that everyone knows. What a party or a character knows beyond that is stored by each character as `knowledge` entries (CHARACTER_FORMAT.md "Knowledge"): a party's map is the union of its members' knowledge and this. |
| `characters` | Everyone playing: sheet id, name, the player once players join by invite, and `party`, the party they are in (`null` until they join one; an NPC follower is in its leader's party). The sheets themselves live in `campaign/characters/`. |

**How it changes**

- Making a party (Atlas, Referee mode) adds it to `parties` with its start, a clock from the start's date and hour, `at: null` and session 0, and makes it `active`. The Atlas then places it at the start's place, or the referee places it on the map. The start's own `revealed` places become knowledge of each character as they join the party.
- Moving a party in the Atlas sets its `at`. Any travel time the Atlas adds also passes on that party's clock. Resetting the Atlas's running time does not turn the clock back. The hexes the party travels through become knowledge of its members.
- The referee can pass a party's time by hand (+1 hour, +8 hours, +1 day), set its start date, and start or end its session. Open and Close session procedures (EVENTS_FORMAT.md) will take over the session fields.
- Saving the file brings `characters` up to date from the party on the referee's device. Players named in the file are kept.

Readers fill anything missing with the defaults above and ignore hexes that aren't 100-ft addresses, so a hand-written file still opens. Files from before parties (top-level `clock`, `party`, `session`) are not read: until 0.8.X there is no compatibility layer (WORKFLOWS.md "Protocol names"), so rebuild them. A file with a higher `version` than the reader knows is refused.
