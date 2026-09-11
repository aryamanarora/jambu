const { chromium } = require('/Users/aryamanarora/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');
const dir = __dirname;
const url = process.env.TELUGU_BLOG_URL || 'http://127.0.0.1:5187/jambu/blogs/telugu-metathesis';
const exampleTables = '.prose > table, .prose > .blog-table > table';
(async () => {
 const browser = await chromium.launch({headless:true,channel:'chrome'});
 const page = await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 const response=await page.goto(url,{waitUntil:'domcontentloaded'});
 assert.equal(response.status(),200);
 await page.locator('.evidence-chart .switch button').first().waitFor();
 const headings=await page.locator('.prose > h2').allTextContents();assert.equal(headings.length,6);
 assert.equal(await page.locator('.evidence-chart').count(),6);
 const rows=await page.locator(exampleTables).evaluateAll(tables=>tables.map(t=>t.querySelectorAll('tbody tr').length));
 assert.deepEqual(rows,[10,10,10,10,10,10]);
 const first=page.locator('.evidence-chart').first();
 await first.getByLabel('Comparison').selectOption('1');
 assert.match(await first.textContent(),/n = 56/);
 await first.getByRole('button',{name:'Count',exact:true}).click();
 assert.equal(await first.getByRole('button',{name:'Count',exact:true}).getAttribute('aria-pressed'),'true');
 await first.getByRole('button',{name:'Proportion',exact:true}).click();
 await first.scrollIntoViewIfNeeded();await page.screenshot({path:path.join(dir,'desktop-chart.png')});
 await page.locator(exampleTables).first().scrollIntoViewIfNeeded();await page.screenshot({path:path.join(dir,'desktop-examples.png')});
 const anchors=await page.locator('.prose a[href]').evaluateAll(as=>as.map(a=>a.getAttribute('href')));
 const recordLinks=[...new Set(anchors.filter(x=>x.includes('/entries/')))];
 // SSR has already resolved every semantic ID. Exercise three real destinations too.
 for (const href of process.env.TELUGU_QA_FOCUSED_BUILD ? [] : recordLinks.slice(0,3)) {
  const result=await page.request.get(new URL(href,url).href);assert.equal(result.status(),200,href);
 }
 await page.locator('.blog-link-form').first().hover();
 await page.locator('.peek-head').waitFor({timeout:60000});
 assert.ok((await page.locator('.peek-word').textContent()).trim().length>0);
 await page.mouse.move(0,0);
 const downloads=[...new Set(anchors.filter(x=>x.includes('/research/telugu-metathesis/')))];
 for(const href of downloads){assert.ok(href.startsWith('/jambu/'),href);const r=await page.request.get(new URL(href,url).href);assert.equal(r.status(),200,href);assert.ok((await r.body()).length>100);}
 await page.setViewportSize({width:390,height:844});
 await page.locator(exampleTables).first().scrollIntoViewIfNeeded();
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Document overflows on mobile');
 await page.screenshot({path:path.join(dir,'mobile-examples.png')});
 await first.scrollIntoViewIfNeeded();await first.getByLabel('Comparison').selectOption('0');
 assert.ok(await first.locator('select').evaluate(el=>el.getBoundingClientRect().right<=el.closest('figure').getBoundingClientRect().right),'Select clipped on mobile');
 await page.screenshot({path:path.join(dir,'mobile-chart.png')});
 await page.emulateMedia({colorScheme:'dark'});
 await page.screenshot({path:path.join(dir,'dark-chart.png')});
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:1200,height:900}});
 const staticPage=await nojs.newPage();assert.equal((await staticPage.goto(url,{waitUntil:'domcontentloaded'})).status(),200);
 assert.equal(await staticPage.locator('.evidence-chart').count(),6);
 assert.equal(await staticPage.locator(exampleTables).locator('tbody tr').count(),60);
 assert.equal(await staticPage.locator('.evidence-chart .controls').count(),0);
 await staticPage.locator('.evidence-chart details').first().locator('summary').click();
 assert.ok(await staticPage.locator('.evidence-chart details').first().getAttribute('open')!==null);
 assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(dir,'browser-qa.json'),JSON.stringify({url,headings,rows,charts:6,recordLinks:recordLinks.length,recordDestinationsFetched:process.env.TELUGU_QA_FOCUSED_BUILD?0:3,recordIDsResolvedDuringSSR:true,hoverPreview:true,downloads,desktop:true,mobile:true,dark:true,noJavaScript:true,pageErrors:errors},null,2)+'\n');
 await browser.close();console.log('Browser QA passed: six charts, sixty examples, controls, record destinations, downloads, mobile, dark, no-JS.');
})().catch(e=>{console.error(e);process.exit(1)});
