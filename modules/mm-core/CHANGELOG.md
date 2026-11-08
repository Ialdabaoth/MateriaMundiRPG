# Materia Mundi core module (mm-core): changelog

The Materia Mundi rules as data, from the Materia Mundi Compendium (canon source). The version lives in `module.json`. Every merged PR bumps the patch; each sprint bumps the minor.

Options are parts of the module a campaign can switch on. `e9` (Materia Mundi for E9, ruleset id `e9mm`) plays the setting on E9 rules, with MM origins as race-as-class, and needs `e9-core`.

## 0.1.0

- Materia Mundi becomes its own module. `rules.json` (origins, classes, origin roll tables, mechanics; was the Companion's `src/rules/options/mm-options.json`), `equipment.json` (Compendium arms, armour, gear and magic lists; was `src/equipment/mm-equipment.json`) and `bestiary.json` (was `src/bestiary/mm-bestiary.json`) move here unchanged.
- MM-for-E9 becomes the module's `e9` option: `e9/rules.json` (was `src/rules/options/e9mm-options.json`) and `e9/equipment.json` (was `src/equipment/e9mm-equipment.json`), unchanged.
- The Companion still bundles these files at build time; ruleset ids (`mm`, `e9mm`) and every equipment and creature id are unchanged, so saved characters are unaffected.
