import json
d=json.load(open('data.json'))
c=lambda k:sum(i['kind']==k for i in d['items'])
t=open('page.html').read().replace('__NSKILL__',str(c('skill'))).replace('__NPB__',str(c('playbook'))).replace('__NPR__',str(c('principle'))).replace('__VER__',d['version'])
t=t.replace('__DATA__',json.dumps(dict(items=d['items'],examples=d['examples']),ensure_ascii=False).replace('</','<\\/'))
open('/workspace/pstack-learn/index.html','w').write(t); print(len(t))
