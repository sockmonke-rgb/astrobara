#!/usr/bin/env python3
"""Astrobara Tier 0 pre-flight — P1 to P12 of the test plan.

    python3 preflight.py <build.html> [SEEDS.txt]

Exits non-zero if any check fails. Every check prints the evidence, not just a
verdict, so a pass is auditable and a failure is actionable.
"""
import sys, re, json, subprocess, pathlib, tempfile

FAILS = []

def check(num, name, ok, detail=''):
    print(('  PASS' if ok else '  FAIL') + f'  {num:<4} {name}')
    if detail:
        for line in str(detail).splitlines():
            print(f'            {line}')
    if not ok:
        FAILS.append(f'{num} {name}')

def main():
    path = pathlib.Path(sys.argv[1])
    seeds_path = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else None
    h = path.read_text()
    print(f'\nASTROBARA PRE-FLIGHT — {path.name}\n')

    script = '\n'.join(re.findall(r'<script[^>]*>(.*?)</script>', h, re.S))
    style  = h.split('<style>')[1].split('</style>')[0] if '<style>' in h else ''

    # P1 — the script parses
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
        f.write(script); tmp = f.name
    r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
    check('P1', 'script parses', r.returncode == 0, r.stderr.strip()[:400])

    # P2 — one source for the version
    hdr  = re.search(r'ASTROBARA (V[\d.]+(?:-[A-Z0-9]+)?)', h)
    meta = re.search(r'content="Astrobara (V[\d.]+(?:-[A-Z0-9]+)?)', h)
    bld  = re.search(r"const BUILD = '(V[\d.]+(?:-[A-Z0-9]+)?)'", h)
    found = {'header': hdr.group(1) if hdr else None,
             'meta':   meta.group(1) if meta else None,
             'BUILD':  bld.group(1) if bld else None}
    check('P2', 'version agrees in three places',
          len(set(found.values())) == 1 and None not in found.values(), found)

    # P3 — no duplicate element IDs
    ids = re.findall(r'\sid="([^"]+)"', h)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    check('P3', 'no duplicate element ids', not dupes,
          f'{len(ids)} ids, all unique' if not dupes else f'duplicated: {dupes}')

    # P4 — every getElementById target exists
    wanted = set(re.findall(r"getElementById\('([^']+)'\)", script))
    wanted |= set(re.findall(r"querySelector\('#([A-Za-z0-9_-]+)'\)", script))
    missing = sorted(wanted - set(ids))
    check('P4', 'every getElementById target exists', not missing,
          f'{len(wanted)} targets, all present' if not missing else f'missing: {missing}')

    # P5 — tags balance inside #app
    body = h.split('<div id="app">')[1].split('<div class="overlay" id="splash">')[0]
    depth = 0; over = False
    for m in re.finditer(r'<div\b|</div>', body):
        depth += 1 if m.group(0).startswith('<div') else -1
        if depth < 0: over = True
    check('P5', 'divs balance inside #app', depth == 0 and not over,
          f'balance {depth}, never over-closed' if not over else 'closed more than opened')

    # P6 — storage keys
    keys = sorted(set(re.findall(r"'(astrobara\.[a-z]+)'", script)))
    expect = ['astrobara.achv', 'astrobara.board', 'astrobara.run']
    check('P6', 'only the three known storage keys', keys == expect, keys)

    # P7 — no network
    net = []
    for pat, label in [(r'\bfetch\s*\(', 'fetch('), (r'XMLHttpRequest', 'XMLHttpRequest'),
                       (r'src\s*=\s*["\']https?:', 'remote src'),
                       (r'@import', '@import'),
                       (r'href\s*=\s*["\']https?://[^"\']*\.(?:css|woff)', 'remote stylesheet/font')]:
        if re.search(pat, h): net.append(label)
    check('P7', 'no network of any kind', not net, net or 'clean')

    # P8 — every font-size scales
    bare = re.findall(r'font-size:\s*[\d.]+px(?!\s*\*)', style)
    scaled = re.findall(r'font-size:calc\([\d.]+px \* var\(--tsb?\)\)', style)
    check('P8', 'every css font-size scales', not bare,
          f'{len(scaled)} scaled, {len(bare)} bare' + (f': {bare[:4]}' if bare else ''))

    # P9 — every touch-action justified
    bad = []
    for m in re.finditer(r'([^{}]+)\{([^{}]*touch-action:\s*([^;}]+)[^{}]*)\}', style):
        sel, val = m.group(1).strip().split('\n')[-1].strip(), m.group(3).strip()
        if val in ('none', 'auto'):
            continue                      # a drag grip, or the default
        if 'pinch-zoom' not in val:
            bad.append(f'{sel} -> {val}')
    check('P9', 'no touch-action silently refuses the system pinch', not bad,
          bad or 'every pan list also names pinch-zoom')

    # P10 — achievement table integrity
    if 'const ACHV = [' in script:
        achv = script.split('const ACHV = [')[1].split('];')[0]
        aids  = re.findall(r"\{id:'([a-z_]+)'", achv)
        names = re.findall(r"n:'([^']+)'", achv)
        awarded = set(re.findall(r"award\('([a-z_]+)'\)", script))
        ok = (len(aids) == len(set(aids)) and len(names) == len(set(names))
              and set(aids) == awarded)
        check('P10', 'achievement table integrity', ok,
              f'{len(aids)} ids, unique; names unique; awarded set matches'
              if ok else f'ids={aids}\nawarded={sorted(awarded)}')
    else:
        check('P10', 'achievement table integrity', False, 'ACHV table not found')

    # P11 — seed round-trip
    if seeds_path and seeds_path.exists():
        codes = re.findall(r'^  ([A-Z]+-[A-Z]+-\d+)$', seeds_path.read_text(), re.M)
        stars = re.findall(r'^(\d) STAR', seeds_path.read_text(), re.M)
        blocks = re.split(r'^\d STAR.*$', seeds_path.read_text(), flags=re.M)[1:]
        claimed = {}
        for st, blk in zip(stars, blocks):
            for c in re.findall(r'^  ([A-Z]+-[A-Z]+-\d+)$', blk, re.M):
                claimed[c] = int(st)
        harness = pathlib.Path(__file__).with_name('seedcheck.js')
        if harness.exists():
            r = subprocess.run(['node', str(harness), str(path), json.dumps(claimed)],
                               capture_output=True, text=True)
            check('P11', 'every published seed regenerates its site',
                  r.returncode == 0, r.stdout.strip() or r.stderr.strip()[:400])
        else:
            check('P11', 'every published seed regenerates its site', False,
                  'seedcheck.js not found beside preflight.py')
    else:
        print('  SKIP  P11  seed round-trip (no SEEDS.txt given)')

    # P12 — css braces balance
    check('P12', 'css braces balance', style.count('{') == style.count('}'),
          f"{style.count('{')} open, {style.count('}')} close")

    print()
    if FAILS:
        print(f'FAILED {len(FAILS)}: ' + '; '.join(FAILS))
        return 1
    print('Tier 0 clean.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
