const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  const consoleLogs = [];
  const failedRequests = [];

  page.on('console', msg => {
    consoleLogs.push(`[${msg.type()}] ${msg.text()}`);
  });
  page.on('pageerror', err => {
    errors.push(err.toString());
  });
  page.on('requestfailed', request => {
    failedRequests.push(`${request.url()} - ${request.failure().errorText}`);
  });

  await page.goto('http://localhost:5173/register', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);

  const rootHTML = await page.evaluate(() => document.getElementById('root')?.innerHTML || 'EMPTY');

  console.log('=== CONSOLE LOGS ===');
  consoleLogs.forEach(l => console.log(l));
  console.log('\n=== PAGE ERRORS ===');
  errors.forEach(e => console.log(e));
  console.log('\n=== FAILED REQUESTS ===');
  failedRequests.forEach(r => console.log(r));
  console.log('\n=== ROOT INNER HTML ===');
  console.log(rootHTML.substring(0, 2000));

  await browser.close();
})();
