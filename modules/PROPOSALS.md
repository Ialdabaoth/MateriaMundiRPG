# E9 Proposals

Ideas under discussion that are not yet agreed. When Heph agrees to one, it moves into the spec it belongs to (usually [WORKFLOWS.md](WORKFLOWS.md)), and this file keeps a one-line pointer to it.

| Proposal | Status | Would change |
| --- | --- | --- |
| P1. Open service adapters | **Agreed 2026-11-08**, now WORKFLOWS.md [Services and adapters](WORKFLOWS.md#services-and-adapters) | |
| [P2. Several root modules](#p2-several-root-modules) | Proposed 2026-11-08 (Heph asked for it) | WORKFLOWS.md "Dependencies" (`system`, new `provides`), "Campaign stack"; rules module manifests |
| [P4. Self-hosting everything](#p4-self-hosting-everything) | Proposed 2026-11-08 (Heph asked for the write-up) | The apps repo (site config, handler); WORKFLOWS.md "Services and adapters"; a new SELF_HOSTING.md |
| P5. Sheet layouts from modules | **Agreed in outline 2026-11-08** (Heph), now [SHEET_LAYOUT.md](SHEET_LAYOUT.md) | Companion sheet renderers (Postcard, PageSheet); rules module manifests (`layout`, `derive`) |
| P3. A campaign is a private module | **Agreed 2026-11-08**, now WORKFLOWS.md [Campaigns are private modules](WORKFLOWS.md#campaigns-are-private-modules) | |

## P2. Several root modules

**Idea (Heph, 2026-11-08):** `e9-core` is the first **root module**, the rules every other module points at. Other roots will follow: OSE, ACKS, LotFP, Shadowdark, maybe 4E and 5E. So modules need dependency resolution that copes with more than one root.

WORKFLOWS.md "Dependencies" already gives `requires`, `recommends`, `conflicts`, `overrides` and `system`, npm-style version ranges, a lockfile, one version per module, and the referee settling clashes (no automatic solver). This proposal keeps all of that and changes four things.

### 1. Roots say which system they provide

`system` today is a list of names (`e9`, `mm`). Instead, each root module declares the system it provides, and other modules name systems, not particular roots:

```json
{ "id": "e9-core", "kind": "rules", "provides": "e9", "version": "0.1.0" }
{ "id": "obx-core", "kind": "rules", "provides": "obx", "version": "0.1.0" }
```

A content module's `system` list then means "works with any root that provides one of these". `requires` still names an exact module when it needs one, e.g. a spell list that patches `e9-core` ids.

### 2. A campaign picks exactly one root

The campaign stack's first layer is one root. A module written for several systems keeps one file per system, as `bestiary/<ruleset>.json` already does in Beyond the Pale (OSE and MM stat blocks side by side), and the app loads only the files for the campaign's root. A module whose `system` list doesn't include the campaign's root can't be added; the app says why.

### 3. Roots can require roots

A root can build on another. `mm-core` (with its E9-for-MM option, `e9mm`) requires `e9-core`. So the resolver walks a chain: campaign root, then whatever it requires, each at one locked version. A cycle is an error.

### 4. Each root's licence is checked before it ships

A root carries another publisher's rules, so its `license` field and credits must match that publisher's terms, and the build refuses a root without them. Known terms to check: OSE and Shadowdark each have a third-party licence; 5E has the SRD 5.2 under CC BY 4.0; E9 is CC BY-SA 4.0; 4E's GSL is the hard case. ACKS and LotFP need checking.

### Build order if agreed

1. Add `provides` to `e9-core` (and `mm-core` when it lands); the Companion maps its ruleset ids (`e9`, `e9mm`, `mm`) to roots.
2. Campaigns record their root; the module picker filters by `system`.
3. Resolver: walk `requires` from the root, check ranges, write `campaign.lock.json`.
4. The first non-E9 root: **`obx-core`** (classic B/X under the OGL 1.0a, no trademarked name; Heph 2026-11-08). Beyond the Pale's planned OSE stat blocks become `bestiary/obx.json`.

### Open questions

1. ~~Is `e9mm` a system of its own, or an option inside `mm`?~~ **Decided (Heph, 2026-11-08):** E9 for Materia Mundi is an option inside MM. `mm-core` provides one system, `mm`, with an E9 option, and requires `e9-core`.
2. ~~Can a campaign ever mix roots?~~ **Decided (Heph, 2026-11-08):** a campaign chooses one root, then patches it with ideas from other systems. Those ideas come in as ordinary modules written for the campaign's root (overrides and additions to its ids), never as a second root.
3. ~~Should the apps (`hexmarch-companion`, `hexmarch-atlas`) be required by version from the first release?~~ **Decided (Heph, 2026-11-08):** yes, modules declare app compatibility from the start, but the referee can override it. Guideline for authors: only require the app features you actually use, at the lowest version that has them, so a module isn't locked out of older or newer apps for no reason.

## P4. Self-hosting everything

**Idea (Heph, 2026-11-08):** the whole suite is open, so take the case of a Linux enthusiast who wants to self-host everything: their own git server, chat server, and customised versions of our apps.

The licence already allows it: everything in the suite is CC BY 4.0 (see the repository's LICENSE.md), so anyone may run, change and redistribute it with credit. This proposal is about making it *practical*.

### What already works

- **The apps are static files.** The E9 Companion, Atlas and Scribe are built in the apps repo (named in `links.json` → `apps`, currently Hexmarch) and served as plain files. Any web server (Caddy, nginx, Apache) can host them.
- **Modules are static files too**, built from this repo with the module build. Any static host works.
- **Every device keeps its own data** and works offline ("Services and adapters" → Resilience).
- **The campaign archive is git**, which any git server can hold.

### The self-hosted stack

| Job | Self-hosted choice | Adapter |
| --- | --- | --- |
| Apps and modules | Caddy or nginx serving the built files | none needed |
| Git (campaign archive, module hosting) | Forgejo or Gitea | Forgejo API adapter (also covers Codeberg) |
| Chat, mailbox, signal | A Matrix server (Synapse, Conduit), or Ergo for IRC (text only) | Matrix adapter, IRC as a last resort |
| Files and snapshots, calendar | Nextcloud (WebDAV for files, CalDAV for calendars). On your own server you allow the apps' pages in, so the apps talk to it directly | WebDAV/CalDAV adapter |
| Voice | Jitsi Meet or Mumble | none: a link in the campaign file |
| Our handler | The same handler code, run on their own box | none |
| VTT (optional) | Foundry VTT can be self-hosted (paid, not open source). Owlbear Rodeo can't. | Foundry adapter |

A fully self-hosted table is then "the open adapters, pointed at your own servers".

### What we need to change

1. **A site config instead of fixed addresses.** Today the apps carry our addresses: the default module site, the SRD wiki, the Patreon link (`links.json` holds some of these already). Every address a self-hoster would change moves into one `site.json` read at build time and at run time, with ours as the defaults. An empty value hides a link, as `links.json` does now.
2. **A portable handler.** Write the handler as one standard web-request function with no Cloudflare-only features, so the same code runs on Cloudflare Workers, Deno, Node or in a container.
3. **The open adapters.** Forgejo, Matrix and WebDAV/CalDAV, in the order "Services and adapters" → Alternatives already suggests (Matrix, then Forgejo, then plain git), with WebDAV/CalDAV added for Nextcloud.
4. **A rule for forks so they still work together.** Fork freely. A changed app gets its own module id and name (the apps are modules too: `hexmarch-companion`, `hexmarch-atlas`), and says which protocol versions it speaks (`hexmarch-module/1`, `hexmarch-mail/1`, `hexmarch-campaign-state/1`). Our apps and a fork can then share campaigns. The licence requires credit; whether the "E9" name itself is protected is a trademark question, separate from the licence.
5. **SELF_HOSTING.md with a docker-compose example** covering the whole stack: web server, Forgejo, a Matrix server, Nextcloud, Jitsi and the handler, with the `site.json` that points the apps at them. Written once the site config and the first open adapter exist, and tested by actually standing the stack up.

### Build order if agreed

1. Site config (`site.json`) in the apps repo. Small, and useful on its own (staging sites, the custom domain move).
2. Portable handler, when the handler is first built.
3. The open adapters, one at a time, after the MVP's first adapter.
4. SELF_HOSTING.md and the docker-compose example, tested end to end.

### Open questions

1. Is a self-hosted stack an MVP goal, or after 1.0.0? (Suggested: the site config and portable handler during the MVP, since they cost little and avoid rework; the adapters and the compose file after.)
2. Should we publish an official container image of the apps, or only the compose file that builds them?
3. Protect the "E9" name for official builds (forks rename, like Firefox forks do), or leave the name open?
