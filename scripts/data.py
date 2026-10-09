import re, json, os, html
from md import render, strip_fm
P='/tmp/backend-plugin-t3ae4E/pstack'; S=P+'/skills'; PB=S+'/poteto-mode/playbooks'
readme=open(P+'/README.md').read()
names=sorted(os.listdir(S)); pbs=sorted(f[:-3] for f in os.listdir(PB))
GH='https://github.com/cursor/plugins/blob/main/pstack/'
def mklink(relfile):
    base=os.path.dirname(relfile)
    def f(url):
        if url.startswith('http'): return url
        if url.startswith('#'): return None
        r=link(url)
        if r: return r
        p=os.path.normpath(os.path.join(base,url.split('#')[0]))
        fp=os.path.join(P,p)
        return (GH.replace('/blob/','/tree/') if os.path.isdir(fp) else GH)+p if os.path.exists(fp) else None
    return f
def link(url):
    m=re.search(r'(?:^|/)(principle-[\w-]+|[\w-]+)/SKILL\.md$',url)
    if m and m.group(1) in names: return '#'+m.group(1)
    m=re.search(r'playbooks/([\w-]+)\.md$',url)
    if m and m.group(1) in pbs: return '#pb-'+m.group(1)
    if url.startswith('#'): return None
    return None
def fm(path):
    t=open(path).read(); y=re.match(r'---\n(.*?)\n---',t,re.S).group(1)
    d=re.search(r'^description:\s*(>-\n(?:\s+.*\n?)+|.*)$',y,re.M).group(1)
    if d.startswith('>-'): d=' '.join(l.strip() for l in d.splitlines()[1:])
    d=d.strip(); return json.loads(d) if d.startswith('"') else d
use={m.group(1):m.group(2) for m in re.finditer(r'^\| \[`/([\w-]+)`\]\([^)]*\) \| (.*) \|$',readme,re.M)}
prin={m.group(1):(m.group(2),m.group(3)) for m in re.finditer(r'^\| \[([\w-]+)\]\([^)]*\) \| (\w+) \| (.*) \|$',readme,re.M)}
pbfor={m.group(2).split('/')[-1][:-3]:(m.group(1),m.group(3)) for m in re.finditer(r'^\| \[([^\]]+)\]\((\./skills/poteto-mode/playbooks/[^)]+)\) \| (.*) \|$',readme,re.M)}
assert len(pbfor)==23, len(pbfor)
# verbatim example prompts: README examples block + guide ```text blocks
exblock=readme.split('all the examples')[1].split('</details>')[0]
rex=[(m.group(1).strip(),re.sub(r'\n\s+',' ',m.group(2)).strip()) for m in re.finditer(r'^([\w -]+):\s+(\S.*(?:\n {19}.*)*)',exblock,re.M)]
prompts=[p for _,p in rex]
G=P+'/docs/guide'
for f in sorted(os.listdir(G)):
    if f.endswith('.md'):
        for b in re.findall(r'```text\n(.*?)\n```',open(G+'/'+f).read(),re.S): prompts.append(b.strip())
prompts=list(dict.fromkeys(prompts))
def examples_for(cmd):
    return [p for p in prompts if p.split()[0]==cmd or p.split()[0]==cmd+','][:3]
cat={'poteto-mode':'Start here','poteto-help':'Start here','setup-pstack':'Start here',
 'how':'Understand','why':'Understand','teach':'Understand','recall':'Understand','blast-radius':'Understand',
 'architect':'Design','arena':'Design','swarm':'Design','interrogate':'Design','figure-it-out':'Design',
 'tdd':'Build & clean','unslop':'Build & clean','no-comments':'Build & clean','typescript-best-practices':'Build & clean','technical-writing':'Build & clean','bro':'Build & clean',
 'create-verification-skill':'Verify','maintain-verification-skill':'Verify','benchmark-checklist':'Verify','show-me-your-work':'Verify',
 'automate-me':'Make it yours','reflect':'Make it yours','correct':'Make it yours','make-bot-ui':'Make it yours'}
pbex={'bug-fix':'bug fix','perf-issue':'perf','feature':'feature','prototype':'prototype','multi-phase-plan':'multi-phase','babysit':'babysit','visual-parity':'visual parity'}
items=[]
for n in names:
    raw=open(f'{S}/{n}/SKILL.md').read(); d=fm(f'{S}/{n}/SKILL.md')
    body=render(raw,mklink(f'skills/{n}/SKILL.md'))
    if n.startswith('principle-'):
        k=n[10:]; g,rule=prin[k]
        title=re.search(r'^#\s+(.*)$',strip_fm(raw),re.M).group(1)
        items.append(dict(id=n,kind='principle',title=title,group=g.capitalize(),summary=rule,when=d.split('. ')[0].rstrip('.')+'.' if d.startswith('Apply') else '',ex=[],body=body,src=GH+f'skills/{n}/SKILL.md'))
    else:
        items.append(dict(id=n,kind='skill',title='/'+n,group=cat[n],summary=d,when=use[n],ex=list(dict.fromkeys([pr for lab,pr in rex if {'figure it out':'figure-it-out','help':'poteto-help'}.get(lab,lab)==n]+examples_for('/'+n)))[:3],body=body,src=GH+f'skills/{n}/SKILL.md'))
for p in pbs:
    raw=open(f'{PB}/{p}.md').read()
    title=re.search(r'^###\s+(.*)$',raw,re.M).group(1)
    tag=re.search(r'\*\*(.+?)\*\*',raw); tag=tag.group(1) if tag and raw.find('**')<raw.find('\n',raw.find('###'))+5 else ''
    ex=[pr for lab,pr in rex if pbex.get(p)==lab]
    items.append(dict(id='pb-'+p,kind='playbook',title=title,group='Playbook',summary=pbfor[p][1][:1].upper()+pbfor[p][1][1:],when=tag,ex=ex,body=render(raw,mklink(f'skills/poteto-mode/playbooks/{p}.md')),src=GH+f'skills/poteto-mode/playbooks/{p}.md'))
print(len(items),{k:sum(i['kind']==k for i in items) for k in ['skill','principle','playbook']})
print('skills w/o example:',[i['id'] for i in items if i['kind']=='skill' and not i['ex']])
bad=[(i['id'],m) for i in items for m in re.findall(r'.{20}(?:\*\*|\]\(|^#).{20}',i['body'],re.M)]
print('leftover md:',bad[:10])
from md import inline
for i in items:
    for k in ('summary','when'):
        s=i[k]; s=s[:1].upper()+s[1:] if s else s
        i[k+'H']=inline(s,lambda u:None)
    i['ex']=i['ex'][:2]
json.dump(dict(items=items,examples=rex,version=json.load(open(P+'/.cursor-plugin/plugin.json'))['version']),open('data.json','w'),ensure_ascii=False)
print(os.path.getsize('data.json'))
