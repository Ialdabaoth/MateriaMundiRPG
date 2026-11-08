# E9 Scribe: campaign view and update checker (draft)

E9 Scribe is the module editor, the third app beside the E9 Atlas and the E9 Companion, at `/scribe/` from day one. It is part of the MVP. A campaign is a private module (PROPOSALS.md P3), so a campaign is made in Scribe, through a simplified **campaign view** of the full creator suite. This file covers that view, how a referee's edits to someone else's module are stored, and the **update checker** that runs whenever a module is opened.

Status: agreed in outline with Heph on 2026-11-08. Nothing is built yet. Builds on WORKFLOWS.md (Dependencies, Campaign stack, Trust), PROPOSALS.md P2 and P3, MODULE_FORMAT.md and STATE_FORMAT.md.

## 1. From modules to a campaign

The campaign view is a short sequence of steps. Each step writes part of the campaign module, so a referee can stop at any point and pick up later.

| Step | What the referee does | What Scribe writes |
| --- | --- | --- |
| 1. Root | Pick one root module and its option (for example `mm-core` with its `e9` option). A campaign has exactly one root (P2). | `requires` entry for the root |
| 2. Modules | Add modules, or a bundle that offers several. Scribe resolves `requires`, offers `recommends`, refuses `conflicts`. | Further `requires`, in order; `campaign.lock.json` with exact versions and manifest hashes |
| 3. Start | Pick one of the modules' **starts** (section 2), or place the party by hand on the Atlas and set a date. | `campaign/state.json`: `clock.start`, `party`, the `all` audience in `revealed` |
| 4. Conflicts and slicing | Settle each id that two modules change without a declared override; leave out any id, group or system half. | `overrides` with the referee's note and optional spoiler flag; the exclusion list |
| 5. Own content | House rules, plus the referee's own sites, NPCs, handouts and tables. Edits to another module's content are stored as patches (section 3). | The campaign module's own content and `patches` |
| 6. Parties and secrets | One party, or several (West Marches). Seed each character's private reveals from their background. | `party:` and `character:` audiences in `private` (P3 section 4) |
| 7. Open | "Open in Atlas" and "Open in Companion". | Nothing new. The apps load the campaign like any module (P3 "One loader"). |

Invites, the mailbox and every other player-facing service stay in the Companion, where the service adapters live (PROPOSALS.md P1). Scribe stops at step 7.

The same steps work for an existing campaign: opening it in Scribe shows each step's current answer, and the referee changes any of them.

## 2. Starts: how a module offers to begin a campaign

Today a module says nothing about how play begins. A new optional field in the module's source `module.json` (MODULE_FORMAT.md section 3) lists the ways its author suggests:

```json
"starts": [
  {
    "id": "arrive-at-the-keep",
    "title": "<author's title>",
    "date": "3507-05-01",
    "hour": 8,
    "site": "<site name>",
    "revealed": { "places": ["<site name>", "<site name>"], "hexes": [] },
    "handouts": ["<handout id>"],
    "levels": [1, 3],
    "note": "<author's note to the referee>"
  }
]
```

| Field | Meaning |
| --- | --- |
| `id` | Stable within the module, like every other id. |
| `title`, `note` | The author's own words, shown to the referee when choosing. |
| `date`, `hour` | The first day (`YYYY-MM-DD` in the setting's years) and hour; they become `clock.start` and `clock.hours`. |
| `site` | Where the party begins; the party marker goes on that site's hex. A hex address may be given instead. |
| `revealed` | Common knowledge at the start: becomes the `all` audience. |
| `handouts` | Handouts every player gets at the first session. |
| `levels` | Suggested character levels, lowest and highest. |

A module may offer any number of starts, or none. With none, or when the referee prefers, step 3 is done by hand.

## 3. Patches: editing someone else's module

When a referee changes content that belongs to another module (a site's description, an NPC's stats, a table entry), Scribe saves **only the changed fields**, never a copy of the whole entry. Upstream fixes to every other field still reach the campaign.

Each patch remembers what it was made against, so the update checker can tell when the author later changed the same field:

```json
"patches": {
  "isle-of-mists/site/cnoc-na-teamhrach": {
    "base": "0.4.10",
    "fields": {
      "note": { "was": "sha256:…", "now": "<referee's text>" }
    }
  }
}
```

- `base` is the module version the patch was made against.
- `was` is a hash of the field's upstream value at that version. If the upstream value still matches `was`, the patch applies quietly. If it doesn't, the author changed that field too, and the update checker asks the referee.
- Removing a patch returns the field to the module's current value.

This is git's three-way merge reduced to single fields: the base, the author's change and the referee's change.

## 4. The update checker

Opening any module in Scribe, a campaign included, runs the **update checker**. It walks the module's dependencies and reports which new versions can be taken quietly and which need a decision. It is a checker in the WORKFLOWS.md sense (Trust: checkers): it ships as a module with `e9-core`, and referees can swap or add their own.

**What it does**

1. Reads the module's `requires` and the lockfile, then walks every dependency's own `requires` (the whole tree, root included).
2. For each module, fetches its manifest and finds newer versions: inside the declared range, and beyond it.
3. Reads the release notes of every version between the locked one and the newest (added, changed and removed ids, WORKFLOWS.md Versioning).
4. Checks each changed or removed id against what this module depends on:
   - the module's `overrides` and conflict decisions,
   - its `patches` (does `was` still match?),
   - its exclusions,
   - ids the campaign actually uses: characters' sheets, parties, `state.json`, the module's own content that points at that id,
   - new collisions: an id that two modules now both change without a declared override.
5. Reports the result.

**The report sorts every update into three groups**

| Group | Meaning | What happens |
| --- | --- | --- |
| Quiet | Patch or minor version; no changed id touches anything above. | Listed with its release notes and one Accept button. |
| Needs a decision | Any version where a changed or removed id touches an override, a patch, an exclusion, a used id, or makes a new collision. | One review card per item, showing the old value, the new value and the campaign's value. The referee keeps theirs, takes the author's, or writes a new version. |
| Blocked | A major version outside the declared range, or two modules needing versions of a third that can't both be met. | Explained in plain words; the referee picks a version or drops a module. There is no automatic solver. |

Nothing changes until the referee accepts. Accepting rewrites the lockfile, updates each patch's `base` and `was`, and stores every decision with the referee's note, so it is applied again after the next update (as in the Campaign stack). A decision whose id changes again in a later update comes back for a second look.

**When it runs.** On opening a module in Scribe, and on demand. The Companion's Inbox already lists available updates (WORKFLOWS.md Campaign stack); its Review button opens the same report in Scribe.

**Creators use it too.** A module author opening their own module sees the same report for the modules it requires, such as a new `e9-core`, before releasing.

## 5. Open questions

1. Does `kind: "campaign"` become a manifest value of its own (P3 open question 4)? Scribe's campaign view would open only for those.
2. Should a start be able to name its own module subset (for example a start that uses only B2 of the Beyond the Pale quartet)?
3. Should the update checker also run on a schedule in the referee's Apps Script (P1), so the Inbox shows "needs a decision" before Scribe is opened?
