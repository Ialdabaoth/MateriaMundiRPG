# E9 Proposals

Ideas under discussion that are not yet agreed. When Heph agrees to one, it moves into the spec it belongs to (usually [WORKFLOWS.md](WORKFLOWS.md)), and this file keeps a one-line pointer to it.

| Proposal | Status | Would change |
| --- | --- | --- |
| [P1. Open service adapters](#p1-open-service-adapters) | Proposed 2026-11-08 (Heph thinking out loud) | WORKFLOWS.md "Mailbox and archive", "Live channel", "Accounts" |

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
| **Google** | Gmail sign-in (referee) | Drive folder inbox (players post through a Google Form) | Drive folder | Drive files (slow) | Calendar invites and RSVPs | No server of ours. Needs a Google Cloud OAuth client (`drive.file`). The current default. |
| **Discord** | Discord sign-in | Channel messages (players post through a webhook) | Channel attachments | Channel messages | Scheduled events ("Interested") | Discord keeps the messages, so the channel itself is the mailbox. The referee's open app acts as the bot, with the token on that device only. **To test:** whether Discord's API lets a browser page read channel messages. If not, reads go through our handler. |
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
4. Is a Google Form's no-confirmation post good enough for requests, or should posts always go to something that answers (webhook, handler)?
