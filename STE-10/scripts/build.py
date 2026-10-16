#!/usr/bin/env python3
"""
build.py — compile STE-10 prose sources into HTML episode pages and book index.

Source files:  <book>/episodes-src/ch{N}-ep{N}-<slug>.md
Output HTML:   <book>/episodes/ch{N}-ep{N}-<slug>.html
Book index:    <book>/index.html

Usage (run from STE-10/):
    python3 scripts/build.py book-01            # all episodes + index
    python3 scripts/build.py book-01/episodes-src/ch2-ep1-mentes-at-the-gate.md
"""

import html
import re
import sys
from pathlib import Path

# ── color families ─────────────────────────────────────────────────────────────

FAMILIES = {
    'amber':   dict(hc=36,  hd=8,  sat=75, lc=28, lr=8),
    'violet':  dict(hc=268, hd=14, sat=60, lc=26, lr=8),
    'teal':    dict(hc=172, hd=12, sat=70, lc=28, lr=8),
    'slate':   dict(hc=215, hd=8,  sat=40, lc=28, lr=8),
    'forest':  dict(hc=140, hd=10, sat=60, lc=25, lr=8),
    'magenta': dict(hc=312, hd=10, sat=65, lc=26, lr=8),
}

# ── CSS ────────────────────────────────────────────────────────────────────────

