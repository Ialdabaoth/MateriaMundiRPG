# Campaign state file (e9-campaign-state/1)

One small JSON file holds the campaign's shared record between sessions: where the party stands, the game clock, what the party has found, the current session and who is playing. The E9 Companion and the E9 Atlas both read it. Only the referee writes it.

- **Where it lives.** For now each device keeps one per campaign (the Companion has one for "This device" too), and the referee can save and load it by hand (Campaign › State). With referee sign-in, **Update campaign** commits it to the campaign repository as `campaign/state.json` (MODULE_FORMAT.md section 7), and players read it from there.
- **Since Companion 0.5.6** it replaces the Companion's `partyAt` setting. A party placed earlier moves into This device's state the first time the app opens.

```json
{
  "format": "e9-campaign-state",
  "version": 1,
  "campaign": "kells-1422",
  "revision": 42,
  "updated": "2026-11-08T13:40:00.000Z",
  "rules": { "ruleset": "e9mm", "module": "mm-core", "option": "e9", "version": "0.1.0" },
  "clock": { "start": "3507-05-01", "hours": 34.5 },
  "party": { "base": "https://ialdabaoth.github.io/MateriaMundiRPG/", "module": "isle-of-mists", "map": "atlas", "hex": "world:6947:25B2", "label": "6947:25B2", "hours": 2.5 },
  "revealed": { "isle-of-mists": { "hexes": ["world:6947:25B2"], "places": ["cnoc-na-teamhrach"] } },
  "session": { "number": 3, "open": false },
  "characters": [{ "id": "c-aldric", "name": "Aldric", "player": "" }]
}
```

| Field | Meaning |
|---|---|
| `campaign` | The campaign file's `id`; `""` for This device. A file from another campaign is refused. |
| `revision`, `updated` | Every change adds one to `revision`. Loading a file older than the device's copy asks first. |
| `rules` | The ruleset the campaign plays with and the core rules module that provides it (format `e9-rules/1`: `e9-core`, or `mm-core` and its `e9` option for Materia Mundi for E9), with that module's version. `module` is `""` when the campaign file links a ruleset file of its own. Written by the referee's device each time the file is saved. |
| `clock.start` | The first day, `YYYY-MM-DD` in the setting's own years (Materia Mundi: AD + 2085, so 1 May 1422 is `3507-05-01`). Months and days run as in the Gregorian calendar. |
| `clock.hours` | Game hours since midnight of the start day (a new campaign starts at 8, 08:00). |
| `party` | Where the party stands, or `null`: the module's site (`base`) and `id`, and a 100-ft hex address (ATLAS_FORMAT.md "Party marker"). `hours` is the Atlas's running travel time since the party was placed. |
| `revealed` | By module id: hexes the party has seen and place slugs (module.json `sites`) it has found. The Atlas player view shows only these. |
| `session` | The last session started (`0` before the first) and whether it is in play. |
| `characters` | The party: sheet id, name, and the player once players join by invite. The sheets themselves live in `campaign/characters/`. |

**How it changes**

- Moving the party in the Atlas sets `party`. Any travel time the Atlas adds also passes on the clock. Resetting the Atlas's running time does not turn the clock back. The hex the party arrives in is added to `revealed`.
- The referee can pass time by hand (+1 hour, +8 hours, +1 day), set the start date, and start or end a session. Open and Close session procedures (EVENTS_FORMAT.md) will take over the session fields.
- Saving the file brings `characters` up to date from the party on the referee's device. Players named in the file are kept.

Readers fill anything missing with the defaults above and ignore hexes that aren't 100-ft addresses, so an older or hand-written file still opens. A file with a higher `version` than the reader knows is refused.
