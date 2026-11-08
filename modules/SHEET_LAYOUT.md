# Sheet layouts (draft)

**Status:** agreed in outline (Heph, 2026-11-08; proposal P5 in [PROPOSALS.md](PROPOSALS.md)). This file is the format; the Companion builds it in its 0.5.X line. Details below are a first draft and change as the first two layouts (E9, then OSE) are written.

## The idea

The Companion owns the **surfaces**. A module owns the **layout** that goes on them.

- **The Companion provides** a fixed set of surfaces, a root stylesheet, and the wiring: dice, rolls, the portrait, print.
- **A module provides** a markup layout for each surface, which places values and roll buttons. It also provides the **derivations** that work those values out from the sheet. Any module may ship a layout, but in practice it is the root (`e9-core`, `mm-core`, `ose-core`).

A campaign has one root (WORKFLOWS.md, "Campaign stack"), so a character has one layout: the root's own, or one a later module in the stack overrides.

## 1. Surfaces

| Surface id | Size | Today |
| --- | --- | --- |
| `card-front` | index card, 5 × 3 in, landscape | front of `Postcard.svelte` |
| `card-back` | index card, 5 × 3 in, landscape | back of `Postcard.svelte` |
| `page-1` … `page-N` | US letter, 8.5 × 11 in, portrait | `PageSheet.svelte` |

Sizes are fixed, so a layout can't grow a card. Text that doesn't fit is clipped on print and scrolls on screen, and the Companion's layout check warns about it. On a phone the two card faces are the main view: they sit side by side to swipe, and you tap a value to roll it.

## 2. Files

A module that ships a layout adds these files beside its `module.json`:

```
layout/
  card-front.html
  card-back.html
  page-1.html          (as many pages as it needs)
  layout.css           (optional, scoped; see section 5)
derive.json            how named values are worked out (section 4)
```

and names them in its manifest:

```json
{ "layout": "layout/", "derive": "derive.json" }
```

## 3. Markup

A layout file is a fragment of plain HTML using a **whitelist** of elements, plus a few Companion elements. The Companion parses it on load and refuses anything off the list: no scripts, no event attributes, no links out, no images except the portrait slot. Modules come from other authors, so a layout can only arrange; it can't run code.

**Plain elements allowed:** `div span p h1 h2 h3 h4 strong em small br hr ul ol li table thead tbody tr th td`. **Attributes allowed:** `class`, plus `data-print` (below).

**Companion elements:**

| Element | What it does |
| --- | --- |
| `<e9-value key="…">` | Shows a named value (section 4), e.g. `key="stats.name"` or `key="d.ac"`. Optional `format="signed"` shows +1 / −1. |
| `<e9-roll check="…" key="…">label</e9-roll>` | A value you tap to roll. `check` is one of the Companion's check kinds: `talent`, `save`, `attack`, `damage`, `ability`, or `dice` (a plain expression in `key`). The frame wires it to the dice tray and the roll log. On paper it prints as plain text. |
| `<e9-each list="…" as="w">…</e9-each>` | Repeats its contents for each entry of a list, such as weapons, items, prepared magic or followers. Inside, `w.name` and the like are named values. Optional `max="6"` caps the count on a fixed surface. |
| `<e9-if key="…">…</e9-if>` | Shows its contents only when the value is set and not zero, false or empty (for example a class with spells). |
| `<e9-portrait>` | The one portrait slot. |
| `<e9-page-ref ref="…">` | A rules page reference, linked to the wiki like `PageRef.svelte`. |

**`data-print`** on any element: `only` means it appears only on paper or PDF, `never` means it appears only on screen.

**Example** (a structural sketch, not rules text):

```html
<div class="row">
  <e9-portrait></e9-portrait>
  <div>
    <h2><e9-value key="stats.name"></e9-value></h2>
    <small><e9-value key="d.classLine"></e9-value></small>
  </div>
</div>
<table class="saves">
  <e9-each list="d.saves" as="s">
    <tr><th><e9-value key="s.name"></e9-value></th>
        <td><e9-roll check="save" key="s.id"><e9-value key="s.target"></e9-value></e9-roll></td></tr>
  </e9-each>
</table>
<p data-print="never" class="hint">Tap a value to roll it.</p>
```

