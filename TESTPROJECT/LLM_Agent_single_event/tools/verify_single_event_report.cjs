// Browser QA for the local generated report. No external website or API access.
const { chromium } = require('playwright');
const { pathToFileURL } = require('node:url');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
(async () => {
  const report = path.resolve(process.argv[2]);
  const output = path.resolve(process.argv[3]); fs.mkdirSync(output, { recursive: true });
  const installed = ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Google/Chrome/Application/chrome.exe'].find(p => fs.existsSync(p));
  const browser = await chromium.launch({ headless: true, ...(installed ? {executablePath: installed} : {}) });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
    const errors = []; page.on('pageerror', e => errors.push(e.message));
    const external = [];
    page.on('request', r => { if (!r.url().startsWith('file:')) external.push(r.url()); });
    await page.goto(pathToFileURL(report).href, { waitUntil: 'load' });
    await page.locator('#overall path').first().waitFor();
    assert.match(await page.locator('#mode').innerText(), /离线流程演示/);
    assert.equal(await page.locator('#agent option').count(), 582);
    await page.locator('#round').fill('20'); await page.locator('#round').dispatchEvent('input');
    assert.match(await page.locator('#channels').innerText(), /政府直接投送：40次/);
    await page.locator('#round').fill('19'); await page.locator('#round').dispatchEvent('input');
    assert.match(await page.locator('#channels').innerText(), /政府直接投送：0次/);
    await page.locator('#round').fill('20'); await page.locator('#round').dispatchEvent('input');
    // Select a directly treated user and verify actual exposure and its source cue.
    const treated = await page.locator('#simulation-data').evaluate(el => JSON.parse(el.textContent).policy.recipients[0]);
    await page.locator('#agent').selectOption(treated);
    assert.match(await page.locator('#decision').innerText(), /GOV/);
    const details = page.locator('#decision details');
    for (let i=0; i<await details.count(); i++) await details.nth(i).locator('summary').click();
    assert.match(await page.locator('#decision').innerText(), /最近10条/);
    await page.screenshot({ path: path.join(output, 'report_desktop.png'), fullPage: true });
    await page.locator('#play').click(); await page.waitForTimeout(850); await page.locator('#play').click();
    assert(Number(await page.locator('#round').inputValue()) > 20);
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: path.join(output, 'report_mobile.png'), fullPage: true });
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    assert.equal(overflow, false); assert.deepEqual(errors, []); assert.deepEqual(external, []);
    const result = { passed: true, agent_options: 582, government_direct_at_20: 40,
      no_government_at_19: true, round_slider: true, agent_selection: true,
      source_cue_visible: true, autoplay: true, mobile_overflow: false,
      javascript_errors: errors, external_requests: external };
    fs.writeFileSync(path.join(output, 'browser_qa.json'), JSON.stringify(result, null, 2));
    console.log(JSON.stringify(result));
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
