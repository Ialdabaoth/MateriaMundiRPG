# E9 Events and Procedures format (draft)

How a module says *what can happen* on its maps, and how each ruleset says *how it is resolved*, so the Hexmarch Atlas can run a hexcrawl at the table.
Designed with Heph on 2026-11-05. Status: **draft, being built in the Atlas** (Heph 2026-11-15: "Procedures lives primarily in the Atlas"). Tables here extend the table format in MODULE_FORMAT.md section 6.

**Where it runs.** The Atlas runs procedures, in Referee mode: it loads the events and procedures, queues what applies when a party moves or its clock passes, runs what the referee taps, and keeps each party's Events log. The Companion and Scribe take part only where play spills over to them (a `show` line in a player's Inbox, a roll request, a closed session's log to publish); those parts are specified when they are built.

## 1. The idea in one paragraph

A module's `events.json` speaks only in **fiction**: triggers (when something can happen) and d6/d20 tables (what happens), whose rows **call procedures by name**. Each ruleset's `procedures.json` speaks in **mechanics**: it implements those names as steps (who rolls what, against what, and what it does to whom). The same module therefore runs under E9, E9 for Materia Mundi, Materia Mundi, or a third-party ruleset such as OSE, Dolmenwood or ACKS, provided someone writes a `procedures.json` for it. Everything that resolves is written to the session's **Events log**, which becomes the session's commit (MODULE_FORMAT.md section 7).

## 2. Files

```
modules/<module-id>/
  events.json                         triggers, tables, macro vocabularies, calendar (rule-generic; any *.json with an "events" block also counts)
  procedures/<ruleset-id>.json        this module's procedures for one ruleset
modules/<rules-module>/               the ruleset's own module (e9-core, mm-core, obx-core...; rules-modules.md)
  rules.json                          gains a "conditions" list and "time" units (sections 6, 7)
  procedures/<ruleset-id>.json        the ruleset's generic procedures (travel, sight-range, save, morale, reaction, damage...)
```

The ruleset's procedures live in its rules module (2026-11-15), not inside an app: rules are modules, and the Atlas reads modules. A campaign's lockfile therefore pins the procedures it plays with.

### Multiple files (Heph 2026-11-05)

`events.json` is a convention, not a requirement. **Any `*.json` file in the module folder (at any depth) that has a top-level `"events"` block is merged into the module's events**, whatever its name, so a referee can keep `bog-hazards.json`, `fomhoire.json` and `weather.json` side by side. The same rule applies to `"encounters"` blocks (the sibling encounters spec). One file may hold both blocks. An `"events"` block holds any of `triggers` (a list), `tables`, `macros` and `calendar`:

```json
{"events": {"triggers": [...], "tables": {"bog-hazards": {...}}, "macros": {"threat": [...]}}}
```

Merging and name collisions:

- Files load in **path order** (case-sensitive, `/` before letters), so the result never depends on the disk or the browser.
- **Triggers and tables** are keyed by `id`. A duplicate id inside one layer (the module, or the campaign) is **flagged on load**, and the first file in path order keeps it. Nothing is silently replaced.
- **Macros** with the same vocabulary name must list the same values. A different list is flagged, and the first one is kept.
- **Calendar**: at most one per module. A second one is flagged and ignored.
- **Layers**: a referee's `campaign/` folder is a later layer (MODULE_FORMAT.md section 7). An id there **replaces** the module's id on purpose, which is how a referee house-rules a table without editing the module. The load report lists each replacement so it is never a surprise. To remove a module trigger, the campaign gives the same id with `"off": true`.

The load report names the file for every warning, such as `fomhoire.json: table "bog-hazards" already defined in bog-hazards.json`.

Every `procedures.json` declares which rulesets it serves: `{"format": "hexmarch-procedures/1", "rules": ["e9mm"], ...}`. `rules` is a list, so one file may serve several rulesets that share conditions and dice. A campaign only offers procedures written for its own ruleset.

