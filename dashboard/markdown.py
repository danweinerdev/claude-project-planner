"""Minimal markdown to HTML conversion."""

import html
import re


def format_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def md_to_html(content: str) -> str:
    lines = content.split('\n')
    out = []
    in_code = False
    in_list = False

    for line in lines:
        if line.startswith('```'):
            if in_code:
                out.append('</code></pre>')
                in_code = False
            else:
                lang = line[3:].strip() or 'text'
                out.append(f'<pre><code class="language-{lang}">')
                in_code = True
            continue

        if in_code:
            out.append(html.escape(line))
            continue

        if in_list and not line.strip().startswith(('-', '*', '+')) and line.strip():
            out.append('</ul>')
            in_list = False

        if line.startswith('#### '):
            out.append(f'<h4>{format_inline(line[5:].strip())}</h4>')
        elif line.startswith('### '):
            out.append(f'<h3>{format_inline(line[4:].strip())}</h3>')
        elif line.startswith('## '):
            out.append(f'<h2>{format_inline(line[3:].strip())}</h2>')
        elif line.startswith('# '):
            out.append(f'<h1>{format_inline(line[2:].strip())}</h1>')
        elif line.strip().startswith(('-', '*', '+')) and len(line.strip()) > 1:
            if not in_list:
                out.append('<ul>')
                in_list = True
            item = line.strip()[2:].strip() if line.strip()[:2] in ('- ', '* ', '+ ') else line.strip()[1:].strip()
            item = re.sub(r'\[x\]', '<input type="checkbox" checked disabled>', item, flags=re.IGNORECASE)
            item = re.sub(r'\[ \]', '<input type="checkbox" disabled>', item)
            out.append(f'<li>{format_inline(item)}</li>')
        elif not line.strip():
            if in_list:
                out.append('</ul>')
                in_list = False
            out.append('')
        else:
            out.append(f'<p>{format_inline(line)}</p>')

    if in_list:
        out.append('</ul>')
    if in_code:
        out.append('</code></pre>')

    return '\n'.join(out)
