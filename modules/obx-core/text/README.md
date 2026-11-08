# OBX rules text: Heph's wording

obx-core copies **no rules text** from any source. Its numbers and tables (`rules.json`, `derive.json`, `equipment.json`) come from the B/X SRD's tables, which are Open Game Content. Every rule that needs words is written by Heph, one file per entry below, and is Open Game Content too (see `../LICENSE.OGL.md`).

How it works: for each entry Heph says how the rule should read, and Claude records his words verbatim in `text/<id>.md`, with no paraphrase. Reference for what each rule does: the SRD section named in brackets (the Markdown copy at github.com/oldmanumby/ose.srd, and Necrotic Gnome's online rules reference, read only, never copied).

Status: `[ ]` waiting for Heph, `[x]` written.

## 0.1.0: what a character sheet needs

### Characters
- [ ] `ability-scores`: what each score modifies (Ability Scores)
- [ ] `prime-requisite`: XP modifier from prime requisites (Ability Scores > Prime Requisite)
- [ ] `creating-a-character`: the steps, in order (Creating a Character)
- [ ] `hit-points`: rolling hit points at 1st level and on levelling (Game Statistics; Creating a Character > 7)
- [ ] `armour-class`: AC, unarmoured AC, ascending AC option (Game Statistics; Creating a Character > 11)
- [ ] `attack-roll`: THAC0 and attack bonus (Game Statistics > THAC0)
- [ ] `saving-throws`: the five categories and how to roll (Game Statistics > Saving Throw Values)
- [ ] `alignment`: (Alignment)
- [ ] `languages`: (Languages)
- [ ] `advancement`: XP, level up, the per-session cap (Advancement)

### Classes (one file each: who may take it, armour, weapons, languages, and each ability)
- [ ] `class-cleric`: combat, divine magic, turning the undead and its table results, after 9th level
- [ ] `class-dwarf`: combat, detect construction tricks, detect room traps, infravision, listening at doors, after 9th level
- [ ] `class-elf`: arcane magic, combat, detect secret doors, immunity to ghoul paralysis, infravision, listening at doors, after 9th level; its two-prime XP bonus
- [ ] `class-fighter`: combat, stronghold, after 9th level
- [ ] `class-halfling`: combat, defensive bonus, hiding, initiative bonus (optional), listening at doors, missile attack bonus, stronghold; its two-prime XP bonus
- [ ] `class-magic-user`: arcane magic, combat, after 11th level
- [ ] `class-thief`: back-stab, combat, read languages, scroll use, thief skills and rolling them, after 9th level

### Equipment
- [ ] `weapon-qualities`: Blunt, Brace, Charge, Melee, Missile, Reload, Slow, Splash weapon, Two-handed (Weapons and Armor > Weapon Qualities)
- [ ] `encumbrance`: both optional systems (Weapons and Armor > Encumbrance)

## Later
Spells, combat, adventuring, monsters and treasure, in the same way, once the character sheet works.
