#!/usr/bin/env python3
"""Build obx-core's data files from the Markdown copy of the 2019 B/X SRD text.

usage: python3 -I extract_srd.py <checkout of github.com/oldmanumby/ose.srd> <out dir>

The source text is Open Game Content under the OGL 1.0a (see ../LICENSE.OGL.md). This script only
copies numbers out of the SRD's tables; it writes no rules text. Heph words every rule himself (../text/). Every table keeps
a "ref" naming the SRD section it came from, so a reader can check it by hand.
"""

import json
import re
import sys
from pathlib import Path

SOURCE_COMMIT = '7bd995b'  # the checkout this was built from; the class text dates from 2023-09
ABILITIES = ['str', 'int', 'wis', 'dex', 'con', 'cha']
CLASSES = [  # (id, file)
    ('cleric', '1_Cleric.md'), ('dwarf', '2_Dwarf.md'), ('elf', '3_Elf.md'), ('fighter', '4_Fighter.md'),
    ('halfling', '5_Halfling.md'), ('magic-user', '6_Magic-User.md'), ('thief', '7_Thief.md'),
]
SAVES = [('D', 'death'), ('W', 'wands'), ('P', 'paralysis'), ('B', 'breath'), ('S', 'spells')]


def tables(md: str):
    """Yield (heading, rows) for each Markdown table, rows as lists of cell strings (separator rows dropped)."""
    heading, rows = '', []
    for line in md.splitlines() + ['']:
        if line.startswith('#'):
            heading = line.lstrip('#').strip()
        if line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if not (any(cells) and all(re.fullmatch(r':?-+:?', c) for c in cells if c)):
                rows.append(cells)
        elif rows:
            yield heading, rows
            rows = []


def num(s: str):
    s = s.replace(',', '').replace('−', '-').replace('–', '-').strip()
    if s in ('—', '-', '', 'None'):
        return 0 if s == 'None' else None
    if re.fullmatch(r'[+-]?\d+', s):
        return int(s)
    if re.fullmatch(r'[+-]?\d+%', s):
        return int(s[:-1])
    return s


def score_range(s: str):
    s = s.replace('–', '-')
    a, _, b = s.partition('-')
    return int(a), int(b or a)


def ability_tables(md: str):
    out = {}
    for heading, rows in tables(md):
        m = re.match(r'(Strength|Intelligence|Wisdom|Dexterity|Constitution|Charisma) \((\w+)\)', heading)
        if m:
            ab = m.group(2).lower()
            # Charisma's table has a two-row header ("Retainers" spans two columns).
            head = rows[1] if ab == 'cha' else rows[0]
            body = rows[2:] if ab == 'cha' else rows[1:]
            cols = [re.sub(r'[^a-z]+', '_', h.lower()).strip('_') for h in head[1:]]
            if ab == 'cha':
                cols = ['npc_reactions', 'max_retainers', 'retainer_loyalty']
            out[ab] = {'by': 'range', 'ref': f'Ability Scores > {heading}',
                       'columns': cols,
                       'rows': [dict(zip(['min', 'max'], score_range(r[0])), **{c: num(v) for c, v in zip(cols, r[1:])}) for r in body]}
        elif heading == 'Prime Requisite':
            out['primeXp'] = {'by': 'range', 'ref': 'Ability Scores > Prime Requisite', 'columns': ['xp_modifier'],
                              'rows': [dict(zip(['min', 'max'], score_range(r[0])), xp_modifier=num(r[1])) for r in rows[1:]]}
    return out


def info_table(md: str):
    for _, rows in tables(md):
        return {r[0]: r[1] for r in rows[1:] if len(r) >= 2 and r[0]}
    return {}


