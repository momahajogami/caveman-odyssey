#!/usr/bin/env python3
"""
build-episodes.py — compile Caveman Odyssey markdown sources into HTML read + print pages.

Usage:
    python3 scripts/build-episodes.py episodes-src/book-04-sparta.md
    python3 scripts/build-episodes.py episodes-src/*.md   # rebuild all

Source format: see episodes-src/TEMPLATE.md

Output:
    episodes/<slug>.html         — read page
    episodes/<slug>-print.html   — printable puppet script
"""

import re
import sys
import os
from pathlib import Path

# ── color families ────────────────────────────────────────────────────────────

FAMILIES = {
    'amber':   dict(hc=36,  hd=8,  sat=75, lc=28, lr=8),
    'violet':  dict(hc=268, hd=14, sat=60, lc=26, lr=8),
    'teal':    dict(hc=172, hd=12, sat=70, lc=28, lr=8),
    'slate':   dict(hc=215, hd=8,  sat=40, lc=28, lr=8),
    'forest':  dict(hc=140, hd=10, sat=60, lc=25, lr=8),
    'magenta': dict(hc=312, hd=10, sat=65, lc=26, lr=8),
}

# Default color by slug — override with `color:` in frontmatter
DEFAULT_COLORS = {
    'book-01-gods':    'violet',
    'book-01-feast':   'amber',
    'book-02-wakeup':  'forest',
    'book-02-council': 'slate',
    'book-02-boat':    'teal',
    'book-03-pylos':   'amber',
    'book-04-sparta':  'slate',
    'book-04-proteus': 'teal',
}

# ── markdown parser ───────────────────────────────────────────────────────────

def parse(text):
    """
    Parse a source .md file. Returns a dict:
      meta:   {title, book, part, slug, note, color}
      cast:   [{name, role}]
      script: [{type: scene_head|speech|stage|break, ...}]
      tips:   [str]
    """
    lines = text.splitlines()
    idx = 0

    # frontmatter
    meta = {}
    if lines[idx].strip() == '---':
        idx += 1
        while idx < len(lines) and lines[idx].strip() != '---':
            if ':' in lines[idx]:
                k, _, v = lines[idx].partition(':')
                meta[k.strip()] = v.strip()
            idx += 1
        idx += 1  # skip closing ---

    # sections
    cast, script, tips = [], [], []
    section = None

    # state for speech accumulation
    current_speaker = None
    current_role = None
    current_paras = []

    def flush_speech():
        nonlocal current_speaker, current_role, current_paras
        if current_speaker:
            script.append({
                'type': 'speech',
                'name': current_speaker,
                'role': current_role or '',
                'paras': list(current_paras),
            })
        current_speaker = None
        current_role = None
        current_paras = []

    SPEAKER_RE = re.compile(
        r'^\*\*([^*]+?)\*\*'          # **NAME**
        r'(?:\s*\*\(([^)]+)\)\*)?\s*'  # optional *(role)*
        r':\s*(.*)'                     # : first para text
    )

    for raw in lines[idx:]:
        line = raw.rstrip()
        stripped = line.strip()

        # section headers
        if stripped.startswith('## '):
            flush_speech()
            heading = stripped[3:].strip().lower()
            if 'cast' in heading:
                section = 'cast'
            elif 'script' in heading:
                section = 'script'
            elif 'tip' in heading:
                section = 'tips'
            else:
                section = None
            continue

        if section == 'cast':
            if '|' in stripped and stripped:
                name, _, role = stripped.partition('|')
                cast.append({'name': name.strip(), 'role': role.strip()})
            continue

        if section == 'tips':
            if stripped.startswith('- '):
                tips.append(stripped[2:].strip())
            continue

        if section == 'script':
            # scene head
            if stripped.startswith('### '):
                flush_speech()
                script.append({'type': 'scene_head', 'text': stripped[4:].strip()})
                continue

            # section break
            if stripped == '---':
                flush_speech()
                script.append({'type': 'break'})
                continue

            # stage direction
            if stripped.startswith('> '):
                flush_speech()
                script.append({'type': 'stage', 'text': stripped[2:].strip()})
                continue

            # new speaker
            m = SPEAKER_RE.match(stripped)
            if m:
                flush_speech()
                current_speaker = m.group(1).strip()
                current_role    = (m.group(2) or '').strip()
                first_para      = m.group(3).strip()
                if first_para:
                    current_paras.append(first_para)
                continue

            # continuation paragraph
            if stripped and current_speaker:
                current_paras.append(stripped)
                continue

            # blank line: paragraph boundary (already handled by state)

    flush_speech()

    return dict(meta=meta, cast=cast, script=script, tips=tips)


