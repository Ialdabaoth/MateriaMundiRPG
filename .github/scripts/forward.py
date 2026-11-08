#!/usr/bin/env python3
"""Forward the old app addresses on this site to the apps repo's site (links.json "apps.url").

usage: python3 -I .github/scripts/forward.py <site dir>

The E9 Companion used to live at this site's root and the E9 Atlas at /atlas/; both moved to the apps repo
(Heph 2026-11-08). This writes:
  index.html        -> <apps>       (query and #hash kept)
  atlas/index.html  -> <apps>atlas/ (query and #hash kept; ?site= points the Atlas back at this site)
  sw.js             a service worker that removes the old Companion's offline copy, so installed apps
                    reload and land on the forward. Characters stay: they are stored per site origin, and
                    both sites share ialdabaoth.github.io.
"""
import json, os, sys

site = os.path.abspath(sys.argv[1])
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
apps = json.load(open(os.path.join(REPO, 'links.json')))['apps']['url']

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} has moved</title>
<script>
(function () {{
  var to = new URL({target}), here = new URL(location.href);
  here.searchParams.forEach(function (v, k) {{ to.searchParams.set(k, v); }});
  {extra}
  to.hash = location.hash;
  location.replace(to.href);
}})();
</script>
</head><body style="font-family:Georgia,serif;max-width:32rem;margin:3rem auto;padding:0 1rem">
<p>{title} has moved to <a href={target}>{target_text}</a>.</p>
</body></html>
"""

def page(path, title, target, extra=''):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(PAGE.format(title=title, target=json.dumps(target), target_text=target, extra=extra))

page(os.path.join(site, 'index.html'), 'The E9 Companion', apps)
# the Atlas loads this site's modules: say so unless the link already names a site
page(os.path.join(site, 'atlas', 'index.html'), 'The E9 Atlas', apps + 'atlas/',
     "if (!to.searchParams.has('site')) to.searchParams.set('site', new URL('../', location.href).href);")
open(os.path.join(site, 'sw.js'), 'w').write("""// The E9 Companion moved (see index.html). Remove its old offline copy and reload open pages onto the forward.
self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (e) {
  e.waitUntil((async function () {
    for (const k of await caches.keys()) await caches.delete(k);
    await self.registration.unregister();
    for (const c of await self.clients.matchAll({ type: 'window' })) c.navigate(c.url);
  })());
});
""")
print(f'forwards -> {apps}')