def progression(md: str, name: str):
    for heading, rows in tables(md):
        if heading == f'{name} Level Progression':
            head = next(r for r in rows if r[0] == 'Level')
            body = [r for r in rows if re.fullmatch(r'\d+', r[0])]
            out = []
            for r in body:
                row = dict(zip(head, r))
                thac0, _, bonus = row['THAC0'].partition('[')
                entry = {'level': int(row['Level']), 'xp': num(row['XP']), 'hd': row['HD'].rstrip('*'),
                         'conApplies': not row['HD'].endswith('*'),
                         'thac0': int(thac0), 'attackBonus': int(bonus.rstrip(']')),
                         'saves': {sid: int(row[k]) for k, sid in SAVES}}
                slots = [num(row[str(i)]) for i in range(1, 10) if str(i) in row]
                if slots:
                    entry['spellSlots'] = [s or 0 for s in slots]
                out.append(entry)
            return {'ref': f'Classes > {heading}', 'rows': out}
    raise SystemExit(f'no progression table for {name}')


def thief_skills(md: str):
    for heading, rows in tables(md):
        if rows and rows[0][:2] == ['Level', 'CS']:
            head = rows[0]
            return {'ref': 'Classes > Thief > Thief Skills', 'columns': head[1:],
                    'rows': [dict(level=int(r[0]), **{h: num(v) for h, v in zip(head[1:], r[1:])}) for r in rows[1:]]}
    raise SystemExit('no thief skills table')


def turning(md: str):
    for heading, rows in tables(md):
        if heading == 'Turning the Undead' and len(rows) > 2 and rows[1][0] == 'Level':
            # Columns are monster Hit Dice ("2*" = 2 HD with a special ability). Cells: a number to roll
            # on 2d6, "T" turned, "D" destroyed, "—" no effect.
            head = rows[1]
            cell = lambda v: None if v == '—' else num(v)
            return {'ref': 'Classes > Cleric > Turning the Undead', 'columns': head[1:],
                    'rows': [dict(level=r[0], **{h: cell(v) for h, v in zip(head[1:], r[1:])}) for r in rows[2:] if r[0]]}
    raise SystemExit('no turning table')


def equipment(md: str):
    weapons, armor = [], []
    for heading, rows in tables(md):
        if heading == 'Weapons':
            for r in rows[1:]:
                quals = [q.strip() for q in re.split(r',\s*(?![^()]*\))', r[4]) if q.strip()]
                w = {'id': re.sub(r'[^a-z0-9]+', '-', r[0].lower()).strip('-'), 'name': r[0], 'kind': 'weapon',
                     'cost': num(r[1]), 'weight': num(r[2]), 'damage': r[3], 'qualities': quals}
                for q in quals:
                    m = re.match(r'Missile \((.*)\)', q)
                    if m:
                        w['ranges'] = [p.strip() for p in m.group(1).split('/')]
                weapons.append(w)
        elif heading == 'Armor':
            for r in rows[1:]:
                ac, _, asc = r[1].partition('[')
                a = {'id': re.sub(r'[^a-z0-9]+', '-', r[0].lower()).strip('-'), 'name': r[0], 'kind': 'shield' if r[0] == 'Shield' else 'armor',
                     'cost': num(r[2]), 'weight': num(r[3])}
                if a['kind'] == 'shield':
                    a['acBonus'] = 1 if r[1].startswith('+1') else num(r[1])
                else:
                    a['ac'], a['ascendingAc'] = int(ac), int(asc.rstrip(']'))
                armor.append(a)
    return weapons, armor


