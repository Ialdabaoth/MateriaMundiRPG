# Licences

All the code in this repository, for the whole E9 app suite, is dedicated to the public domain by Heph under **CC0 1.0 Universal** (https://creativecommons.org/publicdomain/zero/1.0/). To the extent possible under law, he has waived all copyright and related rights to it. Use it, change it, fork it, self-host it and ship it, with no permission or credit needed.

| Part | Where | Licence |
| --- | --- | --- |
| E9 Companion app code | `companion-app/` (see [its LICENSE.md](companion-app/LICENSE.md) for the data files it carries) | CC0 1.0 |
| E9 Atlas app and map tools | `modules/tools/` ([LICENSE.md](modules/tools/LICENSE.md)) | CC0 1.0 |
| E9 Bridge for Foundry VTT | `vtt/foundry/e9-bridge/` | CC0 1.0 |
| Build workflow and repo scripts | `.github/`, `mm.json`, `links.json` | CC0 1.0 |
| Format specs | `modules/*.md`, `companion-app/*_FORMAT.md` | CC0 1.0, so anyone can implement them |

**This covers code and specs only.** Other material keeps its own licence and is not part of the CC0 dedication:

- **The Materia Mundi books and their files** (the PDFs and Affinity `.af` files at the top of the repo, and `Art/`): © Heph, all rights reserved unless the book itself says otherwise.
- **Rules data in the Companion** (rulesets, equipment, magic and bestiary JSON): see [companion-app/LICENSE.md](companion-app/LICENSE.md). Parts come from the E9 System Reference Handbook (CC BY-SA 4.0) and the System Reference Document 5.2 (CC BY 4.0), which require credit and, for CC BY-SA, share-alike.
- **Hex tile art** in `modules/assets/tiles`: C. Martins, CC BY-SA 4.0 (edited icons: "Art by C. Martins, edited by Heph", same licence).
- **Each module's text and maps**: the licence in its own `module.json`, plus the data sources it lists under `credits` (for example the Ireland castle dataset, CC BY 4.0).
- **Third-party libraries** the apps install (for example three.js): their own licences, as listed in `companion-app/package-lock.json`.