## 3. Name lookup and the contract

A procedure name is resolved in this order:

1. the module's `procedures/<ruleset>.json`,
2. the ruleset's generic `procedures/<ruleset>.json`,
3. `"aliases": {"mired": "stuck-in-bog"}` in either file, then lookup again.

**The contract:** every procedure name and every macro name that `events.json` uses must resolve for the campaign's ruleset. When a module loads, the app lists anything missing (as it does for unknown conditions) instead of failing at the table.

Procedures may call each other and the ruleset's generic procedures. Calls and nested tables share one **depth limit of 6**; a deeper chain stops with a warning in the log, so a loop can never hang the app.

## 4. Triggers (in `events.json`)

```json
{"id": "bog-entry", "on": "terrain", "terrain": "bog", "edge": "enter", "lod": "league", "mode": "boundary", "run": {"table": "bog-hazards"}}
```

| `on` | Fires when | Fields |
|---|---|---|
| `clock` | the campaign clock passes a boundary | `every`: `{"n": 1, "unit": "day"}` (units in section 6) |
| `place` | the party enters or leaves a hex or site | `place`: a site slug or a hex address `<map>:<hex>`; `edge`: `enter` / `leave` |
| `terrain` | the party enters or leaves terrain of a type | `terrain`, `edge`, `lod`, `mode` |
| `manual` | the referee presses its button | `label` |

- **`lod`** is `100ft`, `furlong` (500 ft), `field`, `league` or `march`. A module with its own map scales (ATLAS_FORMAT.md, "Map scales per module") instead uses a level `id` from its ladder. A terrain trigger tests that level's own summary terrain (the most common terrain in the hex, as the Atlas computes it; ATLAS_FORMAT.md). A March-scale "enter bog" fires on entering a mostly-bog March even if the League underfoot is dry.
- **`mode`**: `boundary` (default) fires only when crossing from other terrain into this one (or out, for `leave`); `each` fires on every hex of that terrain entered, for things like a per-hex check to get stuck in the bog.
- `run` names either a table (`{"table": id}`) or a procedure (`{"call": name, "with": {...}}`).
- An optional `"recommend": {"roller": "player" | "referee"}` gives the module's recommended default for who rolls (section 9).

## 5. Tables, macros and arguments (in `events.json`)

Tables are d20 or d6 only (a big table is a d6 choosing among d20 sub-tables, MODULE_FORMAT.md section 6). This dice rule binds `events.json` only; a ruleset's procedures roll whatever its own system rolls. A row may now call a procedure:

```json
{"roll": [7, 9], "text": "Fomhóire scouts shadow the party.", "call": "ambush", "with": {"creature": "fomhoire-scout", "count": "1d6", "threat": "dangerous"}}
```

**Arguments are fiction only.** `with` may carry: `who` (a role), `where` (a site slug or hex address), `creature` or `site` (module ids, which each ruleset resolves through its own bestiary), `count` (a number or d6/d20 dice), free `text`, and **macro names**. Never raw mechanics (difficulties, modifiers, damage numbers), because those mean nothing in another system.

**Macros** are author-defined vocabularies, declared once:

```json
"macros": {"threat": ["trivial", "minor", "serious", "dangerous", "deadly"], "fey-mood": ["kindly", "fickle", "wrathful"]}
```

Each `procedures.json` expands every name for its ruleset, to a number, a dice amount, a label, a condition, or a small bundle of those:

```json
"macros": {"threat": {"serious": {"difficulty": "hard", "damage": "1d6", "condition": "shaken"}}}
```

An OSE file might expand `serious` to `{"save": -2, "damage": "1d6"}`. An unexpanded name is flagged on load. Description strings may use macros too (`{threat}` reads "deadly").

## 6. Time and calendar