# ── chipsquirt JS snippet ─────────────────────────────────────────────────────

def chipsquirt_js(family_name):
    f = FAMILIES.get(family_name, FAMILIES['amber'])
    return f"""  (function(){{
    var fam={{hc:{f['hc']},hd:{f['hd']},sat:{f['sat']},lc:{f['lc']},lr:{f['lr']}}};
    function hsvToRgb(h,s,v){{h=((h%360)+360)%360;var c=v*s,x=c*(1-Math.abs((h/60)%2-1)),m=v-c,r,g,b;if(h<60){{r=c;g=x;b=0;}}else if(h<120){{r=x;g=c;b=0;}}else if(h<180){{r=0;g=c;b=x;}}else if(h<240){{r=0;g=x;b=c;}}else if(h<300){{r=x;g=0;b=c;}}else{{r=c;g=0;b=x;}}return[Math.round((r+m)*255),Math.round((g+m)*255),Math.round((b+m)*255)];}}
    function lc(i,p){{var P=1.6180339887,P2=2.6180339887,fr=0.45;var h=((fam.hc+fam.hd*Math.sin(i*fr+p))%360+360)%360;var s=Math.max(0,Math.min(1,fam.sat/100+0.18*Math.sin(i*fr*P+p+1.1)));var v=Math.max(0.08,Math.min(0.60,0.30+0.18*Math.sin(i*fr*P2+p+2.3)));return'rgb('+hsvToRgb(h,s,v)+')';}}
    function colorize(el){{var p=Math.random()*Math.PI*2,i=0,w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT),ns=[],n;while((n=w.nextNode()))ns.push(n);ns.forEach(function(node){{var f=document.createDocumentFragment();for(var ci=0;ci<node.nodeValue.length;ci++){{var ch=node.nodeValue[ci];if(/[ \\t\\n\\r]/.test(ch)){{f.appendChild(document.createTextNode(ch));}}else{{var sp=document.createElement('span');sp.style.color=lc(i++,p);sp.textContent=ch;f.appendChild(sp);}}}}node.parentNode.replaceChild(f,node);}});}}
    document.addEventListener('DOMContentLoaded',function(){{document.querySelectorAll('h1').forEach(function(el){{colorize(el);}});}});
  }})();"""


# ── read page HTML ────────────────────────────────────────────────────────────

