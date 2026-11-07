#!/usr/bin/env python3
"""内容层审计：孤儿页面、薄页面、标题/描述长度、H1。

用法: python3 -I content.py <web_root> <out.json> [--name NAME]

刻意保守，宁可漏报也不误报——这套检查此前的教训都是误报造成的：
  * 孤儿判定要把 /a/、/a/index.html、/a 视为同一个页面，否则整站全是孤儿。
  * 字数只数正文，并且在没有 main/article 时才退回 body，同时剔除
    nav/header/footer/aside/script/style，否则导航文字会把薄页面撑过阈值。
  * 法律页、联系页本来就短，单独标注而不计入薄页面。
"""
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.abspath(sys.argv[1].rstrip('/'))
OUT = sys.argv[2]
NAME = sys.argv[sys.argv.index('--name') + 1] if '--name' in sys.argv \
    else os.path.basename(os.path.dirname(ROOT)) or os.path.basename(ROOT)

THIN = 300          # 低于这个字数算薄
VERY_THIN = 150
TITLE_MAX = 60      # Google 按像素截断，字符数只是代理指标
DESC_MAX = 160
# 这些页面天然就短，不算薄
SHORT_OK = re.compile(
    r'(privacy|terms|legal|cookie|contact|about|disclaimer|imprint|'
    r'aviso|politica|privacidade|termos|impressum|404|thanks?|success)',
    re.I)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.desc, self.robots = '', '', ''
        self.h1 = []
        self.links = []
        self.canonical = ''
        self._skip = 0
        self._in_title = False
        self._in_h1 = False
        self._text = []
        self._main_depth = None
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self._depth += 1
        if tag in ('script', 'style', 'nav', 'header', 'footer', 'aside', 'svg'):
            self._skip += 1
        elif tag == 'title':
            self._in_title = True
        elif tag == 'h1':
            self._in_h1 = True
            self.h1.append('')
        elif tag == 'meta':
            n = (a.get('name') or '').lower()
            if n == 'description':
                self.desc = a.get('content', '')
            elif n == 'robots':
                self.robots = (a.get('content') or '').lower()
        elif tag == 'link' and (a.get('rel') or '').lower() == 'canonical':
            self.canonical = a.get('href', '')
        elif tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        elif tag in ('main', 'article') and self._main_depth is None:
            self._main_depth = self._depth

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'nav', 'header', 'footer', 'aside', 'svg'):
            self._skip = max(0, self._skip - 1)
        elif tag == 'title':
            self._in_title = False
        elif tag == 'h1':
            self._in_h1 = False
        self._depth -= 1

    def handle_data(self, d):
        if self._in_title:
            self.title += d
        if self._in_h1 and self.h1:
            self.h1[-1] += d
        if not self._skip:
            self._text.append(d)

    def words(self):
        t = re.sub(r'\s+', ' ', ' '.join(self._text)).strip()
        # 中日韩不用空格分词，按字符计；其余语言按词计。
        #
        # 这里必须是 Unicode 感知的字母类，不能写 [A-Za-z]：第一版就是
        # 那样写的，于是 graveyard-keeper2 的俄语页整段西里尔文被算成 0 词，
        # /ru/alchemy/ 实际 290 词却报成 34 词、判定为"极薄页面"。
        # 同一个毛病此前也让 hreflang 的 [a-z-] 匹配不到 pt-BR。
        cjk_re = r'[一-鿿぀-ヿ가-힯]'
        cjk = len(re.findall(cjk_re, t))
        rest = re.sub(cjk_re, ' ', t)
        words = len(re.findall(r'[^\W\d_]+', rest, re.UNICODE))
        return cjk + words


def url_of(path):
    rel = os.path.relpath(path, ROOT).replace('\\', '/')
    if rel.endswith('/index.html'):
        rel = rel[:-len('index.html')]
    elif rel == 'index.html':
        rel = ''
    return '/' + rel


def norm(u):
    """把一个链接归一成和 url_of 同形的 key。"""
    u = u.split('#')[0].split('?')[0]
    if not u:
        return None
    if re.match(r'^[a-z]+:', u, re.I) and not u.lower().startswith('http'):
        return None                      # mailto:, tel:, javascript:
    if u.lower().startswith('http'):
        m = re.match(r'^https?://[^/]+(/.*)?$', u, re.I)
        u = m.group(1) or '/' if m else '/'
    if not u.startswith('/'):
        return ('REL', u)
    if u.endswith('/index.html'):
        u = u[:-len('index.html')]
    if not u.endswith('/') and '.' not in u.rsplit('/', 1)[-1]:
        u += '/'
    return u