def main(src: Path, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    read = lambda p: (src / p).read_text(encoding='utf-8')
    abilities = ability_tables(read('1_Characters/3_Ability_Scores.md'))

    classes, prog = [], {}
    for cid, fname in CLASSES:
        md = read(f'2_Classes/{fname}')
        name = md.splitlines()[0].lstrip('# ').strip()
        info = info_table(md)
        primes = [p.lower() for p in re.findall(r'\b(STR|INT|WIS|DEX|CON|CHA)\b', info['Prime requisite'])]
        reqs = {m[0].lower(): int(m[1]) for m in re.findall(r'[Mm]inimum (STR|INT|WIS|DEX|CON|CHA) (\d+)', info['Requirements'])}
        classes.append({'id': cid, 'name': name, 'ref': f'Classes > {name}',
                        'requirements': reqs, 'primes': primes, 'hitDie': info['Hit Dice'],
                        'maxLevel': int(info['Maximum level']),
                        # Armour, weapons, languages and class abilities are rules text: Heph words them (text/).
                        'text': 'pending'})
        prog[cid] = progression(md, name)

    weapons, armor = equipment(read('3_Equipment_&_Services/3_Weapons_and_Armor.md'))

    head = lambda fmt: {'format': fmt, 'id': 'obx', 'source': f'B/X SRD text, Markdown copy github.com/oldmanumby/ose.srd at {SOURCE_COMMIT}; Open Game Content under the OGL 1.0a',
                        'license': 'OGL-1.0a'}
    rules = dict(head('obx-rules/1'), name='OBX', abilities=ABILITIES, saves=[s for _, s in SAVES], classes=classes)
    derive = dict(head('hexmarch-derive/1'), tables={
        **{f'ability.{k}': v for k, v in abilities.items()},
        **{f'progression.{k}': v for k, v in prog.items()},
        'thiefSkills': thief_skills(read('2_Classes/7_Thief.md')),
        'turning': turning(read('2_Classes/1_Cleric.md')),
    })
    # Named values a layout can show (SHEET_LAYOUT.md section 4). Sheet fields: stats.class, stats.level,
    # stats.abilities.<ability> (3-18). lookup() returns the matching row; ".column" reads one cell.
    prog_row = 'lookup(progression[stats.class], stats.level)'
    derive['values'] = {
        'd.mod.str.melee': 'lookup(ability.str, stats.abilities.str).melee',
        'd.mod.str.openDoors': 'lookup(ability.str, stats.abilities.str).open_doors',
        'd.mod.int.languages': 'lookup(ability.int, stats.abilities.int).spoken_languages',
        'd.mod.int.literacy': 'lookup(ability.int, stats.abilities.int).literacy',
        'd.mod.wis.magicSaves': 'lookup(ability.wis, stats.abilities.wis).magic_saves',
        'd.mod.dex.ac': 'lookup(ability.dex, stats.abilities.dex).ac',
        'd.mod.dex.missile': 'lookup(ability.dex, stats.abilities.dex).missile',
        'd.mod.dex.initiative': 'lookup(ability.dex, stats.abilities.dex).initiative',
        'd.mod.con.hp': 'lookup(ability.con, stats.abilities.con).hit_points',
        'd.mod.cha.reactions': 'lookup(ability.cha, stats.abilities.cha).npc_reactions',
        'd.mod.cha.maxRetainers': 'lookup(ability.cha, stats.abilities.cha).max_retainers',
        'd.mod.cha.loyalty': 'lookup(ability.cha, stats.abilities.cha).retainer_loyalty',
        'd.thac0': f'{prog_row}.thac0',
        'd.attackBonus': f'{prog_row}.attackBonus',
        'd.hitDice': f'{prog_row}.hd',
        'd.saves': f'{prog_row}.saves',
        'd.spellSlots': f'{prog_row}.spellSlots',
        'd.xpNext': 'try(lookup(progression[stats.class], stats.level + 1).xp, null)',
        'd.thiefSkills': 'if(stats.class == "thief", lookup(thiefSkills, stats.level), null)',
    }
    # Not modelled yet, because the SRD words them as rules (Heph words them): multi-prime XP bonuses
    # (elf, halfling), class abilities, and the turning table's 2d6 roll.
    equip = dict(head('obx-equipment/1'), ref='Equipment > Weapons and Armor', items=weapons + armor)
    for fname, data in (('rules.json', rules), ('derive.json', derive), ('equipment.json', equip)):
        (out / fname).write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
        print('wrote', out / fname)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