READ_CSS = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html { font-size: 18px; }
    body {
      font-family: Georgia, "Times New Roman", serif;
      background: #fdfaf5;
      color: #1a1a1a;
      line-height: 1.8;
      max-width: 640px;
      margin: 0 auto;
      padding: 4rem 2rem 7rem;
    }
    .back { font-size: 0.72rem; color: #bbb; text-decoration: none;
            display: inline-block; margin-bottom: 3.5rem; letter-spacing: 0.06em;
            text-transform: uppercase; }
    .back:hover { color: #666; }
    .print-link { float: right; font-size: 0.72rem; color: #bbb; text-decoration: none;
                  letter-spacing: 0.06em; text-transform: uppercase; }
    .print-link:hover { color: #666; }
    h1 { font-size: 1.9rem; font-weight: normal; line-height: 1.2;
         margin-bottom: 0.35rem; letter-spacing: -0.01em; clear: both; }
    .book-note { font-size: 0.78rem; color: #bbb; font-style: italic; margin-bottom: 4rem; }
    .scene { margin-bottom: 3rem; }
    .speaker {
      font-size: 0.65rem; font-weight: normal; text-transform: uppercase;
      letter-spacing: 0.2em; color: #c0b8ae; margin-bottom: 0.5rem;
    }
    .speaker .role { letter-spacing: 0.04em; text-transform: none; font-style: italic; }
    .speech p { margin-bottom: 0.8rem; font-size: 1rem; }
    .speech p:last-child { margin-bottom: 0; }
    .stage {
      font-style: italic; color: #bbb; font-size: 0.82rem;
      margin: 2rem 0; text-align: center; letter-spacing: 0.01em;
    }
    .section-break { text-align: center; color: #ddd; margin: 3rem 0;
                     font-size: 0.9rem; letter-spacing: 0.5em; }
    .footer { margin-top: 6rem; font-size: 0.72rem; color: #ccc;
              border-top: 1px solid #ede8e0; padding-top: 2rem; }
"""

def render_script_html(script):
    parts = []
    for node in script:
        t = node['type']
        if t == 'scene_head':
            pass  # read page doesn't show scene heads
        elif t == 'break':
            parts.append('<div class="section-break">&middot; &middot; &middot;</div>')
        elif t == 'stage':
            parts.append(f'<div class="stage">{node["text"]}</div>')
        elif t == 'speech':
            role_html = ''
            if node['role']:
                role_html = f' <span class="role">— {node["role"]}</span>'
            paras = ''.join(f'<p>{p}</p>' for p in node['paras'])
            parts.append(
                f'<div class="scene">\n'
                f'  <div class="speaker">{node["name"]}{role_html}</div>\n'
                f'  <div class="speech">{paras}</div>\n'
                f'</div>'
            )
    return '\n\n'.join(parts)


def build_read_page(parsed, slug, color):
    meta   = parsed['meta']
    title  = meta.get('title', slug)
    note   = meta.get('note', '')
    script_html = render_script_html(parsed['script'])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Caveman Odyssey</title>
  <style>{READ_CSS}</style>
</head>
<body>

  <a class="back" href="../index.html">&#8592; all episodes</a>
  <a class="print-link" href="{slug}-print.html">puppet script &#9112;</a>

  <h1>{title}</h1>
  <p class="book-note">{note}</p>

{script_html}

  <div class="footer">Caveman Odyssey &mdash; after Homer &mdash; Ralph Hutchison</div>

  <script>
{chipsquirt_js(color)}
  </script>

</body>
</html>"""


# ── print page HTML ───────────────────────────────────────────────────────────

PRINT_CSS = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Georgia, "Times New Roman", serif; background: #fff;
           color: #111; font-size: 12pt; line-height: 1.55; }
    .screen-only { background: #fdfaf5; padding: 0.8rem 2rem; font-size: 0.78rem;
                   color: #aaa; border-bottom: 1px solid #e0d8cc; }
    .screen-only a { color: #888; text-decoration: none; }
    .screen-only a:hover { text-decoration: underline; }
    .page { max-width: 7in; margin: 0 auto; padding: 0.75in 0.8in 0.9in; }
    .title-block { border-bottom: 3px double #111; padding-bottom: 0.5rem;
                   margin-bottom: 1.2rem; }
    .title-block h1 { font-size: 18pt; font-weight: bold; margin-bottom: 0.15rem; }
    .title-block .sub { font-size: 10pt; font-style: italic; color: #444; }
    .cast { margin-bottom: 1.4rem; font-size: 10pt; }
    .cast h2 { font-size: 8pt; text-transform: uppercase; letter-spacing: 0.14em;
               margin-bottom: 0.5rem; color: #777; }
    .cast ul { list-style: none; }
    .cast li { margin-bottom: 0.2rem; }
    .cast .cname { font-weight: bold; }
    .cast .cdesc { color: #555; font-style: italic; }
    .scene-head { font-size: 8pt; text-transform: uppercase; letter-spacing: 0.14em;
                  color: #999; margin: 1.4rem 0 0.7rem; border-top: 1px solid #ddd;
                  padding-top: 0.6rem; }
    .line { display: flex; gap: 0.5rem; margin-bottom: 0.6rem; page-break-inside: avoid; }
    .line .who { font-weight: bold; font-size: 10.5pt; min-width: 1.5in; flex-shrink: 0;
                 text-align: right; padding-top: 0.05rem; color: #111; }
    .line .what { flex: 1; font-size: 10.5pt; }
    .stage { font-style: italic; color: #888; font-size: 9.5pt;
             margin: 0.8rem 0 0.8rem 1.5in; padding-left: 0.5rem;
             border-left: 1px solid #ddd; }
    .tips { margin-top: 1.8rem; border: 1px solid #bbb; padding: 0.65rem 0.8rem;
            font-size: 9.5pt; page-break-inside: avoid; }
    .tips h2 { font-size: 8pt; text-transform: uppercase; letter-spacing: 0.14em;
               margin-bottom: 0.45rem; color: #777; }
    .tips ul { padding-left: 1.1rem; }
    .tips li { margin-bottom: 0.3rem; }
    .footer-print { margin-top: 1.4rem; font-size: 8pt; color: #bbb;
                    border-top: 1px solid #ddd; padding-top: 0.4rem; text-align: center; }
    @media print {
      .screen-only { display: none; }
      @page { size: letter; margin: 0; }
      .page { padding: 0.65in 0.75in 0.75in; }
    }
"""

def render_script_print(script):
    parts = []
    for node in script:
        t = node['type']
        if t == 'scene_head':
            parts.append(f'<div class="scene-head">{node["text"]}</div>')
        elif t == 'break':
            pass  # print page uses scene-heads instead
        elif t == 'stage':
            parts.append(f'<div class="stage">{node["text"]}</div>')
        elif t == 'speech':
            name = node['name']
            role = f' <em>({node["role"]})</em>' if node['role'] else ''
            all_paras = node['paras']
            if not all_paras:
                continue
            # first paragraph on same line as name
            parts.append(
                f'<div class="line">'
                f'<span class="who">{name}</span>'
                f'<span class="what">{role}{all_paras[0]}</span>'
                f'</div>'
            )
            # continuation paragraphs indented under blank name
            for para in all_paras[1:]:
                parts.append(
                    f'<div class="line">'
                    f'<span class="who"></span>'
                    f'<span class="what">{para}</span>'
                    f'</div>'
                )
    return '\n'.join(parts)


def build_print_page(parsed, slug, color):
    meta  = parsed['meta']
    title = meta.get('title', slug)
    book  = meta.get('book', '')
    part  = meta.get('part', '')
    cast  = parsed['cast']
    tips  = parsed['tips']

    sub = f'Book {book}'
    if part:
        sub += f', Part {part}'
    sub += ' \u2014 a puppet script \u2014 after Homer'

    cast_items = ''.join(
        f'<li><span class="cname">{c["name"]}</span>'
        f'<span class="cdesc"> \u2014 {c["role"]}</span></li>'
        for c in cast
    )

    tips_items = ''.join(f'<li>{t}</li>' for t in tips)
    tips_html = ''
    if tips_items:
        tips_html = f'''
    <div class="tips">
      <h2>Puppet Show Tips</h2>
      <ul>{tips_items}</ul>
    </div>'''

    script_html = render_script_print(parsed['script'])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} \u2014 Puppet Script</title>
  <style>{PRINT_CSS}</style>
</head>
<body>
  <div class="screen-only">
    <a href="{slug}.html">\u2190 read version</a> &nbsp;|&nbsp;
    <a href="../index.html">all episodes</a> &nbsp;|&nbsp;
    <span>Ctrl+P to print</span>
  </div>
  <div class="page">
    <div class="title-block">
      <h1>Caveman Odyssey: {title}</h1>
      <p class="sub">{sub}</p>
    </div>
    <div class="cast">
      <h2>Puppets Needed</h2>
      <ul>{cast_items}</ul>
    </div>
{script_html}{tips_html}
    <div class="footer-print">
      Caveman Odyssey \u2014 after Homer \u2014 Ralph Hutchison \u2014 free to use and share
    </div>
  </div>
</body>
</html>"""


# ── main ─────────────────────────────────────────────────────────────────────

def build_file(src_path):
    src_path = Path(src_path)
    text = src_path.read_text(encoding='utf-8')
    parsed = parse(text)

    meta  = parsed['meta']
    slug  = meta.get('slug', src_path.stem)
    color = meta.get('color') or DEFAULT_COLORS.get(slug, 'amber')

    out_dir = src_path.parent.parent / 'episodes'
    out_dir.mkdir(exist_ok=True)

    read_path  = out_dir / f'{slug}.html'
    print_path = out_dir / f'{slug}-print.html'

    read_path.write_text(build_read_page(parsed, slug, color), encoding='utf-8')
    print_path.write_text(build_print_page(parsed, slug, color), encoding='utf-8')

    print(f'  {slug}: {read_path.name}  {print_path.name}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/build-episodes.py episodes-src/<file>.md ...')
        sys.exit(1)
    for arg in sys.argv[1:]:
        for path in Path().glob(arg) if '*' in arg else [Path(arg)]:
            build_file(path)
