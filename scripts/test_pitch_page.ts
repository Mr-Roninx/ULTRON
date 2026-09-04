import { chromium } from 'playwright';
import path from 'node:path';

async function verifyPitch() {
  console.log('🚀 Launching Playwright Chromium to test Pitch landing page...');
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const filePath = 'file:///' + path.resolve(process.cwd(), 'Pitch', 'index.html').replace(/\\/g, '/');
  console.log(`🌐 Navigating to: ${filePath}`);
  
  await page.goto(filePath, { waitUntil: 'domcontentloaded' });

  // 1. Verify Title & Header
  const title = await page.title();
  console.log(`✓ Page Title: "${title}"`);
  if (!title.includes('ULTRON')) throw new Error('Title does not contain ULTRON');

  // 2. Verify Hero Elements
  const heroBtn = await page.$('#hero-pitch-btn');
  if (!heroBtn) throw new Error('#hero-pitch-btn not found');
  console.log('✓ Hero pitch button found');

  // 3. Verify Audio Dock & Caption Bar
  const captionText = await page.$eval('#caption-text', el => el.textContent);
  console.log(`✓ Initial Caption: "${captionText?.slice(0, 50)}..."`);
  if (!captionText) throw new Error('Caption bar empty');

  // 4. Verify Interactive ROI Calculator
  const netRecInitial = await page.$eval('#res-net-rec', el => el.textContent);
  console.log(`✓ Initial Calculator Net Recovered: ${netRecInitial}`);

  // Move GMV slider to 200
  await page.$eval('#calc-gmv', (el: any) => {
    el.value = 200;
    el.dispatchEvent(new Event('input'));
  });
  const netRecUpdated = await page.$eval('#res-net-rec', el => el.textContent);
  console.log(`✓ Updated Calculator Net Recovered (GMV=200L): ${netRecUpdated}`);
  if (netRecInitial === netRecUpdated) throw new Error('Calculator did not update dynamically');

  // 5. Verify Pipeline Explorer Tab Switching
  const initialStageTitle = await page.$eval('#pipe-stage-title', el => el.textContent);
  console.log(`✓ Initial Pipeline Stage: "${initialStageTitle}"`);
  
  const stepBtns = await page.$$('.pipeline-step-btn');
  console.log(`✓ Found ${stepBtns.length} pipeline step buttons`);
  if (stepBtns.length < 7) throw new Error('Expected 7 pipeline steps');

  // Click stage 3
  await stepBtns[2].click();
  const stage3Title = await page.$eval('#pipe-stage-title', el => el.textContent);
  console.log(`✓ Switched to Stage 3: "${stage3Title}"`);
  if (!stage3Title?.includes('Stage 3')) throw new Error('Pipeline stage did not switch');

  // 6. Verify Scenario Decision Tester
  const scenarioSelect = await page.$('#scenario-select');
  if (scenarioSelect) {
    await scenarioSelect.selectOption('1'); // Stolen Card
    const verdict = await page.$eval('#scenario-decision', el => el.textContent);
    console.log(`✓ Scenario B Verdict: "${verdict?.trim()}"`);
    if (!verdict?.includes('ABSTAIN / BLOCKED')) throw new Error('Scenario decision mismatch');
  }

  // 7. Verify Transcript Modal
  await page.click('#btn-open-transcript');
  const modalVisible = await page.$eval('#transcript-modal', el => el.classList.contains('open'));
  console.log(`✓ Transcript Modal Open: ${modalVisible}`);
  if (!modalVisible) throw new Error('Transcript modal did not open');

  const actsInModal = await page.$$('.transcript-act');
  console.log(`✓ Transcript contains ${actsInModal.length} acts`);
  if (actsInModal.length !== 6) throw new Error('Expected 6 acts in transcript');

  await page.click('#btn-close-transcript');
  const modalClosed = await page.$eval('#transcript-modal', el => !el.classList.contains('open'));
  console.log(`✓ Transcript Modal Closed: ${modalClosed}`);

  // Take screenshots
  const heroScreenshot = path.resolve(process.cwd(), 'Pitch', 'pitch_hero.png');
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: heroScreenshot, fullPage: false });
  console.log(`📸 Saved hero screenshot to: ${heroScreenshot}`);

  const fullScreenshot = path.resolve(process.cwd(), 'Pitch', 'pitch_full.png');
  await page.screenshot({ path: fullScreenshot, fullPage: true });
  console.log(`📸 Saved full screenshot to: ${fullScreenshot}`);

  await browser.close();
  console.log('🎉 All Pitch landing page checks PASSED successfully!');
}

verifyPitch().catch(err => {
  console.error('❌ Verification failed:', err);
  process.exit(1);
});
