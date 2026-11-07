#!/usr/bin/env python3
"""SEO audit v2 — see SPEC.md. Every rule here exists because v1 produced a
false positive. Guiding principle: if a claim cannot be proven from file
contents, it is not emitted.

Usage: audit.py <repo_dir> <out.json> [--run-generator]
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(sys.argv[1].rstrip('/'))
OUT = sys.argv[2]
RUN_GEN = '--run-generator' in sys.argv
NAME = os.path.basename(ROOT)

F = []
INFO = {'repo': NAME}
SKIP_DIRS = {'.git', 'node_modules', '.next', '.astro', '.vercel', '__pycache__',
             'dist/.cache', '.cache'}

# hreflang region subtags are uppercase (pt-BR) or numeric (es-419). v1's
# [a-z-] class silently matched neither.
HREFLANG_RE = re.compile(r'<link\s+rel="alternate"\s+hreflang="([A-Za-z0-9-]+)"\s+href="([^"]+)"', re.I)
CANON_RE = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"', re.I)
TITLE_RE = re.compile(r'<title[^>]*>([^<]*)', re.I)
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"', re.I)
# Only a real robots meta counts. v1 grepped the word "noindex" and matched
# body copy that merely explained the site's noindex policy.
ROBOTS_META_RE = re.compile(r'<meta\s+name="robots"\s+content="([^"]*)"', re.I)

IGNORED_HOSTS = {
    'sitemaps.org', 'www.sitemaps.org', 'schema.org', 'www.w3.org', 'w3.org',
    'googletagmanager.com', 'google-analytics.com', 'fonts.googleapis.com',
    'fonts.gstatic.com', 'example.com', 'localhost', 'roblox.com',
    'www.roblox.com', 'github.com', 'vercel.app',
}


def add(sev, code, msg, detail=None):
    F.append({'sev': sev, 'code': code, 'msg': msg, 'detail': detail or []})


def rd(p, limit=600000):
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as fh:
            return fh.read(limit)
    except Exception:
        return ''


def walk(base, exts=None):
    for dp, dns, fns in os.walk(base):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            if exts is None or os.path.splitext(fn)[1].lower() in exts:
                yield os.path.join(dp, fn)


def host_of(u):
    """Apex host, or None when the value is not a usable domain."""
    if not u:
        return None
    if any(t in u for t in ('${', '{{', '[', '`', '%s', '{0}')):
        return None            # unresolved template expression
    m = re.search(r'https?://([^/\s"\']+)', u)
    h = (m.group(1) if m else u).strip().lower().split(':')[0].lstrip('.')
    if h.startswith('www.'):
        h = h[4:]
    if h in IGNORED_HOSTS or not re.match(r'^[a-z0-9][a-z0-9.-]*\.[a-z]{2,}$', h):
        return None
    return h


# ---------------------------------------------------------------- stack
pkg = {}
try:
    pkg = json.loads(rd(os.path.join(ROOT, 'package.json')) or '{}')
except Exception:
    pkg = {}
deps = {**(pkg.get('dependencies') or {}), **(pkg.get('devDependencies') or {})}

# Root entry points first. steal-a-chicken's DEPLOY.md says the entry is
# `python3 gen.py`; picking build/build.py instead rewrote site/ into a state
# that no longer matched the committed sitemap, and its verifier then reported
# 57 errors that did not exist before the audit touched anything.
GEN_ENTRIES = ['gen.py', 'generate.py', 'build.py', 'gen_site.py',
               'build/generate.py', 'build/build.py', 'build/build_site.py',
               'build/run_build.py', 'build/gen.py']
generator = next((g for g in GEN_ENTRIES if os.path.exists(os.path.join(ROOT, g))), None)

app_dir = next((d for d in ('src/app', 'app') if os.path.isdir(os.path.join(ROOT, d))), None)
astro = 'astro' in deps or os.path.exists(os.path.join(ROOT, 'astro.config.mjs')) \
    or os.path.exists(os.path.join(ROOT, 'astro.config.ts'))

if 'next' in deps and app_dir:
    stack = 'next-app'
elif astro:
    stack = 'astro'
elif generator:
    stack = 'generator'
else:
    stack = 'static'
INFO['stack'] = stack
INFO['generator'] = generator

# ---------------------------------------------------------------- web root
# v1 assumed the repo root. big-walk-companion keeps a stale copy there and
# the live site in site/, which produced five bogus findings.
def find_web_root():
    """Find the directory that is actually served.

    A fixed candidate list is not enough: animebreaker.online and
    activematter-guide nest the output at site/site/, so a one-level probe
    reports 'not a site' for a real 67-page site. Walk instead, and prefer the
    directory that carries robots.txt/sitemap.xml alongside index.html.
    """
    best = None
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        depth = os.path.relpath(dp, ROOT).count(os.sep) + (0 if dp == ROOT else 1)
        if depth > 4:
            dns[:] = []
            continue
        names = set(fns)
        if 'index.html' not in names and 'robots.txt' not in names:
            continue
        has_robots = 'robots.txt' in names
        has_sm = bool(names & {'sitemap.xml', 'sitemap-index.xml'})
        has_index = 'index.html' in names
        if not (has_robots or has_sm or has_index):
            continue
        n_html = sum(1 for _ in walk(dp, {'.html'}))
        # a directory nobody deploys: drafts, docs, examples, templates…
        rel_l = os.path.relpath(dp, ROOT).lower()
        junk = any(seg in ('drafts', 'draft', 'docs', 'doc', 'examples', 'example',
                           'templates', 'template', 'samples', 'test', 'tests',
                           'archive', 'backup', 'old')
                   for seg in rel_l.replace('\\', '/').split('/'))
        # markers first, then page count, then prefer the shallower directory
        score = (-int(junk), has_robots + has_sm + has_index, n_html, -depth)
        if best is None or score > best[0]:
            best = (score, os.path.relpath(dp, ROOT))
    return best[1] if best else None


# What is deployed is what is COMMITTED. Only generate when the repo ships no
# built output (the-veil and racehorses-online gitignore theirs) — and never
# mutate a tree that already has output, or the audit judges its own damage.
committed_root = find_web_root()
committed_pages = len(list(walk(os.path.join(ROOT, committed_root), {'.html'}))) \
    if committed_root else 0
INFO['committed_pages'] = committed_pages

if RUN_GEN and generator and committed_pages == 0:
    r = subprocess.run([sys.executable, os.path.basename(generator)],
                       cwd=os.path.join(ROOT, os.path.dirname(generator)) or ROOT,
                       capture_output=True, text=True, timeout=600)
    INFO['generator_ran'] = (r.returncode == 0)
    INFO['generator_entry'] = generator
    INFO['generator_tail'] = (r.stdout or r.stderr)[-300:]
elif generator and committed_pages:
    INFO['generator_ran'] = False
    INFO['generator_skipped'] = '仓库已提交构建产物，直接审查产物，不重跑生成器'

web_root_rel = find_web_root()
INFO['web_root'] = web_root_rel
WEB = os.path.join(ROOT, web_root_rel) if web_root_rel else None
pages = sorted(walk(WEB, {'.html'})) if WEB else []
INFO['built_pages'] = len(pages)
# Astro/Next repos do not commit build output. Without it, every per-page
# check below is simply unavailable — say so, so that "no findings" is not
# mistaken for "clean".
INFO['page_level_checked'] = bool(pages)

# ---------------------------------------------------------------- is it a site?
src_routes = []
for d in ('src/pages', 'pages'):
    if os.path.isdir(os.path.join(ROOT, d)):
        src_routes = [p for p in walk(os.path.join(ROOT, d), {'.astro', '.md', '.mdx', '.tsx', '.ts', '.js'})]
        break
if app_dir:
    src_routes = [p for p in walk(os.path.join(ROOT, app_dir)) if os.path.basename(p).startswith('page.')]
INFO['source_routes'] = len(src_routes)

# ---------------------------------------------------------------- declared domain
declared = {}
astro_cfg = rd(os.path.join(ROOT, 'astro.config.mjs')) + rd(os.path.join(ROOT, 'astro.config.ts'))
# objectbrief writes `const site = process.env.SITE_URL || 'https://...'` then
# passes `site` by shorthand. v1 only matched the literal form.
for m in re.finditer(r'site\s*[:=]\s*["\']([^"\']+)["\']', astro_cfg):
    declared['astro.config site'] = m.group(1)
for m in re.finditer(r'(?:const|let|var)\s+site\s*=\s*[^;\n]*?["\']([^"\']*https?://[^"\']*)["\']', astro_cfg):
    declared.setdefault('astro.config site', m.group(1))

gen_cfg = ''
for c in ('build/config.py', 'config.py', 'build/conf.py'):
    gen_cfg += rd(os.path.join(ROOT, c)) + '\n'
for m in re.finditer(r'^\s*DOMAIN\s*=\s*["\']([^"\']+)["\']', gen_cfg, re.M):
    declared['config.py DOMAIN'] = m.group(1)
for m in re.finditer(r'["\']domain["\']\s*:\s*["\']([^"\']+)["\']', gen_cfg):
    declared['config SITE.domain'] = m.group(1)

envtxt = ''
for n in ('.env.example', '.env', '.env.local.example', '.env.production'):
    envtxt += rd(os.path.join(ROOT, n)) + '\n'
for m in re.finditer(r'(?:NEXT_PUBLIC_)?(?:APP|SITE|WEB)_URL\s*=\s*["\']?([^\s"\'\n]+)', envtxt, re.I):
    declared['env app_url'] = m.group(1)

# poor normalises pooptimer.com -> pooptimer.org in src/config/index.ts. Any
# domain comparison that ignores that layer is wrong.
#   if (parsed.hostname === 'pooptimer.com') parsed.hostname = 'pooptimer.org'
# The host being COMPARED is the one rewritten away; the one ASSIGNED is the
# survivor. v1 of this check had it backwards and reported .com as effective.
norm_from, norm_to = set(), set()
src_dir = os.path.join(ROOT, 'src')
for p in (list(walk(src_dir, {'.ts', '.tsx'}))[:400] if os.path.isdir(src_dir) else []):
    t = rd(p, 40000)
    if 'hostname' not in t:
        continue
    # the comparison often carries a method call: hostname.toLowerCase() === '…'
    for m in re.finditer(r'hostname(?:\s*\.\s*\w+\s*\(\s*\))*\s*===?\s*["\']([^"\']+)["\']', t):
        norm_from.add(m.group(1).lower())
    for m in re.finditer(r'hostname(?:\s*\.\s*\w+\s*\(\s*\))*\s*=(?!=)\s*["\']([^"\']+)["\']', t):
        norm_to.add(m.group(1).lower())
norm_from -= norm_to
INFO['url_rewritten_away'] = sorted(norm_from)
INFO['url_rewritten_to'] = sorted(norm_to)

hosts = {k: host_of(v) for k, v in declared.items()}
hosts = {k: v for k, v in hosts.items() if v}
# drop hosts the config rewrites away, and add the survivor it rewrites to
effective = {k: v for k, v in hosts.items() if v not in norm_from}
for h in norm_to:
    hh = host_of('https://' + h)
    if hh:
        effective.setdefault('config 归一化目标', hh)
INFO['declared_domains'] = hosts
INFO['distinct_domains'] = sorted(set(effective.values()))

if len(set(effective.values())) > 1:
    add('high', 'domain_mismatch',
        '配置里声明了多个不同域名，且没有归一化代码把它们合并。canonical 与 sitemap 会指向不同主机。',
        [f'{k} = {v}' for k, v in sorted(effective.items())])

site_domain = INFO['distinct_domains'][0] if INFO['distinct_domains'] else None

# A live site always has its domain configured somewhere — canonical, sitemap
# and hreflang all need it. game-time declares none and its site/ holds a
# single page written by gen_site.py as a sample, so it is a tool, not a site.
# Guarded by the page count so that a real domainless site (shouyouradar, 613
# committed pages) is not swept up.
tiny_and_domainless = (not site_domain) and len(pages) <= 2 and len(src_routes) <= 2
is_site = (bool(pages) or bool(src_routes) or bool(site_domain)) and not tiny_and_domainless
INFO['is_site'] = is_site
INFO['not_a_site_reason'] = ('无域名声明且产物不足 3 页，判定为工具/脚手架而非站点'
                             if tiny_and_domainless else None)
if not is_site:
    INFO['verdict'] = 'not-a-site'
    json.dump({'info': INFO, 'findings': []}, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print(f'{NAME}: not-a-site (no web root, no routes, no domain)')
    sys.exit(0)

# ---------------------------------------------------------------- robots / sitemap
robots_sources, sitemap_sources = [], []
for c in ('robots.txt', 'public/robots.txt', 'static/robots.txt'):
    if os.path.exists(os.path.join(ROOT, c)):
        robots_sources.append(c)
if WEB and os.path.exists(os.path.join(WEB, 'robots.txt')):
    robots_sources.append(f'{web_root_rel}/robots.txt')
# Astro / Next endpoint routes — v1 knew none of these.
for c in ('src/pages/robots.txt.ts', 'src/pages/robots.txt.js',
          'pages/robots.txt.ts', 'src/app/robots.ts', 'app/robots.ts'):
    if os.path.exists(os.path.join(ROOT, c)):
        robots_sources.append(c)

for c in ('sitemap.xml', 'public/sitemap.xml', 'sitemap-index.xml'):
    if os.path.exists(os.path.join(ROOT, c)):
        sitemap_sources.append(c)
if WEB:
    for c in ('sitemap.xml', 'sitemap-index.xml'):
        if os.path.exists(os.path.join(WEB, c)):
            sitemap_sources.append(f'{web_root_rel}/{c}')
for c in ('src/pages/sitemap.xml.ts', 'src/pages/sitemap.xml.js',
          'pages/sitemap.xml.ts', 'src/app/sitemap.ts', 'app/sitemap.ts'):
    if os.path.exists(os.path.join(ROOT, c)):
        sitemap_sources.append(c)
if '@astrojs/sitemap' in deps and re.search(r'sitemap\s*\(', astro_cfg):
    sitemap_sources.append('@astrojs/sitemap integration')
# a generator that writes them counts too
if generator:
    gtxt = rd(os.path.join(ROOT, generator))
    for c in ('build/components.py', 'build/build_site.py'):
        gtxt += rd(os.path.join(ROOT, c))
    if 'robots.txt' in gtxt:
        robots_sources.append(f'{generator} 生成 robots.txt')
    if 'sitemap' in gtxt:
        sitemap_sources.append(f'{generator} 生成 sitemap.xml')

INFO['robots_sources'] = sorted(set(robots_sources))
INFO['sitemap_sources'] = sorted(set(sitemap_sources))
if not robots_sources:
    add('high', 'robots_missing', '找不到任何 robots.txt 来源：静态文件、端点路由、集成、生成器都没有。')
if not sitemap_sources:
    add('high', 'sitemap_missing', '找不到任何 sitemap 来源：静态文件、端点路由、@astrojs/sitemap、生成器都没有。')

# ---------------------------------------------------------------- robots x sitemap
disallow = []
rtxt = ''
for s in INFO['robots_sources']:
    rtxt += rd(os.path.join(ROOT, s)) + '\n'
disallow += [m.strip() for m in re.findall(r'^\s*Disallow:\s*(\S+)', rtxt, re.I | re.M)]
for blk in re.findall(r'disallow\s*:\s*\[([^\]]*)\]', rtxt, re.I):
    disallow += re.findall(r'["\'](/[^"\']*)["\']', blk)
disallow = [d for d in dict.fromkeys(disallow) if d.startswith('/')]
INFO['disallow'] = disallow

sm_routes = []
for s in INFO['sitemap_sources']:
    p = os.path.join(ROOT, s)
    if not os.path.isfile(p):
        continue
    t = rd(p)
    if s.endswith('.xml'):
        sm_routes += [re.sub(r'^https?://[^/]+', '', u) or '/' for u in re.findall(r'<loc>([^<]+)</loc>', t)]
    else:
        blk = re.search(r'staticRoutes\s*=\s*\[(.*?)\]', t, re.S)
        sm_routes += re.findall(r'["\'](/[^"\'\s]*)["\']', blk.group(1) if blk else '')
sm_routes = list(dict.fromkeys(sm_routes))
INFO['sitemap_routes'] = len(sm_routes)

conflict = []
for r in sm_routes:
    for d in disallow:
        dd = d.rstrip('*').rstrip('/')
        if not dd or dd == '':
            continue
        if r.rstrip('/') == dd or (d.endswith('*') and r.startswith(dd)):
            conflict.append(f'{r}  ←  Disallow: {d}')
if conflict:
    add('high', 'robots_sitemap_conflict',
        'URL 同时被 sitemap 提交和 robots 屏蔽。Search Console 会报 "Submitted URL blocked by robots.txt"。',
        sorted(set(conflict))[:20])

# ---------------------------------------------------------------- per-page HTML
titles, metas = {}, {}
noindexed, no_canon, canon_other = set(), [], []
hreflang_sets = {}
missing_xdefault = []


def page_url(p):
    rel = os.path.relpath(p, WEB).replace(os.sep, '/')
    if rel.endswith('index.html'):
        rel = rel[:-len('index.html')]
    return '/' + rel.lstrip('/')


for p in pages:
    t = rd(p)
    u = page_url(p)
    rm = ROBOTS_META_RE.search(t)
    if rm and 'noindex' in rm.group(1).lower():
        noindexed.add(u)
        continue                      # noindex pages are exempt from the rest
    ti = TITLE_RE.search(t)
    if ti:
        titles.setdefault(ti.group(1).strip(), []).append(u)
    de = DESC_RE.search(t)
    if de:
        metas.setdefault(de.group(1).strip(), []).append(u)
    cm = CANON_RE.search(t)
    if not cm:
        # a 404 page is not a canonical target and is not submitted anywhere
        if os.path.basename(p) not in ('404.html', '500.html'):
            no_canon.append(u)
    else:
        c = re.sub(r'^https?://[^/]+', '', cm.group(1)) or '/'
        if (c.rstrip('/') or '/') != (u.rstrip('/') or '/'):
            canon_other.append((u, c))
    hl = HREFLANG_RE.findall(t)
    if hl:
        tags = {a for a, _ in hl}
        hreflang_sets[u] = sorted(tags)
        # a single self-referential tag means the page has no translations:
        # correct to omit x-default (the-veil /guides/tomes/)
        if len(tags - {'x-default'}) > 1 and 'x-default' not in tags:
            missing_xdefault.append(u)

INFO['noindex_pages'] = len(noindexed)
INFO['pages_with_hreflang'] = len(hreflang_sets)

# sitemap vs noindex: submitting a noindex URL is a real Search Console error
sm_set = {r.rstrip('/') or '/' for r in sm_routes}
ni_in_sm = sorted({u for u in noindexed if (u.rstrip('/') or '/') in sm_set})
if ni_in_sm:
    add('high', 'noindex_in_sitemap',
        'noindex 页面仍被提交进 sitemap。Search Console 会报 "Submitted URL marked noindex"。',
        ni_in_sm[:20])

dup_t = {k: v for k, v in titles.items() if len(v) > 1}
# shouyouradar serves /game/2015.html and /game/stellaris.html with the same
# title, but the ID URL canonicals to the slug URL and only the slug is in the
# sitemap. That is deliberate consolidation, not two pages competing — so a
# group where every page but one points its canonical at that one is not a
# finding. v1 reported these as duplicates.
consolidated_to = {u: c for u, c in canon_other}
INFO['canonical_consolidations'] = len(consolidated_to)
_kept = {}
for k, v in dup_t.items():
    targets = {(consolidated_to.get(p, p).rstrip('/') or '/') for p in v}
    if len(targets) == 1:
        continue          # whole group folds onto one URL by canonical
    _kept[k] = v
dup_t = _kept
if dup_t:
    # same-language duplicates compete; cross-language ones are handled by
    # hreflang and only cost SERP click-through
    same_lang = {k: v for k, v in dup_t.items()
                 if len({re.match(r'/([a-z]{2})(?:-[a-zA-Z0-9]+)?/', x).group(1)
                         if re.match(r'/([a-z]{2})(?:-[a-zA-Z0-9]+)?/', x) else 'en'
                         for x in v}) == 1}
    cross = {k: v for k, v in dup_t.items() if k not in same_lang}
    if same_lang:
        add('high', 'duplicate_titles_same_language',
            '同一语言下多个页面共用标题，它们会互相竞争同一关键词。',
            [f'{len(v)}×  "{k[:70]}"  {v[:4]}' for k, v in list(same_lang.items())[:10]])
    if cross:
        add('low', 'duplicate_titles_across_languages',
            '不同语言版本共用同一标题。hreflang 正确时 Google 不会合并它们，代价只是该语言用户在搜索结果里看到外语标题、点击率受损。'
            '若后缀是专名（游戏名、模式名），同标题是正确的。',
            [f'{len(v)}×  "{k[:70]}"' for k, v in list(cross.items())[:10]])

if no_canon:
    add('med' if len(no_canon) > 2 else 'low', 'missing_canonical',
        '页面没有 canonical。',
        sorted(no_canon)[:20])

if missing_xdefault:
    add('low', 'hreflang_no_xdefault',
        f'{len(missing_xdefault)} 个多语言页面的 hreflang 集合里没有 x-default。'
        '注意：这是风格选择而非缺陷——当每个页面都已明确对应某语言、且默认语言版本本身就是兜底时，'
        'x-default 与 hreflang="<默认语言>" 信息重复。若仓库自带校验器规定了集合大小，以校验器为准。',
        sorted(missing_xdefault)[:10])

# ---------------------------------------------------------------- sitemap targets
# v1 resolved these against the repo root and reported 15 phantom dead URLs.
dead = []
if WEB and sm_routes:
    for r in sm_routes:
        rel = r.strip('/')
        if not rel:
            continue
        if any(os.path.exists(os.path.join(WEB, rel + sfx))
               for sfx in ('', '.html', '/index.html')):
            continue
        dead.append(r)
if dead and len(dead) < len(sm_routes):
    add('med', 'sitemap_dead_urls',
        'sitemap 里的 URL 在网站根下找不到对应文件。注意：动态路由、catch-all 和服务端渲染页面属正常，需人工确认。',
        sorted(dead)[:20])

# ---------------------------------------------------------------- next-app routes
if stack == 'next-app':
    bare_meta_layout = []
    for p in walk(os.path.join(ROOT, app_dir)):
        if os.path.basename(p).startswith('layout.'):
            t = rd(p, 60000)
            if re.search(r'generateMetadata\s*=\s*getMetadata\(\s*\)', t):
                bare_meta_layout.append(os.path.relpath(p, ROOT))
    seo_lib = next((p for p in walk(os.path.join(ROOT, 'src'), {'.ts'})
                    if p.endswith('lib/seo.ts')), None) if os.path.isdir(os.path.join(ROOT, 'src')) else None
    fallback_home = bool(seo_lib and re.search(r"canonicalUrl\s*=\s*['\"]/['\"]", rd(seo_lib)))

    # Layouts that only supply SITE-WIDE defaults must not count as coverage —
    # inheriting those is the very defect being looked for. That means the app
    # root layout, the [locale] layout, and any layout whose metadata is a bare
    # getMetadata() call.
    site_default_layouts = set()
    for p in walk(os.path.join(ROOT, app_dir)):
        if not os.path.basename(p).startswith('layout.'):
            continue
        d = os.path.normpath(os.path.dirname(p))
        seg = os.path.relpath(d, os.path.join(ROOT, app_dir)).replace(os.sep, '/')
        lt = rd(p, 60000)
        if seg in ('.', '') or re.fullmatch(r'\[[a-z]+\]', seg) \
                or re.search(r'generateMetadata\s*=\s*getMetadata\(\s*\)', lt):
            site_default_layouts.add(d)
    INFO['site_default_layouts'] = sorted(
        os.path.relpath(d, ROOT) for d in site_default_layouts)

    def layout_supplies_metadata(page_path):
        """A scoped sibling/ancestor layout can carry the metadata — that is how
        a 'use client' page gets its noindex. Site-wide defaults don't count."""
        d = os.path.normpath(os.path.dirname(page_path))
        stop = os.path.normpath(os.path.join(ROOT, app_dir))
        while True:
            if d not in site_default_layouts:
                for ext in ('tsx', 'ts', 'jsx', 'js'):
                    lp = os.path.join(d, f'layout.{ext}')
                    if os.path.exists(lp) and re.search(
                            r'generateMetadata|export\s+const\s+metadata', rd(lp, 60000)):
                        return True
            if d == stop or len(d) <= len(stop):
                return False
            d = os.path.dirname(d)

    nometa = []
    for p in src_routes:
        t = rd(p, 60000)
        if 'generateMetadata' in t or re.search(r'export\s+const\s+metadata', t):
            continue
        # a redirect page needs no metadata (poor /blog)
        if re.search(r'permanentRedirect\s*\(|\bredirect\s*\(', t):
            continue
        if layout_supplies_metadata(p):
            continue
        r = '/' + os.path.relpath(p, os.path.join(ROOT, app_dir)).replace(os.sep, '/')
        r = re.sub(r'/page\.(tsx|ts|jsx|js)$', '', r)
        r = r.replace('/[locale]', '').replace('/(landing)', '').replace('/(auth)', '') \
             .replace('/(chat)', '').replace('/(admin)', '').replace('/(ai)', '')
        blocked = any((d.rstrip('*').strip('/') and ('/' + d.rstrip('*').strip('/')) in r)
                      for d in disallow)
        if not blocked:
            nometa.append(r or '/')
    if nometa and fallback_home and bare_meta_layout:
        add('high', 'inherits_home_canonical',
            f'这些路由没有导出任何 metadata，于是继承 {bare_meta_layout[0]} 的裸 getMetadata()；'
            '而共用的 seo 库在未传 canonicalUrl 时回落成 "/"，等于这些可抓取页面把首页声明为自己的 canonical，'
            '标题描述也与首页重复。robots 并未屏蔽它们。',
            sorted(nometa)[:20])
    elif nometa:
        add('med', 'pages_without_metadata',
            '这些可抓取路由没有导出 metadata，会继承 layout 的默认标题与描述。',
            sorted(nometa)[:20])
    INFO['seo_canonical_fallback_home'] = fallback_home

