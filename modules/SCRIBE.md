# Hexmarch Scribe: campaign view and update checker (draft)

Hexmarch Scribe ("⬢ Scribe") is the module editor, the third app beside the Hexmarch Atlas and the Hexmarch Companion, at `/scribe/` from day one. It is part of the MVP. A campaign is a private module (PROPOSALS.md P3), so a campaign is made in Scribe, through a simplified **campaign view** of the full creator suite. This file covers that view, how a referee's edits to someone else's module are stored, and the **update checker** that runs whenever a module is opened.

Status: agreed in outline with Heph on 2026-11-08. Built in Scribe 0.1.x: steps 1 to 3, 7, 8 and 9 (step 3 became the start positions list in 0.6.x), the two files in section 5 (which follow WORKFLOWS.md "Invitations", agreed 2026-11-09), and the hand-over to the other apps by links. The alpha walkthrough worked end to end on 2026-11-09 and Scribe moved to 0.6.0 with the other apps. Still to build, in 0.6.x: steps 4 to 6 and the update checker (section 4). The format ids here (`e9-…`) move to `hexmarch-…` in 0.6.x (WORKFLOWS.md "Protocol names"). Builds on WORKFLOWS.md (Dependencies, Campaign stack, Trust, Invitations), PROPOSALS.md P1 to P3, MODULE_FORMAT.md and STATE_FORMAT.md.

## 1. From modules to a campaign

The campaign view is a short sequence of steps. Each step writes part of the campaign module, so a referee can stop at any point and pick up later.

| Step | What the referee does | What Scribe writes |
| --- | --- | --- |
| 1. Root | Pick one root module and its option (for example `mm-core` with its `e9` option). A campaign has exactly one root (P2). | `requires` entry for the root |
| 2. Modules | Add modules, or a bundle that offers several. Scribe resolves `requires`, offers `recommends`, refuses `conflicts`. | Further `requires`, in order; `campaign.lock.json` with exact versions and manifest hashes |
| 3. Start positions | Nothing to pick (Heph 2026-11-10): the campaign's **start positions** are every start of the modules it uses (section 2). Scribe lists them under each module ("Show Player Start Locations"). Leaving a start out is a job for the module editor tools, after 0.6.x. | Nothing: a new `campaign/state.json` has no parties and no start |
| 4. Conflicts and slicing | Settle each id that two modules change without a declared override; leave out any id, group or system half. | `overrides` with the referee's note and optional spoiler flag; the exclusion list |
| 5. Own content | House rules, plus the referee's own sites, NPCs, handouts and tables. Edits to another module's content are stored as patches (section 3). | The campaign module's own content and `patches` |
| 6. Parties and secrets | Parties are made **after** the campaign is built, in the Atlas's Referee mode (Heph 2026-11-10): a name and one of the campaign's start positions, or a start placed by hand. Each party keeps its own clock and sessions, and every invitation is to a party. Seed each character's private reveals from their background. | `parties` in `campaign/state.json` (STATE_FORMAT.md); `party:` and `character:` audiences in `private` (P3 section 4) |
| 7. Ready | **Build Campaign** saves the campaign. Scribe makes the creator's **Referee invitation** to it (below), then offers "Preview in Companion" and "Preview in Atlas". | The campaign on this device and one Referee invitation for the creator. "Open in Companion" hands the campaign over in a link (WORKFLOWS.md "Apps talk by links"). The apps load the campaign like any module (P3 "One loader"). |
| 8. Services | Say where the campaign lives for players: a **read URL** (where the player snapshot is published) and a **post URL** (where players send requests). The default will be the referee's own Apps Script (WORKFLOWS.md "Invitations", step 4); until it exists, any static host the referee can upload to (section 5). | `services` in Scribe's record of the campaign |
| 9. Publish | Publish the first player snapshot and the campaign pointer. **Invite stays disabled in the Companion until this is done**, because until then the campaign exists only on the referee's device. | `snapshot.json` and `campaign.json` (section 5); `published` in Scribe's record of the campaign |