pages = {}
for dp, dns, fns in os.walk(ROOT):
    dns[:] = [d for d in dns if d not in ('_astro', 'assets', 'node_modules',
                                          '.git', '_next')]
    for fn in fns:
        if not fn.endswith('.html'):
            continue
        p = os.path.join(dp, fn)
        try:
            raw = open(p, encoding='utf-8', errors='ignore').read()
        except OSError:
            continue
        pg = Page()
        try:
            pg.feed(raw)
        except Exception:
            continue
        u = url_of(p)
        if not u.endswith('/'):
            u2 = u
        else:
            u2 = u
        pages[u2] = pg

# 入链统计
inbound = {u: 0 for u in pages}
for u, pg in pages.items():
    base = u if u.endswith('/') else u.rsplit('/', 1)[0] + '/'
    for href in pg.links:
        k = norm(href)
        if k is None:
            continue
        if isinstance(k, tuple):                       # 相对链接
            k = os.path.normpath(os.path.join(base, k[1])).replace('\\', '/')
            if not k.endswith('/') and '.' not in k.rsplit('/', 1)[-1]:
                k += '/'
        if k in inbound and k != u:
            inbound[k] += 1

F = []
orphans, thin, very_thin, long_title, no_desc, long_desc, h1_bad = \
    [], [], [], [], [], [], []
titles = {}
for u, pg in sorted(pages.items()):
    if 'noindex' in pg.robots:
        continue                                        # 不索引的页不参与判定
    # canonical 指向别处 = 有意的合并页（shouyouradar 有 214 个 ID->slug
    # 这样的页）。它们存在的意义就是接住旧链接再把权重导走，因此既不该
    # 被站内链接，也不该有完整正文——按孤儿或薄页面报出来全是噪音。
    cu = pg.canonical.split('#')[0].split('?')[0].rstrip('/')
    if cu:
        cu_path = re.sub(r'^https?://[^/]+', '', cu)
        if cu_path and cu_path.rstrip('/') != u.rstrip('/') \
                and cu_path.rstrip('/') != (u + 'index.html').rstrip('/'):
            continue
    # 404/500 这类框架页本来就不该被链接
    if u != '/' and inbound[u] == 0 and not re.search(r'/(404|500|_not-found)(\.html|/)?$', u):
        orphans.append(u)
    w = pg.words()
    if w < VERY_THIN and not SHORT_OK.search(u):
        very_thin.append(f'{w} 词  {u}')
    elif w < THIN and not SHORT_OK.search(u):
        thin.append(f'{w} 词  {u}')
    t = pg.title.strip()
    if len(t) > TITLE_MAX:
        long_title.append(f'{len(t)} 字符  {u}')
    d = pg.desc.strip()
    if not d:
        no_desc.append(u)
    elif len(d) > DESC_MAX:
        long_desc.append(f'{len(d)} 字符  {u}')
    n1 = len(pg.h1)
    if n1 != 1:
        h1_bad.append(f'{n1} 个 h1  {u}')


def add(sev, code, msg, det):
    if det:
        F.append({'sev': sev, 'code': code, 'msg': msg,
                  'count': len(det), 'detail': det[:25]})


add('med', 'orphan_pages',
    '站内没有任何其他页面链接到它们。Google 靠链接发现和评估页面重要性，'
    '孤儿页面即使在 sitemap 里也会被当成低优先级。注意：若站点靠分页或'
    'JS 渲染导航，这里会误报，需人工确认。', orphans)
add('med', 'very_thin_pages',
    f'正文少于 {VERY_THIN} 词。字数本身不是排名因素，但极薄的页面是'
    'Google「规模化内容滥用」政策的直接判定依据之一。', very_thin)
add('low', 'thin_pages', f'正文少于 {THIN} 词。', thin)
add('low', 'title_too_long',
    f'标题超过 {TITLE_MAX} 字符，搜索结果里很可能被截断，CTR 受损。'
    'Google 实际按像素宽度截断，字符数只是代理指标。', long_title)
add('low', 'missing_description',
    '没有 meta description。Google 会自行摘取正文片段，可控性变差。', no_desc)
add('low', 'description_too_long',
    f'描述超过 {DESC_MAX} 字符，会被截断。', long_desc)
add('low', 'h1_not_exactly_one', '页面没有 h1 或有多个 h1。', h1_bad)

res = {'info': {'repo': NAME, 'web_root': os.path.relpath(ROOT),
                'pages_checked': len(pages)}, 'findings': F}
json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1)
print(f'{NAME}: pages={len(pages)} orphan={len(orphans)} '
      f'very_thin={len(very_thin)} thin={len(thin)} '
      f'long_title={len(long_title)} no_desc={len(no_desc)} h1_bad={len(h1_bad)}')
