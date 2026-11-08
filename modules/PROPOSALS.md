# E9 Proposals

Ideas under discussion that are not yet agreed. When Heph agrees to one, it moves into the spec it belongs to (usually [WORKFLOWS.md](WORKFLOWS.md)), and this file keeps a one-line pointer to it.

| Proposal | Status | Would change |
| --- | --- | --- |
| [P1. Open service adapters](#p1-open-service-adapters) | Proposed 2026-11-08 (Heph thinking out loud) | WORKFLOWS.md "Mailbox and archive", "Live channel", "Accounts", "VTTs"; invite links |
| [P2. Several root modules](#p2-several-root-modules) | Proposed 2026-11-08 (Heph asked for it) | WORKFLOWS.md "Dependencies" (`system`, new `provides`), "Campaign stack"; rules module manifests |

## P1. Open service adapters

**Idea (Heph, 2026-11-08):** don't tie campaign play to one outside service. Make it an open, flexible system: Google is one option, Discord another, and so on, plus a small handler on our end.

Today WORKFLOWS.md uses Google (with Gmail sign-in for everyone) for the mailbox, snapshots, the live-channel handshake and the session calendar, with GitHub as the referee's archive. This proposal keeps those as defaults but makes each one swappable, the same way the git host adapter already plans for GitHub first and Codeberg or Forgejo later.

### First principle: players need only URLs (Heph, 2026-11-08)

The player side is utterly tech-agnostic: **if a player can open URLs, they're in.** No account anywhere, no particular phone. Accounts (Google, Discord, GitHub, a VTT) are a **referee-side** choice only. Every adapter therefore has two halves: the referee half may sign in to a service, and the player half may only fetch and post to URLs.

- **Reading** is any public URL the referee's adapter publishes: a Drive "anyone with the link" file read through Google's API with no sign-in, GitHub Pages, or any static host. Snapshots hold only player-visible content, and the link is unguessable.
- **Writing** is a URL the player's app can post to:
  - a **Discord webhook** (just a URL; the player needs no Discord account),
  - a **Google Form** (anonymous submissions into a Sheet the referee owns; the app can't confirm delivery, and Google could change it),
  - **our handler** (a per-campaign mailbox URL),
  - the **live channel** straight to the referee's laptop during a session.
- **Identity** is a key, not an account. Each device makes its own key pair and signs its envelopes; the referee approves that key when the player joins. A player is "the device holding this key".
- **The invite link carries everything:** where to read, where to post, and the campaign's id. Tap or scan it and you're in.
- **Receipts close the loop.** Every envelope has an id. Whenever the referee's app runs, it collects new requests and writes a receipt list (the ids it has seen) into the public snapshot. The player's app reads it and shows **Sent → Received → Approved** (or Sent back). If an envelope is still missing after the referee's next sync, the player's app sends it again, and the id stops it from being counted twice. Nobody confirms anything by hand. With a post URL that can't answer (a Google Form), "Received" only appears once the referee's app has run, which can be hours between sessions.
- **Apps Script web app (likely better than a Form).** A small script in the referee's own Google account, hosted free by Google, gives a post URL that answers. The player sees "Received" at once, even with the referee's laptop closed. It can also hold the live channel's handshake for remote players, closing the gap below. It runs on the referee's account, so it is still not a server of ours. **To check:** that a browser page can read its reply, and how simple the one-time setup can be for a referee.
- **The same script as a polling Discord bot.** A time trigger runs it with nobody online, as often as once a minute. It calls Discord's API from Google's servers with the bot token kept in the script, so browser limits don't apply (this also sidesteps the Discord browser-read test). Each run it reads new channel messages, posts receipts and replies, edits pending downtime posts once the referee's app approves them, and posts session events. Every 5 minutes uses about 15 of a free account's 90 trigger minutes a day. **It can't:** hold Discord's live gateway connection (runs stop after 6 minutes), and probably can't serve slash commands or buttons, which need an answer within 3 seconds plus a signature check that Apps Script lacks (untested). Live features and buttons stay with the referee's open app or our handler.
- So **one script in the referee's Google account** can be the instant post URL, the remote handshake, and a 1–5 minute Discord bot.
- **Handover between the script and the referee's app (Heph, 2026-11-08).** With the referee online, their Companion or Atlas is the live Discord bot; offline, the script batches every few minutes. The script can't call the app (a browser app has no address), so the app announces itself:
  1. The referee's app opens and checks in with the script: "I'm here; give me everything since message X."
  2. The script hands over its backlog and the **cursor** (the last Discord message handled).
  3. The app takes a **lease**, checking in about once a minute. While the lease is fresh, the script's runs do nothing.
  4. Live mode: the app handles Discord in real time.
  5. When the app closes or crashes, the lease runs out after a few minutes and the script carries on from the cursor.

  One cursor plus one lease means nothing is handled twice and nothing falls through the gap. Only one device holds the lease, normally the referee's laptop (the session host). **To test:** whether a browser can hold Discord's live gateway connection (a WebSocket, which browsers usually allow even when the REST API is blocked). If it can listen but not post, the app listens live and posts through the script.
- **One gap:** the live channel's handshake for remote players needs a meeting point both devices can write to (the handler, the webhook, or a pasted code). In person, a QR code covers it.
- **Apple:** an iPhone user without Google has iCloud Drive, but a web app can't use it. Apple's web route (CloudKit JS) only reaches a container our app owns and needs a $99/year developer account. Under this principle it isn't needed on the player side; it could become a referee-side adapter later.

### Jobs, not services

The apps ask for only five things. Each one is a small interface, and any service that can do the job can implement it.

| Job | What the apps need | Used for |
| --- | --- | --- |
| **Who** | Sign in (referee side); say who a person is (a device key on the player side) | Invites, request authors, scoped referee roles |
| **Mail** | Send a request; list waiting ones; mark one handled | Player requests, approvals, downtime, sub-ref requests |
| **Store** | Write and read a campaign snapshot | Players reading a private campaign between sessions |
| **Signal** | Pass a few small messages so two devices can find each other | The live channel's handshake, and its slow fallback |
| **Schedule** | Post a session; collect RSVPs | The roll call before each session |

The **archive** (the campaign git repo, written only by the referee) stays as it is: git is already behind its own host adapter.

### One envelope

Every request, approval, handout, snapshot notice and handshake travels as one small JSON message (working name `e9-mail/1`): who sent it, to whom, which campaign, a kind, a body, and an id. Adapters only move envelopes and never read the body, so a new service never touches game logic.

### Adapters, mixed per campaign

The campaign file says which adapter does each job, so a table can mix them. For example, Discord for Mail and Signal, GitHub for Store, Google for Schedule. Another table might use Google for everything.

| Adapter | Who | Mail | Store | Signal | Schedule | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| **Google** | Gmail sign-in (referee) | Drive folder inbox (players post to an Apps Script web app, or a Google Form) | Drive folder | Apps Script web app, or Drive files (slow) | Calendar invites and RSVPs | No server of ours. Needs a Google Cloud OAuth client (`drive.file`). The current default. |
| **Discord** | Discord sign-in | Channel messages (players post through a webhook) | Channel attachments | Channel messages | Scheduled events ("Interested") | Discord keeps the messages, so the channel itself is the mailbox. The referee's open app acts as the bot, with the token on that device only. **To test:** whether Discord's API lets a browser page read channel messages. If not, reads go through the referee's Apps Script bot or our handler. |
| **GitHub** | GitHub sign-in | Issues | Repo files | Issues (slow, rate-limited) | none | Every user needs a GitHub account, so it fits referees and sub-refs best. |
| **VTT** (Owlbear Rodeo, Foundry) | Room or world members | During a session only | none | Strong: Owlbear broadcasts, Foundry sockets | none | Live channel only. A table already in a VTT can skip WebRTC. |
| **Our handler** | Relays sign-in | Holds mail for players with no account anywhere | Short-lived only | Yes | none | See below. |
| **Manual** | Typed name | Copy and paste a file or link | Download and upload a file | Paste a code | none | Always available, so nobody is locked out. |

GitHub Actions is not a host for the handler. Its jobs can't stay connected or receive calls. A scheduled workflow could poll a Discord channel into the repo, but private repos only have the free minutes for about one poll every 30 minutes, and GitHub's terms limit Actions to the repo's own build and publishing.

### Our handler

A free Cloudflare Worker, owned by Heph, that does only what a browser can't:

- Trade sign-in codes for tokens, which needs a secret (GitHub App, Discord).
- Relay calls to APIs that refuse browser pages.
- Give Discord buttons and slash commands an address to call.
- Hold mail briefly for a player who has no account anywhere.

It keeps no campaign data, which always lives in services the referee picked. If the handler goes away, tables using Google or Discord directly keep working. It is the same Worker WORKFLOWS.md already plans for the sign-in relay.

### Resilience (Heph, 2026-11-08)

Assume any service can vanish overnight (shutdown, API or price change, banned account, new policy). Nothing may be lost, and switching must be cheap.

| If this goes | What stops | What survives | Fix in advance |
| --- | --- | --- | --- |
| **GitHub** | Hosting of the apps and modules (new players can't load them); the campaign archive host | Installed apps run offline from cache; the referee's laptop holds a complete git copy | Custom domain, so moving the site is a DNS change; a Codeberg mirror of the repo |
| **Google** | Mailbox, snapshots, Apps Script bot, calendar | Characters on players' devices; full state on the referee's | Campaign pointer (below), so invites survive an adapter switch |
| **Discord** | Voice, roll log, a Discord mailbox | Everything else | A second voice option; mailbox on another adapter |
| **Our handler** | Features that lean on it | Tables on Google or Discord directly | Keep it stateless and optional |

Three rules make each of these survivable:

1. **Local first.** Every device keeps its own full copy and works offline. (True today.)
2. **The custom domain** is the one address we control. Every printed QR code and app link uses it, never a service's own address.
3. **Campaign pointer.** Invites point at `<our domain>/c/<campaign id>`, a small file naming the adapters the campaign uses right now. If a service dies, the referee switches adapters, the pointer updates, and every player's app follows it without a new invite. The pointer can live in the campaign repo and be mirrored on our domain.

### Alternatives

**To Discord** (chat, webhooks, bots, voice):

| Service | Fit | Notes |
| --- | --- | --- |
| **Matrix** (Element and others) | Best | Open, federated protocol. Its API is plain HTTPS and the spec requires servers to allow browser pages, so the apps can read and post directly with no bot server. Many public servers, or self-host. Voice via Element Call. The natural open twin of the Discord adapter. |
| **Zulip** | Good | Open source, cloud or self-hosted; REST API and incoming webhooks. Threaded chat suits play-by-post. |
| **Mattermost, Rocket.Chat** | Good, self-hosted | Open source Slack-likes with webhooks and APIs. Need a server the referee or a group runs. |
| **Telegram** | Possible | HTTPS bot API; every user needs an account tied to a phone number. |
| **Slack** | Weak | Webhooks and API, but the free plan hides old history and the API refuses browser pages. |
| **IRC** (last resort) | Text only | Open and ancient. Browsers can't speak IRC directly, so it needs a network or server with a WebSocket gateway (for example a self-hosted Ergo server, which also keeps history). No webhooks, no voice. |

For **voice**, Jitsi Meet fits the first principle exactly: a meeting is a URL, with no account. Mumble is the open fallback for groups that run their own.

**To GitHub** (archive host, module and app hosting):

| Service | Fit | Notes |
| --- | --- | --- |
| **Codeberg** (Forgejo) | Best | Non-profit host with Pages. Its API is the same family as self-hosted **Forgejo** and **Gitea**, so one adapter covers all three. |
| **GitLab.com** | Good | Git, API and Pages; a separate adapter. Can also be self-hosted. |
| **SourceHut** | Possible | Minimal git host with static pages; small, paid, very stable. |
| **Plain git over HTTP** | Fallback | A browser git library (isomorphic-git) can push and pull to any git host. Hosts that refuse browser pages need our handler as a relay. |
| **Radicle** | Later | Peer-to-peer git with no host at all. Worth watching. |

For the **app and module site** itself, any static host works: Cloudflare Pages, Netlify, Codeberg Pages, GitLab Pages, even Neocities. With the custom domain, moving is a DNS change.

**Suggested order** if an alternative is ever built: Matrix (the open protocol among the chat options), then the Forgejo API adapter (Codeberg and self-hosted), then plain git as the catch-all. Jitsi can be named in the campaign file today, since it needs no code.

### Build order if agreed

1. Write the job interfaces and the `e9-mail/1` envelope into WORKFLOWS.md, and add the Manual adapter (needed anyway for testing).
2. Run the Discord browser read test.
3. Build **one** real adapter: Discord if the test passes, Google if not.
4. Add the others one at a time. The handler comes in when an adapter needs it.

**Risk:** every adapter multiplies the testing. The MVP ships with one real adapter plus Manual.

### Open questions

1. Does Discord let a browser page read channel messages? (A five-minute test from a real browser.)
2. Which adapter is the default for a new campaign?
3. Can one campaign mix adapters for the same job? Under the first principle the referee picks the services and players only get URLs, so this is now a referee-side question: e.g. Drive for reading plus a Discord webhook for posting.
4. Is a Google Form's no-confirmation post (with receipts in the snapshot) good enough as a fallback, or should the Google adapter always set up an Apps Script web app?
5. Can a browser page read an Apps Script web app's reply, and can the referee's app set the script up in one step? (Test both.)
6. Can an Apps Script web app answer Discord slash commands and buttons in time? (Expect no; test before ruling it out.)
7. Can a browser page hold Discord's gateway connection, and post through the REST API? (Decides whether the live bot posts itself or through the script.)
8. Campaign pointer: in the campaign repo, on our domain, or both?

## P2. Several root modules

**Idea (Heph, 2026-11-08):** `e9-core` is the first **root module**, the rules every other module points at. Other roots will follow: OSE, ACKS, LotFP, Shadowdark, maybe 4E and 5E. So modules need dependency resolution that copes with more than one root.

WORKFLOWS.md "Dependencies" already gives `requires`, `recommends`, `conflicts`, `overrides` and `system`, npm-style version ranges, a lockfile, one version per module, and the referee settling clashes (no automatic solver). This proposal keeps all of that and changes four things.

### 1. Roots say which system they provide

`system` today is a list of names (`e9`, `mm`). Instead, each root module declares the system it provides, and other modules name systems, not particular roots:

```json
{ "id": "e9-core", "kind": "rules", "provides": "e9", "version": "0.1.0" }
{ "id": "ose-core", "kind": "rules", "provides": "ose", "version": "0.1.0" }
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
4. The first non-E9 root (OSE is the likeliest, given Beyond the Pale's OSE stat blocks).

### Open questions

1. ~~Is `e9mm` a system of its own, or an option inside `mm`?~~ **Decided (Heph, 2026-11-08):** E9 for Materia Mundi is an option inside MM. `mm-core` provides one system, `mm`, with an E9 option, and requires `e9-core`.
2. Can a campaign ever mix roots, e.g. OSE monsters converted on the fly into E9? (Proposed: no, convert at build time into a per-system file.)
3. Should the apps themselves (`e9-companion`, `e9-atlas`) be required by version, as WORKFLOWS suggests, from the first release?