**Invitations (Heph 2026-11-09).** There are two kinds: a **Referee invitation** and a **Player invitation**. One person may hold several of either kind, for different campaigns or for the same one. The Companion's campaign switcher lists one entry per invitation, and picking it sets Referee or Player mode. When a campaign is ready, it automatically gets a Referee invitation for the person who made it, so the creator opens their own campaign the same way anyone else would: by an invitation. Scribe makes only that first one. Every other invitation (more referees, every player: seats and join codes, WORKFLOWS.md "Invitations"), the mailbox and the request flow stay in the Companion, where the service adapters live (PROPOSALS.md P1). The invitation's format belongs to the Companion. Scribe's part ends at steps 8 and 9, which give the Companion something a player can open.

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
    "scenes": ["<scene id>"],
    "handouts": ["<handout id>"],
    "levels": [1, 3],
    "uses": ["<part id>"],
    "note": "<author's note to the referee>"
  }
]
```

| Field | Meaning |
| --- | --- |
| `id` | Stable within the module, like every other id. |
| `title`, `note` | The author's own words, shown to the referee when choosing. |
| `date`, `hour` | The first day (`YYYY-MM-DD` in the setting's years) and hour; they become the clock of a party that starts here (`parties[].clock`). |
| `site` | Where the party begins; the party marker goes on that site's hex. A hex address may be given instead. |
| `revealed` | What a party starting here knows: becomes knowledge of each of its characters as they join. |
| `scenes` | The module's own scenes (encounters.json `scenes` ids) that open play, in order. The start's words come from these, so the text stays the author's and is never copied into the start. |
| `handouts` | Handouts every player gets at the first session. |
| `levels` | Suggested character levels, lowest and highest. |
| `uses` | Optional: the parts of the module this start plays, for a module made of several adventures (Beyond the Pale's B2 to B5). Without it, the whole module is used. (Heph 2026-11-08.) Since starts belong to parties (2026-11-10), a start no longer slices the campaign; slicing is step 4's job. |

A module may offer any number of starts, or none. With none, or when the referee prefers, a party's start is placed by hand.

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

## 5. Services and Publish: the campaign pointer and the player snapshot

A player's Companion never sees the referee's device. It sees two small files, both plain JSON, which Publish writes and every later "Update campaign" in the Companion writes again, with the same code (the shared editing engine).

**The campaign pointer** (`campaign.json`) is what an invite link names. It says where the campaign lives right now, so if the referee moves to another service, the pointer changes and every invitation keeps working (WORKFLOWS.md "Resilience", campaign pointer).

```json
{
  "format": "hexmarch-campaign-pointer",
  "version": 1,
  "campaign": "kells-1422",
  "title": "Kells, 1422",
  "read": "https://<host>/kells-1422/snapshot.json",
  "post": "https://<post URL>",
  "adapters": { "store": "static", "mail": "manual" },
  "updated": "2026-11-09T13:00:00Z"
}
```

**The player snapshot** (`snapshot.json`, at the read URL) is everything a player's app reads: the campaign as a module, its lockfile, the shared part of the state file, and the receipts.

```json
{
  "format": "hexmarch-snapshot",
  "version": 1,
  "campaign": "kells-1422",
  "revision": 1,
  "published": "2026-11-09T13:00:00Z",
  "ruleset": "e9mm",
  "site": "https://<the modules' data site>/",
  "module": { "...": "the campaign module.json" },
  "lock": { "...": "campaign.lock.json" },
  "state": { "...": "state.json, shared parts only" },
  "receipts": [],
  "private": {}
}
```

| Field | Meaning |
| --- | --- |
| `revision` | One more on every publish; a player's app takes a snapshot only if it is newer than the one it has. |
| `ruleset`, `site` | What the player's Companion needs to open the campaign: the ruleset its root provides, and where its modules are published. |
| `state` | The state file as players may see it: clock, party position, `revealed` (common knowledge), session, and `characters` as `{id, name, player}` only. Anything referee-only (a `private` part, `ref:` audiences, creatures, other characters' knowledge) never goes in the shared part. |
| `receipts` | The ids of player envelopes the referee's app has seen (WORKFLOWS.md "Receipts close the loop"). Empty at the first publish. |
| `private` | What only one player may read, keyed by recipient: `private[<recipient>].characters[<character id>].knowledge` is that character's knowledge part (CHARACTER_FORMAT.md "Knowledge", in the apps repo), which the player's Companion puts in place of that part of the sheet. Until device keys exist the recipient is the character id the invitation names; with keys, each recipient's part is encrypted to them (P3 section 4) and the shape stays the same. Approved stats, gear and flavour are not in the snapshot: the player already holds them, and receipts say what was approved. |

**Services for now.** Until the Apps Script adapter is built, the referee gives Scribe a **folder URL** on any static host they can upload to (GitHub Pages, their own site), and optionally a post URL. Publish then hands them `campaign.json` and `snapshot.json` to upload into that folder. The read URL is `<folder>snapshot.json` and the pointer is `<folder>campaign.json`. This is the Manual adapter of PROPOSALS.md P1, and it costs nothing (WORKFLOWS.md: cheap and free options for now). A campaign published this way can be read by anyone who has the URL, so keep secrets out of it until `private` is encrypted.

**What Scribe records.** Scribe's record of the campaign on the device (`scribe-campaign:<id>`) gains `services: {folder, read, post, pointer}` and, after Publish, `published: {revision, at}`. The Companion enables Invite for a campaign whose record has `published`, and its invite links name the pointer. The record travels to the Companion in a `campaign` link, and the Companion sends play back to Scribe in an `update` link (state, each party member's knowledge, receipts), which Publish uses (WORKFLOWS.md "Apps talk by links").

## 6. Open questions

1. Does `kind: "campaign"` become a manifest value of its own (P3 open question 4)? Scribe's campaign view would open only for those.
2. Should the update checker also run on a schedule in the referee's Apps Script (P1), so the Inbox shows "needs a decision" before Scribe is opened?
