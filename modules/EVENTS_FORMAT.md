# E9 Events and Procedures format (draft)

How a module says *what can happen* on its maps, and how each ruleset says *how it is resolved*, so the E9 Companion and E9 Atlas can run a hexcrawl at the table.
Designed with Heph on 2026-11-05. Status: **draft, nothing built yet**. Tables here extend the table format in MODULE_FORMAT.md section 6.

## 1. The idea in one paragraph

A module's `events.json` speaks only in **fiction**: triggers (when something can happen) and d6/d20 tables (what happens), whose rows **call procedures by name**. Each ruleset's `procedures.json` speaks in **mechanics**: it implements those names as steps (who rolls what, against what, and what it does to whom). The same module therefore runs under E9, E9 for Materia Mundi, Materia Mundi, or a third-party ruleset such as OSE, Dolmenwood or ACKS, provided someone writes a `procedures.json` for it. Everything that resolves is written to the session's **Events log**, which becomes the session's commit (MODULE_FORMAT.md section 7).

## 2. Files

```
modules/<module-id>/
  events.json                         triggers, tables, macro vocabularies, calendar (rule-generic; any *.json with an "events" block also counts)
  procedures/<ruleset-id>.json        this module's procedures for one ruleset
companion-app/src/rules/
  options/<ruleset-id>-options.json   gains a "conditions" list and "time" units (sections 6, 7)
  procedures/<ruleset-id>.json        the ruleset's generic procedures (save, morale, reaction, damage...)
```

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

Every `procedures.json` declares which rulesets it serves: `{"format": "e9-procedures/1", "rules": ["e9mm"], ...}`. `rules` is a list, so one file may serve several rulesets that share conditions and dice. A campaign only offers procedures written for its own ruleset.

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

- **`lod`** is `100ft`, `field`, `league` or `march`. A module with its own map scales (ATLAS_FORMAT.md, "Map scales per module") instead uses a level `id` from its ladder. A terrain trigger tests that level's own summary terrain (the most common terrain in the hex, as the Atlas computes it; ATLAS_FORMAT.md). A March-scale "enter bog" fires on entering a mostly-bog March even if the League underfoot is dry.
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

**Effects** are a fixed list, not a scripting language: `damage`, `condition` (from the ruleset's `conditions` list, with a duration), `heal`, `clock` (advance time), `ratchet` (±n on a region ratchet), `explore` (mark a hex), `site` (set a site's status), `scene` (add creatures to the current scene), `encounter-map` (open one, section 10), `note`. Every effect writes campaign state, so undo is a git revert.

**Text**: each step may have `text` (the referee's line) and `players` (the player-facing line). Templates fill `{who}`, `{target}`, `{target.player}`, `{roll}`, `{result}`, `{amount}`, `{place}`, `{terrain}`, `{action}`, any param, and any macro field.

## 8. Running: the referee confirms everything

Moving the party marker on the Atlas **queues** every trigger that applies (time by terrain, getting lost, encounter check, weather, terrain and place triggers). The referee runs each one with a tap, skips it, or reorders the queue. Nothing rolls without a tap, and every result can be applied or overridden before it touches state. Clock triggers queue the same way when time advances.

## 9. Who sees and who rolls

- Every step is **referee-only by default**. `"show": true` sends its `players` text to the party's Inbox; rolls stay hidden unless the step shows them.
- For any roll on a character, the referee chooses each time between **"Roll for {target}'s {action}"** (the referee rolls) and **"Have {target.player} roll for {target}'s {action}"** (a roll request goes to that player's Inbox, they roll on their own device, and the result returns to the queue).
- Defaults stack from weakest to strongest: the module's `recommend` on a trigger or step, then the referee's campaign setting, then the referee's choice on that single roll.

## 10. Encounter maps

An `encounter-map` effect opens the hand-made Encounter map of the site if it has one; otherwise, until generated maps exist, a blank grid of 5-ft squares sized to the Field hex's terrain. Encounter maps are the last build slice (section 11).

## 11. Build order

Each slice is usable at the table on its own:

1. This spec.
2. Manual procedure buttons and the Events log, with one real procedure (the wandering check) for each of e9, e9mm and mm.
3. Clock triggers, the module calendar and ruleset time units.
4. Place and terrain triggers off the party marker, with the referee queue.
5. Encounter maps.