The clock stores **real time**: minutes since the campaign began. `events.json` writes clock triggers in plain units (`minute`, `hour`, `day`, `week`, `month`). Each ruleset names its own units in its options file (`"time": {"turn": 10, "watch": 240}` in minutes), and its procedures may use them ("advance 1 turn"). The **calendar comes from the module**, not the ruleset: `"calendar": {"start": "1422-05-01", "kind": "julian"}` for Beyond the Pale; another setting brings its own months and holy days.

## 7. Procedures (in `procedures.json`)

A procedure is a list of steps. Every step may carry a description template that is emitted to the Events log when it runs.

```json
"stuck-in-bog": {
  "params": ["who", "threat"],
  "steps": [
    {"role": "who", "text": "{who} pushes into the bog."},
    {"roll": "save", "vs": "{threat.difficulty}", "as": "escape", "show": true,
     "text": "{who} struggles free ({roll}).", "players": "Roll to keep your footing."},
    {"branch": "escape", "fail": [
      {"effect": "damage", "target": "who", "amount": "{threat.damage}", "text": "{who} sinks to the waist and takes {amount} damage."},
      {"effect": "condition", "target": "who", "condition": "stuck", "for": {"n": 1, "unit": "turn"}}
    ]}
  ]
}
```

| Step | Does |
|---|---|
| `role` | picks who is involved: `party`, `leader`, `watch`, `random`, `failed` (whoever failed the last roll), or a named param |
| `roll` | rolls dice or a ruleset roll (save, attack, check) and stores the result under `as` |
| `table` | rolls on a table (module or ruleset) |
| `branch` | chooses steps by a stored result: `pass` / `fail`, or by ranges |
| `call` | runs another procedure, with fiction-only `with` |
| `effect` | changes state (below) |
| `note` | emits text only |

| `result` | gives the procedure's answer, for a procedure the Atlas asks a question of (below) |
| `walk` | runs another procedure once for each hex of a route (below) |

**Questions the Atlas asks.** Some procedures answer a question instead of changing state, and the Atlas calls them by these names whenever it needs the answer. Every ruleset implements them, so the Atlas has no rules numbers of its own:

| Name | Params | Answers |
|---|---|---|
| `travel` | `terrain`, `road` (`roman`, `local`, `trail` or none) | the time multiplier against the module's pace (`1` normal pace, `2` twice as slow, `null` no travel on foot) |
| `sight-range` | `terrain` (later light and height) | how far one sees, in miles |

A `result` step answers with a number, or looks it up: `{"result": {"by": "terrain", "of": {"woods": 1.5, "hills": 6}, "else": 3}}`. A module's terrain type keeps the last word on its own map: its `travel` and `sight` fields in the atlas (ATLAS_FORMAT.md) win over the procedure, so a module can say its bog is worse than most. Questions run silently: they write nothing to the Events log.

**Arithmetic.** A field whose template fills to plain arithmetic is worked out: `"hours": "{mi} * {pace} / {mph}"` becomes a number. Numbers, `+ - * /` and brackets only; anything else stays text.

**Walking a route** (Heph 2026-11-15). `{"walk": "move", "stop": "queued"}` runs `move` once for each hex from the party to where it is going, at the level the map shows, with the params `from`, `to` (hex addresses), `terrain`, `road`, `mi` (miles crossed in that hex), `mph` (the module's pace) and `pace` (the `travel` answer for that hex, or the module's own multiplier). After each hex the terrain and place triggers it sets off join the queue. **The procedure decides where the walk stops**: `"stop": "queued"` stops at the first hex where something joined the queue, so it is resolved where it happens, and the referee taps Continue to go on; `"stop": "never"` goes to the end and queues everything. A `halt` effect in the walked procedure (a failed lost check, say) stops it at that hex either way. A hex with no travel on foot ends the walk before it.

