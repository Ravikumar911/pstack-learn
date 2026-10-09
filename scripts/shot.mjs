import puppeteer from 'puppeteer-core';
const b=await puppeteer.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const p=await b.newPage();await p.setViewport({width:1280,height:1000});
for(const id of ['setup-pstack','pb-multi-phase-plan']){await p.goto('about:blank');await p.goto('http://localhost:8787/#'+id,{waitUntil:'networkidle0'});await new Promise(r=>setTimeout(r,300));await p.screenshot({path:`/workspace/pstack-v2/${id}.png`});}
await p.goto('about:blank');await p.goto('http://localhost:8787/',{waitUntil:'networkidle0'});await p.$eval('#catalog',e=>e.scrollIntoView({behavior:'instant'}));await p.screenshot({path:'/workspace/pstack-v2/catalog.png'});
await b.close();
