# Beyond the Pale: Leinster, 1422 — changelog

This module's version is its own. It does not follow the E9 Atlas (`modules/tools/ATLAS_VERSION`) or the E9 Companion; a change to the tools or apps alone never bumps it. Bump it only for changes to this module's content (text, sites, creatures, encounters, maps), using the rules in [WORKFLOWS.md](../WORKFLOWS.md#versioning).

## 0.4.6 (2026-11-07)

- B2 matches Heph's latest draft: scene and creature descriptions in `keep.json`, `lairs.json` and `encounters.json` use his Google Doc of 10 October 2026 word for word. The only edits are agreed canon and rules words (the Boyne at Trim, barrow-cat, feysilver, save vs. Doom and Fear, Alertness checks), listed before and after in `adventure/b2-text-changes.md`.
- Heph's answers to the open questions: the keep was built in 3257, the shrine is to Crom-Cruach (no Orcus), the rumour table is a d6, gate guards are warriors, Brother James is fifth level, the Bloodhand chieftain is at ⑯, and the Dame is MacGearailt.
- Goblin clans take Irish names (Heph): Blacktooth is now Dubhfhiacail, Bloodhand is Lámh Fhuilteach, and Skitterglint is Drithleoga, in text, creature names and the cave map labels. Ids stay as they were (`blacktooth-clan` and so on).
- New scenes from the Doc: arriving in the Pale, keeping the adventure alive, Beyond the Pale, the caves introduction, inter-clan relations, emptying the caves, caves G to K room by room, and the abandoned druid's grove at Tlachtga. They have no map pointers yet.

## 0.4.5 (2026-11-07)

B3, the Palace of Silver and Crimson, brought in from Heph's February 2026 draft, with stat blocks brought up to the current rules with him, in the new `palace.json` (an `encounters` block) and both bestiaries.
- Cast (26 creature records): the lower palace (bloodroses, the redcaps and Chef, Mairead, bloodstirges, the oreiad caryatids), the southern wings (Rowena, a human bard with an elf grandmother, and her elf bodyguards; the kobolds and their bone mother; Travis; rustgrubs), the upper palace (the chaplain's haunt, Boar-champion bugbears and their outcast, the Cleasaí, Aine, Cathbad, Dame Alice Kyteler) and Cill Chainnigh (Lady Petronella d'Meath, an elven druidess, her boar pucca, Tinker Gabhan and Goodwitch Fiona), plus Lig na Péiste, the Silver Knight.
- Rules: warlocks are priests sworn to Crom Cruach (Kyteler takes the Nature domain, Cathbad Death); Lady d'Meath is an elf druid; true fey keep a glamour pool; book monsters (bloodstirge, oreiad, rustgrub) use the Compendium entries.
- Canon fixes: the "Decapus" is now An Deichlámhach, called the Cleasaí; Aine, Mairead and Maddy are Faoladh (wolf pucca); the kobolds' silver dragon is a little cult of Lig na Péiste; the palace is at Kells Priory on the King's River, built in 3278 (Materia Mundi years run AD + 2085, so 1422 is 3507).
- Seven factions (Kyteler's court, d'Meath's court, Cathbad and his bugbears, the palace redcaps, the silver-dragon kobolds, the Faoladh sisters, Lig na Péiste) and 84 scenes: every palace room, Cill Chainnigh, the wilds and the background chapters.
- Heph writes all the prose. Scenes and creature descriptions are his February 2026 text word for word, apart from the agreed edits listed in project-files adventure/b3-text-changes.md. The palace scenes point at encounter maps once his palace map pages are traced.

## 0.4.4 (2026-11-07)

Roads of 1422 (`atlas.roads`, Atlas 0.4.18): 28 roads, about 1,925 miles, routed over the terrain by the Atlas, with 121 river crossings.
- Roman class: the five slighe out of Tara (Slí Midluachra, Slí Asail, Slí Mhór, Slí Dála, Slí Chualann). They have bridges.
- Local: 20 town roads, among them the Barrow, Nore and Suir roads, the south coast road, the Cork and Kerry roads, the Thomond and Connacht roads, and the Ulster and Lecale roads. They have fords.
- Trails: Tóchar Phádraig to Croagh Patrick, St Kevin's Way to Glendalough, and the Lough Derg path, which ends at the shore because pilgrims take the boat to Station Island.
- The courses are general history (Claude); the slighe follow their traditional lines only roughly.

## 0.4.3 (2026-11-07)

NPC and monster pass with Heph (rules: the early-playtest "N faith / glamour / favor" and "Feats: X Frenzy, Evasion, Slay Quarry" lines are gone).
- Every creature now has an `origin` and a `classId`, and casters prepare from their class's slot table (prayer strips, spells, talismans, dweomers).
- New `bestiary/e9mm.json` for E9 for Materia Mundi. People use the race-as-class builds (dwarf fighter+dweomersmith, elf fighter+expert+druid, gnome expert+druid, human single class). Monster tribes use the app's class renames (champion becomes fighter; hunter and bard become expert).
- Keep: the bank is a dwarf family; the barkeep is human and his wife a gnome bard; Sir Edward is warrior 6 / war priest 6; Brother "James" is a warlock whose prayer strips are prayers to the Baalim, so a true priest who copies one gets nothing; Dame MacGeralt is an elf druid with her two wisps.
- Lairs: champions get Improved Critical Hit and, from level 2, Battle-Trance with an initiation (Serpent for ambushers such as ettercaps and the Skitterglint redcaps, Boar for the Blacktooth and Bloodhand, Bear for the hobgoblins, the bugbear and the ogre); hunters get Hunter's Expertise and Sneak Attack. The Faoladh are wolf pucca. The hermit's leopard is now a barrow-cat (`hermits-barrow-cat`).
- Fixed copy-paste errors: Bank Guard talents; HP for Brother Sean, Brother John and Sister Penelope; Sister Penelope gets a quarterstaff.

## 0.4.2 (2026-11-06)

Place ranks for the E9 Atlas (`site_ranks`, Atlas 0.4.16), so that zooming out shows the island's great places instead of a pile of castle icons.
- Rank 1, shown from the Region view (16 places): the great lordships' seats (Trim, Kilkenny, Maynooth, Carrickfergus, Dungannon, Askeaton, Ballintober, Daingean) and the island's great old places (Tara, Rathcroghan, Emain Macha, Cashel, Brú na Bóinne, Clonmacnoise, Armagh, Croagh Patrick).
- Rank 2, shown from the March view (58 places): the other book and hand-picked castles, the best-known Sites and Monuments Record castles, and the notable mythic sites, such as Uisneach, Grianán Ailigh, Skellig Michael, Lough Gur and Lough Derg.
- Everything else uses the Atlas defaults: towns 1, abbeys 2, other sites 3.

## 0.4.1 (2026-11-06)

Gazetteer cleanup for the 131 castles taken from the Sites and Monuments Record.
- Irish names for 95 of them, with the English name kept for the Language toggle. The other 36 are small townland names whose Irish form is uncertain; they stay in English.
- Each castle has a 1422 note in place of the record's class: who holds it (Butler, Desmond, Burke, O'Brien, O'Connor, O'Neill and so on) and what it is like.
- Seven castles that stood empty or wrecked by 1422 are now `ruin`: Dún Másc (Dunamase), Baile Mhuáin (Ballymoon), Bun Raite (Bunratty), Caisleán Chaoimhín (Castle Kevin), Mainnín (Mannan), Cuinche (Quin) and Rinn Dúin (Rindown).
- To check before print: the Irish names come from memory (Claude) and need checking against logainm.ie; holders are general history, not a survey of each site.

## 0.4.0 (2026-11-06)

All of Ireland in the E9 Atlas (Heph: "available for exploration", not yet tied to books). The print maps stay on the four book counties.
- `atlas.land: "island"`: the Atlas covers the whole island, 104 Marches. 89 new real-data terrain masters (ESA WorldCover + SRTM, 1420s rules, tools/realmap.py), with rivers from the island's own drainage.
- New region `eire-1422`: 328 places that stood in 1422 (45 towns, 153 castles, 68 abbeys and friaries, 31 hills, 18 ruins, 10 tombs, 3 caves). Religious houses inside a town are in the town's note.
- Sources: towns, abbeys and old places from general history (Claude), town positions checked against GeoNames (all within about 2 km); most castles (Anglo-Norman stone castles and hall-houses) from Canonical Castles (bussetech/canonical-castles, CC BY 4.0), whose positions come from the Archaeological Survey of Ireland's Sites and Monuments Record (CC BY 4.0). Tower houses are left out: most are later than 1422.
- To check before print: Irish names for the minor castles (still English) and a few less common Irish forms (for example Seanchaisleán for Olderfleet), and which castles were ruined or held by Gaelic lords by 1422.
- `modules/geo/admin1.geojson` gains Northern Ireland's districts (Natural Earth, public domain) so the island's outline is complete.

## 0.3.0 (2026-11-06)

Baseline set by Heph after the E9 Atlas split into its own sub-project. Earlier builds printed 0.1.0 to 0.3.6 while the module and the map tools shared one number; none was released, so the count restarts here. Contents: the Leinster quartet (An Mhí B2, Cill Chainnigh B3, Ceatharlach B5, Cill Dara B4), real-data E9 Atlas terrain masters, sites, creatures and the first encounter maps.