**Offers** (Heph 2026-11-15). A procedure can offer itself on the map: `"offer": "hex"` lists it when the referee has a party shown and clicks another hex, with `"label"` ("Navigate to here") and `"about"` (its tooltip). Each item previews itself without rolling: the hexes and time, where it would stop and for what, and the rolls its steps make (each `roll` step's `label`, or its dice). A second click on the same hex runs the default: the campaign's choice (`defaults.hex` in the state file, set with the menu's star), else the procedure the ruleset marks `"default": true`. The Route tool runs `navigate` along the stops picked by hand. Later contexts may be `party`, `site` and `creature`.

The ruleset's `navigate` is the move: `{"offer": "hex", "label": "Navigate to here", "default": true, "steps": [{"walk": "move", "stop": "queued"}]}`, and its `move` passes the time and moves the party (`clock`, `move`, `reveal`). What a ruleset rolls on the way (getting lost, wandering checks, forced marches) is written in that ruleset's own module.

**Effects** are a fixed list, not a scripting language: `damage`, `condition` (from the ruleset's `conditions` list, with a duration), `heal`, `clock` (advance time), `ratchet` (±n on a region ratchet), `explore` (mark a hex), `site` (set a site's status), `scene` (add creatures to the current scene), `encounter-map` (open one, section 10), `move` (the party's position), `reveal` (what is in sight from there becomes the members' knowledge), `halt` (stops a walk), `note`. Every effect writes campaign state, so undo is a git revert.

**Text**: each step may have `text` (the referee's line) and `players` (the player-facing line). Templates fill `{who}`, `{target}`, `{target.player}`, `{roll}`, `{result}`, `{amount}`, `{place}`, `{terrain}`, `{action}`, any param, and any macro field.

## 8. Running: the referee confirms everything

Moving the party marker on the Atlas **queues** every trigger that applies (time by terrain, getting lost, encounter check, weather, terrain and place triggers). The referee runs each one with a tap, skips it, or reorders the queue. Nothing rolls without a tap, and every result can be applied or overridden before it touches state. Clock triggers queue the same way when time advances. The queue and the log sit in the referee's party box, one per party.

**The Events log** is kept by each party, in the state file as `parties[].log` (STATE_FORMAT.md): the current session's entries, oldest first, each `{"at": <party clock hours>, "proc": <name>, "text": <referee line>, "players": <player line, if shown>, "rolls": [...], "effects": [...]}`. Every party has its own clock and session, so its log runs on that clock. Closing a session moves its log out of the state file into the session's record (`campaign/sessions/<party>-<number>.json`), which becomes the session's commit (MODULE_FORMAT.md section 7), and the next session starts an empty log.

## 9. Who sees and who rolls

- Every step is **referee-only by default**. `"show": true` sends its `players` text to the party's Inbox; rolls stay hidden unless the step shows them.
- For any roll on a character, the referee chooses each time between **"Roll for {target}'s {action}"** (the referee rolls) and **"Have {target.player} roll for {target}'s {action}"** (a roll request goes to that player's Inbox, they roll on their own device, and the result returns to the queue).
- Defaults stack from weakest to strongest: the module's `recommend` on a trigger or step, then the referee's campaign setting, then the referee's choice on that single roll.

## 10. Encounter maps

An `encounter-map` effect opens the hand-made Encounter map of the site if it has one; otherwise, until generated maps exist, a blank grid of 5-ft squares sized to the Field hex's terrain. Encounter maps are the last build slice (section 11).

## 11. Build order

Each slice is usable at the table on its own:

1. This spec.
2. **The runner, in the Atlas** (2026-11-15): loading and merging, name lookup, the depth limit and the load report; the referee's queue and Events log in the party box; **manual triggers** (`on: "manual"`, Heph 2026-11-15), a button for each in the party box that queues it; and the Atlas's own rules numbers moved into procedures (`travel` and `sight-range` in e9-core), so its maps work as before but a ruleset can change them.
3. Place, terrain and clock triggers off each party's marker and clock (the module calendar, ruleset time units), with the wandering check as the first table-driven procedure for each of e9, e9mm and mm.
4. What spills over to the other apps: `show` lines and roll requests to the Companion, closed sessions' logs published through Scribe.
5. Encounter maps.