## 4. Named values and derivations

A layout can only show values that exist. They come from two places.

1. **The sheet**, by part (CHARACTER_FORMAT.md, version 4): `stats.*`, `gear.*`, `knowledge.*`, `flavor.*`. These are the recorded facts: scores, class, level, XP, items.
2. **The root's derivations**, under `d.*`, worked out from the sheet each time it loads. The sheet stays a record with no derived values (the Companion's sheet/character rule).

`derive.json` is data, not code. It holds **tables** and **formulas** in a small expression language the Companion evaluates:

```json
{
  "format": "e9-derive/1",
  "tables": {
    "abilityMod": { "by": "range", "rows": [ { "min": 3, "max": 3, "value": "…" } ] },
    "saves":      { "by": ["class", "level"], "rows": [ "…" ] }
  },
  "values": {
    "d.strMod":   "lookup(abilityMod, stats.abilities.str)",
    "d.saves":    "lookup(saves, stats.class, stats.level)",
    "d.xpNext":   "lookup(xp, stats.class, stats.level + 1)"
  }
}
```

- **Expressions:** numbers, strings, `null`, named values, `+ - * /`, comparisons, `and or not`, `if(c, a, b)`, `min max floor ceil`, `sum(list, expr)`, `count(list)`, `lookup(table, …keys)`, and `try(expr, fallback)`, which gives the fallback where a lookup finds no row (the last level, say).
- `lookup` returns the matching row; `.column` reads one cell of it (`lookup(ability.str, stats.abilities.str).melee`). `name[expr]` picks the table `name.<value>`, so `progression[stats.class]` is `progression.fighter` for a fighter.
- No loops beyond `sum`/`count`, and no recursion. A value may use other `d.*` values, but a cycle is an error reported on load.
- **Range tables** (`"by": "range"`) find the row whose `min`–`max` holds the key. **Keyed tables** match exact keys. A missing row is an error shown on the sheet, never a silent zero.
- Every table and value comes from the root's licensed source and keeps its page or section reference (`"ref"`), as `rules.json` does today. A layout never introduces numbers of its own.

E9 and MM keep their current engine (`rules.ts`) at first, and the frame exposes its results as `d.*`, so porting their card and page is a pure layout job. OSE is the first root that works only through `derive.json`.

## 5. Styling

- The Companion's **root CSS** sets the fonts, sizes, colours (light and dark), and print rules, and gives layouts a small set of classes: `row col grid-2 grid-3 box label value hint small center right`.
- A module's optional `layout.css` is scoped to its own surfaces. It may use only class selectors and plain properties: no `@import`, no `url()`, no positioning outside the surface, no fonts beyond the root's.

## 6. Checks on load

When the Companion or Scribe opens a module with a layout, it checks:

- that every element and attribute is on the whitelist
- that every `key`, `list` and `check` resolves for that root
- that `derive.json` has no cycles or missing rows
- that the content fits each fixed surface at default size

Problems show in the module's update/errata report as **needs-decision**, never as a blank sheet.

## Build order

1. **Companion 0.5.X:** the surfaces, root CSS, the markup parser, and `d.*` exposed from today's engine. Then port today's E9 card and page into `e9-core`'s `layout/`, with no visible change.
2. **`derive.json` evaluator**, tested against E9's own numbers.
3. **`ose-core` 0.1.0** ships tables, values and a layout, so OSE gets a character sheet with no new app code.

## Open questions

1. Should a non-root module (a class pack, say) be able to add a block to the root's layout, or only replace a whole surface?
2. Letter pages flow and split automatically, or does the layout place page breaks by hand? (Suggested: by hand, since the pages are fixed.)
3. Should A4 be offered alongside letter?