# ---------------------------------------------------------------- repo's own verifier
verifier = next((v for v in ('build/verify.py', 'build/verify_site.py', 'verify.py', 'verify_site.py')
                 if os.path.exists(os.path.join(ROOT, v))), None)
INFO['verifier'] = verifier
if verifier:
    try:
        r = subprocess.run([sys.executable, os.path.basename(verifier)],
                           cwd=os.path.join(ROOT, os.path.dirname(verifier)) or ROOT,
                           capture_output=True, text=True, timeout=300)
        tail = (r.stdout or '').strip().splitlines()
        INFO['verifier_output'] = tail[-1] if tail else (r.stderr or '')[-200:]
        # "pages=108 sitemap=108 errors=0" — a loose `(\d+)\s*errors?` grabs the
        # 108 in front of "errors" instead of the 0 behind it. Try keyed forms
        # first, both orders, and fall back to the process exit code.
        full = (r.stdout or '') + (r.stderr or '')
        out = INFO['verifier_output']
        n_err = None
        # Match a line that *is* the count ("errors: 0" in a RESULT block, or
        # "0 errors, 15 warnings"). A loose whole-output search picks up
        # unrelated numbers — steal-a-chicken prints "indexable HTML: 57"
        # above its "errors: 0" and that produced a phantom 57.
        for line in full.splitlines():
            mm = re.match(r'\s*errors?\s*[=:]\s*(\d+)', line, re.I) \
                or re.match(r'\s*(\d+)\s+errors?\b', line, re.I)
            if mm:
                n_err = int(mm.group(1))
        if n_err is None:
            # steal-a-chicken's verify.py exits non-zero while printing only
            # warnings. An exit code alone is not evidence of an error, so
            # count the error-tagged lines instead.
            e_lines = [l for l in full.splitlines() if re.match(r'\s*(E:|ERROR|FAIL)', l)]
            INFO['verifier_warnings'] = len([l for l in full.splitlines()
                                             if re.match(r'\s*W:', l)])
            n_err = len(e_lines) if e_lines else 0
        INFO['verifier_errors'] = n_err
        if n_err:
            add('high', 'own_verifier_fails',
                f'仓库自带的 {verifier} 报告 {n_err} 个错误。以它为准——它编码的是这个项目自己的规格。',
                [INFO['verifier_output']])
    except Exception as e:
        INFO['verifier_output'] = f'run failed: {e}'

