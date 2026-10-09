import re, html
def strip_fm(t):
    if t.startswith('---\n'):
        e=t.find('\n---',4); return t[e+4:].lstrip('\n')
    return t
LINKMAP=None  # function(url)->href or None
def inline(s, link):
    codes=[]
    def keep(m):
        codes.append('<code>'+html.escape(m.group(1))+'</code>'); return f'\x00{len(codes)-1}\x00'
    s=re.sub(r'`([^`]+)`',keep,s)
    s=html.escape(s,quote=False)
    def lk(m):
        text,url=m.group(1),m.group(2)
        href=link(html.unescape(url))
        return f'<a href="{html.escape(href)}">{text}</a>' if href else text
    s=re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)',lk,s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
    s=re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])',r'<em>\1</em>',s)
    s=re.sub(r'\x00(\d+)\x00',lambda m:codes[int(m.group(1))],s)
    return s
LI=re.compile(r'^(\s*)([-*]|\d+\.)\s+(.*)$')
def render(text, link, drop_h1=True, hshift=2):
    lines=strip_fm(text).split('\n'); out=[]; i=0; para=[]
    def flush():
        if para: out.append('<p>'+inline(' '.join(x.strip() for x in para),link)+'</p>'); para.clear()
    while i<len(lines):
        l=lines[i]
        if l.strip().startswith('```'):
            flush(); j=i+1; buf=[]
            while j<len(lines) and not lines[j].strip().startswith('```'): buf.append(lines[j]); j+=1
            out.append('<pre><code>'+html.escape('\n'.join(buf))+'</code></pre>'); i=j+1; continue
        m=re.match(r'^(#{1,6})\s+(.*)',l)
        if m:
            flush(); n=len(m.group(1))
            if not(drop_h1 and not any(o.startswith('<h') or o.startswith('<p') for o in out) and n<=3 and not out):
                out.append(f'<h{min(6,n+hshift)}>'+inline(m.group(2),link)+f'</h{min(6,n+hshift)}>')
            i+=1; continue
        if l.startswith('|'):
            flush(); rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',c) for c in cells): rows.append(cells)
                i+=1
            t='<div class="tw"><table>'
            for k,r in enumerate(rows):
                tag='th' if k==0 else 'td'; t+='<tr>'+''.join(f'<{tag}>{inline(c,link)}</{tag}>' for c in r)+'</tr>'
            out.append(t+'</table></div>'); continue
        if LI.match(l):
            flush(); items=[]  # (indent, ordered, text)
            while i<len(lines):
                m=LI.match(lines[i])
                if m: items.append([len(m.group(1)), m.group(2)[0].isdigit(), m.group(3)]); i+=1
                elif lines[i].strip() and lines[i].startswith((' ','\t')) and items: items[-1][2]+=' \n'+lines[i].strip(); i+=1
                elif not lines[i].strip() and i+1<len(lines) and (LI.match(lines[i+1]) or (lines[i+1].startswith('  ') and lines[i+1].strip())): i+=1
                else: break
            out.append(build_list(items,link)); continue
        if not l.strip(): flush(); i+=1; continue
        if re.match(r'^\s*<(/?details|/?summary)',l): i+=1; continue
        para.append(l); i+=1
    flush(); return '\n'.join(out)
def build_list(items,link):
    res=[]; stack=[]
    for ind,ordered,txt in items:
        while stack and ind<stack[-1][0]: res.append('</li></%s>'%stack.pop()[1])
        if not stack or ind>stack[-1][0]:
            tag='ol' if ordered else 'ul'; stack.append((ind,tag)); res.append(f'<{tag}><li>')
        else: res.append('</li><li>')
        parts=txt.split(' \n'); body=inline(parts[0],link)
        for p in parts[1:]: body+='<br>'+inline(p,link)
        res.append(body)
    while stack: res.append('</li></%s>'%stack.pop()[1])
    return ''.join(res)