EPISODE_CSS = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html { font-size: 18px; }
    body {
      font-family: Georgia, "Times New Roman", serif;
      background: #fdfaf5;
      color: #1a1a1a;
      line-height: 1.85;
      max-width: 620px;
      margin: 0 auto;
      padding: 4rem 2rem 7rem;
    }
    nav { display: flex; justify-content: space-between; margin-bottom: 3.5rem; }
    nav a { font-size: 0.72rem; color: #bbb; text-decoration: none;
            letter-spacing: 0.06em; text-transform: uppercase; }
    nav a:hover { color: #555; }
    .chapter-tag { font-size: 0.72rem; color: #bbb; letter-spacing: 0.06em;
                   text-transform: uppercase; margin-bottom: 0.5rem; }
    h1 { font-size: 1.9rem; font-weight: normal; line-height: 1.2;
         margin-bottom: 0.35rem; letter-spacing: -0.01em; }
    .episode-note { font-size: 0.82rem; color: #bbb; font-style: italic;
                    margin-bottom: 3.5rem; }
    p { margin-bottom: 1.1rem; }
    .section-break { text-align: center; color: #ddd; margin: 2.5rem 0;
                     font-size: 0.9rem; letter-spacing: 0.5em; }
    .footer { margin-top: 6rem; font-size: 0.72rem; color: #ccc;
              border-top: 1px solid #ede8e0; padding-top: 2rem; }
"""

INDEX_CSS = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html { font-size: 18px; }
    body {
      font-family: Georgia, "Times New Roman", serif;
      background: #fdfaf5;
      color: #1a1a1a;
      line-height: 1.75;
      max-width: 680px;
      margin: 0 auto;
      padding: 4rem 2rem 7rem;
    }
    .back { font-size: 0.72rem; color: #bbb; text-decoration: none;
            letter-spacing: 0.06em; text-transform: uppercase;
            display: inline-block; margin-bottom: 3rem; }
    .back:hover { color: #555; }
    h1 { font-size: 2.1rem; font-weight: normal; line-height: 1.2;
         margin-bottom: 0.4rem; letter-spacing: -0.01em; }
    .book-note { font-size: 0.82rem; color: #bbb; font-style: italic;
                 margin-bottom: 4rem; }
    .chapter { margin-bottom: 3.5rem; }
    .chapter-heading { font-size: 0.72rem; color: #bbb; letter-spacing: 0.1em;
                       text-transform: uppercase; margin-bottom: 1.2rem;
                       padding-bottom: 0.6rem; border-bottom: 1px solid #ede8e0; }
    .chapter-title { font-size: 1.1rem; font-weight: normal; color: #555;
                     margin-bottom: 1rem; font-style: italic; }
    .episode-list { list-style: none; }
    .episode-list li { margin-bottom: 0.6rem; }
    .episode-list a { text-decoration: none; color: #1a1a1a; font-size: 1rem; }
    .episode-list a:hover { color: #888; }
    .ep-num { font-size: 0.72rem; color: #bbb; letter-spacing: 0.06em;
              margin-right: 0.5rem; text-transform: uppercase; }
    .ep-note { font-size: 0.78rem; color: #aaa; font-style: italic;
               display: block; padding-left: 3.2rem; margin-top: 0.1rem; }
    .footer { margin-top: 6rem; font-size: 0.72rem; color: #ccc;
              border-top: 1px solid #ede8e0; padding-top: 2rem; }
"""

# ── chipsquirt JS ──────────────────────────────────────────────────────────────

def chipsquirt_js(family_name):
    f = FAMILIES.get(family_name, FAMILIES['amber'])
    return (
        f"  (function(){{\n"
        f"    var fam={{hc:{f['hc']},hd:{f['hd']},sat:{f['sat']},lc:{f['lc']},lr:{f['lr']}}};\n"
        r"    function hsvToRgb(h,s,v){h=((h%360)+360)%360;var c=v*s,x=c*(1-Math.abs((h/60)%2-1)),m=v-c,r,g,b;if(h<60){r=c;g=x;b=0;}else if(h<120){r=x;g=c;b=0;}else if(h<180){r=0;g=c;b=x;}else if(h<240){r=0;g=x;b=c;}else if(h<300){r=x;g=0;b=c;}else{r=c;g=0;b=x;}return[Math.round((r+m)*255),Math.round((g+m)*255),Math.round((b+m)*255)];}"
        "\n"
        r"    function lc(i,p){var P=1.6180339887,P2=2.6180339887,fr=0.45;var h=((fam.hc+fam.hd*Math.sin(i*fr+p))%360+360)%360;var s=Math.max(0,Math.min(1,fam.sat/100+0.18*Math.sin(i*fr*P+p+1.1)));var v=Math.max(0.08,Math.min(0.60,0.30+0.18*Math.sin(i*fr*P2+p+2.3)));return'rgb('+hsvToRgb(h,s,v)+')';}"
        "\n"
        r"    function colorize(el){var p=Math.random()*Math.PI*2,i=0,w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT),ns=[],n;while((n=w.nextNode()))ns.push(n);ns.forEach(function(node){var f=document.createDocumentFragment();for(var ci=0;ci<node.nodeValue.length;ci++){var ch=node.nodeValue[ci];if(/[ \t\n\r]/.test(ch)){f.appendChild(document.createTextNode(ch));}else{var sp=document.createElement('span');sp.style.color=lc(i++,p);sp.textContent=ch;f.appendChild(sp);}}node.parentNode.replaceChild(f,node);});}"
        "\n"
        r"    document.addEventListener('DOMContentLoaded',function(){document.querySelectorAll('h1').forEach(function(el){colorize(el);});});"
        "\n"
        "  })();"
    )

# ── parser ─────────────────────────────────────────────────────────────────────

def parse(text):
    """
    Parse frontmatter + prose body.
    Returns (meta dict, blocks list).
    Each block is {'type': 'para', 'text': str} or {'type': 'break'}.
    """
    lines = text.splitlines()
    idx = 0
    meta = {}

    if lines and lines[idx].strip() == '---':
        idx += 1
        while idx < len(lines) and lines[idx].strip() != '---':
            if ':' in lines[idx]:
                k, _, v = lines[idx].partition(':')
                meta[k.strip()] = v.strip()
            idx += 1
        idx += 1

    body = '\n'.join(lines[idx:])
    raw_blocks = re.split(r'\n{2,}', body.strip())

    blocks = []
    for block in raw_blocks:
        stripped = block.strip()
        if not stripped:
            continue
        if stripped == '---':
            blocks.append({'type': 'break'})
        else:
            # collapse soft-wrapped lines in source
            joined = ' '.join(line.strip() for line in stripped.splitlines() if line.strip())
            blocks.append({'type': 'para', 'text': joined})

    return meta, blocks

# ── HTML rendering ─────────────────────────────────────────────────────────────

def render_body(blocks):
    parts = []
    for block in blocks:
        if block['type'] == 'break':
            parts.append('<div class="section-break">&middot; &middot; &middot;</div>')
        else:
            parts.append(f'<p>{html.escape(block["text"])}</p>')
    return '\n\n'.join(parts)


def build_episode_html(meta, blocks, prev_ep, next_ep):
    color        = meta.get('color', 'amber')
    chapter_num  = meta.get('chapter', '')
    episode_num  = meta.get('episode', '')
    title        = meta.get('title', '')
    note         = meta.get('note', '')

    tag = f'Chapter {chapter_num} \u00b7 Episode {chapter_num}.{episode_num}'

    if prev_ep:
        prev_href  = f'{prev_ep["slug"]}.html'
        prev_label = html.escape(prev_ep['meta'].get('title', ''))
        nav_left   = f'<a href="{prev_href}">&#8592; {prev_label}</a>'
    else:
        nav_left   = '<a href="../index.html">&#8592; Book I</a>'

    if next_ep:
        next_href  = f'{next_ep["slug"]}.html'
        next_label = html.escape(next_ep['meta'].get('title', ''))
        nav_right  = f'<a href="{next_href}">{next_label} &#8594;</a>'
    else:
        nav_right  = '<a href="../index.html">&#8592; Book I</a>'

    body_html = render_body(blocks)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} \u2014 Very Small Homer</title>
  <style>{EPISODE_CSS}</style>
</head>
<body>

  <nav>
    {nav_left}
    {nav_right}
  </nav>

  <p class="chapter-tag">{tag}</p>
  <h1>{html.escape(title)}</h1>
  <p class="episode-note">{html.escape(note)}</p>

{body_html}

  <div class="footer">Very Small Homer &mdash; after Homer &mdash; STE-10</div>

  <script>
{chipsquirt_js(color)}
  </script>

</body>
</html>"""


def build_index_html(book_dir, episodes):
    """Build the book index page from a list of episode metadata dicts."""
    book_note = ''
    if episodes:
        # use the note from the book config if present, else first episode context
        pass

    # group by chapter
    chapters = {}
    for ep in episodes:
        ch = int(ep['meta'].get('chapter', 0))
        chapters.setdefault(ch, []).append(ep)

    chapters_html = ''
    for ch_num in sorted(chapters):
        eps = sorted(chapters[ch_num], key=lambda e: int(e['meta'].get('episode', 0)))
        ch_title = eps[0]['meta'].get('chapter_title', f'Chapter {ch_num}')

        items = ''
        for ep in eps:
            m = ep['meta']
            ep_num  = m.get('episode', '')
            title   = html.escape(m.get('title', ''))
            note    = html.escape(m.get('note', ''))
            slug    = ep['slug']
            items += (
                f'      <li>\n'
                f'        <a href="episodes/{slug}.html">\n'
                f'          <span class="ep-num">{ch_num}.{ep_num}</span>{title}\n'
                f'        </a>\n'
                f'        <span class="ep-note">{note}</span>\n'
                f'      </li>\n'
            )

        chapters_html += (
            f'  <div class="chapter">\n'
            f'    <p class="chapter-heading">Chapter {ch_num}</p>\n'
            f'    <p class="chapter-title">{html.escape(ch_title)}</p>\n'
            f'    <ul class="episode-list">\n'
            f'{items}'
            f'    </ul>\n'
            f'  </div>\n\n'
        )

    # read book-level note from book.cfg if present
    book_cfg = book_dir / 'book.cfg'
    book_title = book_dir.name.replace('-', ' ').title()
    book_subtitle = ''
    if book_cfg.exists():
        for line in book_cfg.read_text().splitlines():
            if line.startswith('title:'):
                book_title = line.partition(':')[2].strip()
            if line.startswith('note:'):
                book_subtitle = line.partition(':')[2].strip()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(book_title)} \u2014 Very Small Homer / STE-10</title>
  <style>{INDEX_CSS}</style>
</head>
<body>

  <a class="back" href="../../index.html">&#8592; Very Small Homer</a>

  <h1>{html.escape(book_title)}</h1>
  <p class="book-note">{html.escape(book_subtitle)}</p>

{chapters_html}
  <div class="footer">Very Small Homer &mdash; after Homer &mdash; STE-10</div>

  <script>
{chipsquirt_js('amber')}
  </script>

</body>
</html>"""

# ── file I/O ───────────────────────────────────────────────────────────────────

def load_episode(src_path):
    src_path = Path(src_path)
    text = src_path.read_text(encoding='utf-8')
    meta, blocks = parse(text)
    slug = src_path.stem
    return {'slug': slug, 'meta': meta, 'blocks': blocks, 'src': src_path}


def build_one(ep, prev_ep, next_ep, out_dir):
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f'{ep["slug"]}.html'
    content = build_episode_html(ep['meta'], ep['blocks'], prev_ep, next_ep)
    out_path.write_text(content, encoding='utf-8')
    print(f'  {ep["slug"]}.html')


def build_book(book_dir):
    book_dir = Path(book_dir)
    src_dir  = book_dir / 'episodes-src'
    out_dir  = book_dir / 'episodes'

    src_files = sorted(src_dir.glob('*.md'))
    if not src_files:
        print(f'No .md files found in {src_dir}')
        return

    episodes = [load_episode(f) for f in src_files]

    # sort by (chapter, episode)
    def ep_key(e):
        m = e['meta']
        return (int(m.get('chapter', 0)), int(m.get('episode', 0)))

    episodes.sort(key=ep_key)

    for i, ep in enumerate(episodes):
        prev_ep = episodes[i - 1] if i > 0 else None
        next_ep = episodes[i + 1] if i < len(episodes) - 1 else None
        build_one(ep, prev_ep, next_ep, out_dir)

    index_path = book_dir / 'index.html'
    index_path.write_text(build_index_html(book_dir, episodes), encoding='utf-8')
    print(f'  index.html')


# ── main ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/build.py book-01')
        print('       python3 scripts/build.py book-01/episodes-src/ch1-ep1-the-muse.md')
        sys.exit(1)

    arg = Path(sys.argv[1])

    if arg.is_dir():
        build_book(arg)
    elif arg.suffix == '.md':
        # single-file mode: build just this episode, no index, no prev/next
        ep = load_episode(arg)
        out_dir = arg.parent.parent / 'episodes'
        build_one(ep, None, None, out_dir)
    else:
        print(f'Unknown argument: {arg}')
        sys.exit(1)
