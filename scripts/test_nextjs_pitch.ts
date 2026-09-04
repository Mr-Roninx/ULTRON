import { chromium } from 'playwright';
import { spawn, ChildProcess } from 'node:child_process';
import path from 'node:path';

async function waitForServer(url: string, maxRetries = 20): Promise<boolean> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const res = await fetch(url);
      if (res.ok) return true;
    } catch {
      // Waiting for server to start
    }
    await new Promise(r => setTimeout(r, 500));
  }
  return false;
}

async function testNextJsPitch() {
  console.log('🚀 Starting Next.js server on port 3005 for E2E test...');
  const nextProcess: ChildProcess = spawn('npx', ['next', 'start', '-p', '3005'], {
    cwd: path.resolve(process.cwd(), 'frontend'),
    shell: true,
    stdio: 'inherit',
  });

  const isUp = await waitForServer('http://localhost:3005/pitch');
  if (!isUp) {
    nextProcess.kill();
    throw new Error('Next.js server failed to respond on http://localhost:3005/pitch');
  }
  console.log('✓ Next.js server is UP on http://localhost:3005');

  const browser = await chromium.launch({ headless: true });

  try {
    // 1. Test /pitch Landing Page
    const page = await browser.newPage();
    console.log('🌐 Navigating to http://localhost:3005/pitch ...');
    await page.goto('http://localhost:3005/pitch', { waitUntil: 'domcontentloaded' });

    const title = await page.title();
    console.log(`✓ Landing Page Title: "${title}"`);

    // Verify Pipeline Tab Switching
    const stepBtns = await page.$$('button:has-text("Stage")');
    console.log(`✓ Found ${stepBtns.length} pipeline step buttons`);
    if (stepBtns.length >= 7) {
      await stepBtns[2].click();
      await page.waitForTimeout(200);
      const stageText = await page.textContent('h3');
      console.log(`✓ Clicked Stage 3 -> Active header: "${stageText}"`);
    }

    // Capture Landing Page
    const snapLanding = path.resolve(process.cwd(), 'Pitch', 'nextjs_pitch_landing.png');
    await page.screenshot({ path: snapLanding });
    console.log(`📸 Saved Next.js Pitch Landing Screenshot: ${snapLanding}`);

    // 2. Test /pitch/video Motion Graph Page (1920x1080 Viewport)
    console.log('🎬 Navigating to http://localhost:3005/pitch/video in 1920x1080...');
    const videoContext = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      deviceScaleFactor: 1,
    });
    const videoPage = await videoContext.newPage();
    await videoPage.goto('http://localhost:3005/pitch/video', { waitUntil: 'domcontentloaded' });

    // Assert Canvas Dimensions
    const canvasBox = await videoPage.$eval('#canvas-viewport', el => {
      const rect = el.getBoundingClientRect();
      return { width: rect.width, height: rect.height };
    });
    console.log(`✓ Next.js Canvas Dimensions: ${canvasBox.width}x${canvasBox.height}`);
    if (canvasBox.width !== 1920 || canvasBox.height !== 1080) {
      throw new Error(`Expected 1920x1080, got ${canvasBox.width}x${canvasBox.height}`);
    }

    // Verify Act 1
    const act1Active = await videoPage.$eval('#scene-act-1', el => el.classList.contains('active'));
    console.log(`✓ Next.js Act 1 initially active: ${act1Active}`);
    const snapVideo1 = path.resolve(process.cwd(), 'Pitch', 'nextjs_video_act1.png');
    await videoPage.screenshot({ path: snapVideo1 });
    console.log(`📸 Saved Next.js Video Act 1 Screenshot: ${snapVideo1}`);

    // Test Key '4' -> Act 4 (Decision Triad & Knapsack)
    await videoPage.keyboard.press('Digit4');
    await videoPage.waitForTimeout(500);
    const act4Active = await videoPage.$eval('#scene-act-4', el => el.classList.contains('active'));
    console.log(`✓ Pressed '4' -> Act 4 active: ${act4Active}`);
    if (!act4Active) throw new Error('Act 4 not active');
    const snapVideo4 = path.resolve(process.cwd(), 'Pitch', 'nextjs_video_act4.png');
    await videoPage.screenshot({ path: snapVideo4 });
    console.log(`📸 Saved Next.js Video Act 4 Screenshot: ${snapVideo4}`);

    // Test Key '6' -> Act 6 (Causal Truth & Ledger)
    await videoPage.keyboard.press('Digit6');
    await videoPage.waitForTimeout(500);
    const act6Active = await videoPage.$eval('#scene-act-6', el => el.classList.contains('active'));
    console.log(`✓ Pressed '6' -> Act 6 active: ${act6Active}`);
    if (!act6Active) throw new Error('Act 6 not active');
    const snapVideo6 = path.resolve(process.cwd(), 'Pitch', 'nextjs_video_act6.png');
    await videoPage.screenshot({ path: snapVideo6 });
    console.log(`📸 Saved Next.js Video Act 6 Screenshot: ${snapVideo6}`);

    // Test Restart Key 'R'
    await videoPage.keyboard.press('KeyR');
    await videoPage.waitForTimeout(300);
    const act1Reset = await videoPage.$eval('#scene-act-1', el => el.classList.contains('active'));
    console.log(`✓ Pressed 'R' -> Reset back to Act 1: ${act1Reset}`);

    console.log('🎉 All Next.js Pitch & Motion Video Tests PASSED completely!');
  } finally {
    await browser.close();
    if (nextProcess.pid) {
      spawn('taskkill', ['/PID', nextProcess.pid.toString(), '/T', '/F'], { shell: true });
    }
  }
}

testNextJsPitch().catch(err => {
  console.error('❌ Next.js test failed:', err);
  process.exit(1);
});
