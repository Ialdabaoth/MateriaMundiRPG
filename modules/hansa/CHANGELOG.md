# Hansa: changelog

The module's own version (WORKFLOWS.md). Tool and app changes never bump it.

## 0.2.1 (2026-11-07)

- Credits: `credits` in module.json lists the data sources the map uses (ESA WorldCover, SRTM, Natural Earth). The Atlas and the module viewer show them.

## 0.2.0 (2026-11-07)

- First city Encounter map: Lübeck's Markt, Rathaus and St Mary's (5-ft squares, roughly historic c. 1420, simplified), opened from the Lübeck place in the Atlas. Drawn from `encounter-maps/lubeck-markt/plan.json` with tools/encounter_draw.py.

## 0.1.0 (2026-11-06)

- First real-data map: the coast from Lübeck to the Vistula Lagoon, with Bornholm offshore, pushed back to 1422 (REALMAP.md). Centroid Bornholm, fixed extent Holstein to Livonia plus western Poland.
- Period lands (Holstein, Mecklenburg, Pommern, Pomerellen, Preussen, Kulmerland ...) cut from Natural Earth with tools/admin_lands.py.
- Gazetteer of about 100 towns, castles and abbeys of 1422, positions approximate.
