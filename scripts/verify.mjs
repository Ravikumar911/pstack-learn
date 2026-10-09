import puppeteer from 'puppeteer-core';
import fs from 'fs';
const URL=process.argv[2]||'http://localhost:8787/';
const data=JSON.parse(fs.readFileSync('data.json','utf8'));
const ids=data.items.map(i=>i.id);
const b=await puppeteer.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const errs=[];let fail=0;const ok=(c,m)=>{console.log((c?'PASS ':'FAIL ')+m);if(!c)fail++};
for(const [name,vp,scheme] of [['desktop',{width:1280,height:900},'light'],['phone',{width:390,height:844,isMobile:true,deviceScaleFactor:2},'dark']]){
 const ctx=await b.createBrowserContext();const p=await ctx.newPage();await p.setViewport(vp);await p.emulateMediaFeatures([{name:'prefers-color-scheme',value:scheme}]);
 p.on('console',m=>{if(['error','warning'].includes(m.type()))errs.push(`${name}: ${m.text()}`)});p.on('pageerror',e=>errs.push(`${name}: ${e.message}`));
 p.on('requestfailed',r=>errs.push(`${name}: failed ${r.url()}`));
 await p.goto(URL,{waitUntil:'networkidle0'});
 const cards=await p.$$eval('#cards article',a=>a.map(x=>x.id));
 ok(cards.length===74&&ids.every(i=>cards.includes(i)),`${name}: all ${cards.length}/74 cards present`);
 const ov=await p.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
 ok(ov<=0,`${name}: no horizontal overflow (${ov}px)`);
 const bg=await p.evaluate(()=>getComputedStyle(document.body).backgroundColor);ok(scheme==='dark'?bg==='rgb(17, 17, 17)':bg!=='rgb(17, 17, 17)',`${name}: ${scheme} scheme bg ${bg}`);
 const hero=await p.$eval('#start .start',e=>e.getBoundingClientRect().bottom);ok(name==='phone'||hero<vp.height,`${name}: three start commands above the fold (bottom ${Math.round(hero)}px)`);
 if(name==='desktop'){
  for(const a of await p.$$eval('nav a',x=>x.map(y=>y.getAttribute('href')))) ok(await p.$(a)!==null,`nav anchor ${a} exists`);
  await p.type('#q','perf');let n=await p.$$eval('#cards article',a=>a.length);ok(n>0&&n<74,`search "perf" -> ${n} cards`);
  await p.$eval('#q',e=>{e.value='';e.dispatchEvent(new Event('input'))});
  await p.click('[data-k=principle]');n=await p.$$eval('#cards article',a=>a.length);ok(n===24,`Principles filter -> ${n}`);
  await p.click('[data-g=Verification]');n=await p.$$eval('#cards article',a=>a.length);ok(n===5,`Principles·Verification -> ${n}`);
  await p.click('[data-k=playbook]');n=await p.$$eval('#cards article',a=>a.length);ok(n===23,`Playbooks filter -> ${n}`);
  await p.click('[data-k=all]');
  await p.click('.more[data-id="pb-bug-fix"]');const bt=await p.$eval('#pb-bug-fix .body',e=>e.innerText);ok(/Reproduce it yourself/.test(bt),'expand bug-fix playbook shows real steps');
  const theme0=await p.evaluate(()=>getComputedStyle(document.body).backgroundColor);await p.click('#theme');const theme1=await p.evaluate(()=>getComputedStyle(document.body).backgroundColor);ok(theme0!==theme1,`theme toggle ${theme0} -> ${theme1}`);
  await p.click('#theme');
  // every in-body anchor resolves via hash routing
  const hrefs=[...new Set(data.items.flatMap(i=>[...i.body.matchAll(/href="#([^"]+)"/g)].map(m=>m[1])))];
  const bad=hrefs.filter(h=>!ids.includes(h));ok(bad.length===0,`${hrefs.length} in-body cross-links all resolve (${bad.join(',')})`);
  await p.goto('about:blank');await p.goto(URL+'#principle-prove-it-works',{waitUntil:'networkidle0'});await new Promise(r=>setTimeout(r,300));
  const st=await p.evaluate(()=>{const e=document.getElementById('principle-prove-it-works');const r=e.getBoundingClientRect();return {open:e.classList.contains('open'),top:r.top}});
  ok(st.open&&st.top>=0&&st.top<900,`deep link #principle-prove-it-works opens and scrolls (top ${Math.round(st.top)})`);
  await p.click('#principle-prove-it-works .body a[href="#principle-show-me-your-work"], #principle-prove-it-works .body a').catch(()=>{});
  // quiz
  await p.goto('about:blank');await p.goto(URL,{waitUntil:'networkidle0'});await p.screenshot({path:'/workspace/pstack-learn/preview.png'});await p.click('#qz .qq[data-n="0"] input[value="0"]');ok(await p.$eval('#score',e=>e.textContent)==='1','quiz scores a right answer');
 } else await p.screenshot({path:'/workspace/pstack-v2/phone.png'});
 await ctx.close();
}
ok(errs.length===0,`console errors/warnings: ${errs.length} ${errs.join(' | ')}`);
await b.close();console.log(fail?`${fail} FAILED`:'ALL PASS');process.exit(fail?1:0);