# ---------------------------------------------------------------- heavy images
heavy = []
for base in ([WEB] if WEB else []) + [os.path.join(ROOT, 'public')]:
    if not base or not os.path.isdir(base):
        continue
    for p in walk(base, {'.png', '.jpg', '.jpeg', '.gif', '.webp'}):
        try:
            sz = os.path.getsize(p)
        except OSError:
            continue
        if sz > 500 * 1024:
            heavy.append((sz, os.path.relpath(p, ROOT)))
heavy.sort(reverse=True)
if heavy:
    # referenced or not? unreferenced files never hit LCP, they only bloat deploys
    allsrc = ''
    for d in ('src', 'content', 'build'):
        dd = os.path.join(ROOT, d)
        if os.path.isdir(dd):
            for p in list(walk(dd))[:600]:
                allsrc += rd(p, 40000)
    used, unused = [], []
    for sz, rel in heavy[:40]:
        base = os.path.basename(rel)
        (used if base in allsrc else unused).append(f'{sz // 1024}KB  {rel}')
    if used:
        add('med', 'heavy_images_in_use',
            '被引用的图片超过 500KB，直接影响 Largest Contentful Paint（Core Web Vitals 排名信号）。'
            '若经由 next/image 等按需优化层提供，实际影响较小，需实测确认。',
            used[:20])
    if unused:
        add('low', 'heavy_images_unreferenced',
            '超过 500KB 但源码里找不到引用的图片，不影响 LCP，只占部署体积。可能是模板示例图。',
            unused[:20])

# ---------------------------------------------------------------- duplicate site copies
if WEB and web_root_rel != '.':
    both = [f for f in ('index.html',)
            if os.path.exists(os.path.join(ROOT, f)) and os.path.exists(os.path.join(WEB, f))]
    if both:
        add('med', 'duplicate_site_copy',
            f'仓库根和 {web_root_rel}/ 下各有一份站点副本。'
            f'robots/sitemap 只在 {web_root_rel}/ 里，确认部署指向哪个目录，并删掉另一份。')

if not INFO['page_level_checked']:
    add('info', 'page_level_not_checked',
        f'这个仓库不提交构建产物（{stack}），所以本次没有检查任何渲染后的页面：'
        'canonical、hreflang、标题重复、noindex、sitemap 死链这些结论都缺席，'
        '不代表没问题。要覆盖它们需要能跑构建（当前沙箱的代理以 403 拒绝 npm registry）。')

res = {'info': INFO, 'findings': F}
json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1)
hi = sum(1 for x in F if x['sev'] == 'high')
print(f"{NAME}: stack={stack} web_root={web_root_rel} pages={len(pages)} "
      f"domain={site_domain} verifier={INFO.get('verifier_errors')} "
      f"findings={len(F)} high={hi}")
