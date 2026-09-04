import { chromium } from 'playwright';
import path from 'node:path';

async function verifyVideoPitch() {
  console.log('🚀 Launching Playwright Chromium in 1920x1080 for Video Pitch test...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();

  const filePath = 'file:///' + path.resolve(process.cwd(), 'Pitch', 'video.html').replace(/\\/g, '/');
  console.log(`🌐 Navigating to: ${filePath}`);

  await page.goto(filePath, { waitUntil: 'domcontentloaded' });

  // 1. Verify Title
  const title = await page.title();
  console.log(`✓ Video Page Title: "${title}"`);
  if (!title.includes('ULTRON')) throw new Error('Title does not match');

  // 2. Check Canvas Frame Dimensions
  const canvasBox = await page.$eval('#canvas-frame', el => {
    const rect = el.getBoundingClientRect();
    return { width: rect.width, height: rect.height };
  });
  console.log(`✓ Canvas Dimensions: ${canvasBox.width}x${canvasBox.height}`);
  if (canvasBox.width !== 1920 || canvasBox.height !== 1080) {
    throw new Error(`Expected 1920x1080, got ${canvasBox.width}x${canvasBox.height}`);
  }

  const scene0Rect = await page.$eval('#scene-0', el => {
    const r = el.getBoundingClientRect();
    const cs = window.getComputedStyle(el);
    return { 
      rect: { x: r.x, y: r.y, w: r.width, h: r.height },
      display: cs.display,
      opacity: cs.opacity,
      visibility: cs.visibility,
      color: cs.color,
      zIndex: cs.zIndex,
      innerHTML: el.innerHTML.slice(0, 100)
    };
  });
  console.log('Scene 0 computed:', JSON.stringify(scene0Rect, null, 2));

  await page.waitForTimeout(600);

  // Capture Scene 0 (Hook)
  const snap0 = path.resolve(process.cwd(), 'Pitch', 'video_scene_0_hook.png');
  await page.screenshot({ path: snap0 });
  console.log(`📸 Saved Scene 0 screenshot: ${snap0}`);

  // Capture Scene 1 (Problem @ 25s)
  for (let i = 0; i < 5; i++) {
    await page.keyboard.press('ArrowRight');
  }
  await page.waitForTimeout(600);
  const snap1 = path.resolve(process.cwd(), 'Pitch', 'video_scene_1_problem.png');
  await page.screenshot({ path: snap1 });
  console.log(`📸 Saved Scene 1 screenshot: ${snap1}`);

  // Capture Scene 4 (Decision Triad @ 90s)
  for (let i = 0; i < 13; i++) {
    await page.keyboard.press('ArrowRight');
  }
  await page.waitForTimeout(600);
  const snap4 = path.resolve(process.cwd(), 'Pitch', 'video_scene_4_triad.png');
  await page.screenshot({ path: snap4 });
  console.log(`📸 Saved Scene 4 Triad screenshot: ${snap4}`);

  // Let's jump to Scene 5 (Tech Stack @ 210s)
  for (let i = 0; i < 28; i++) {
    await page.keyboard.press('ArrowRight');
  }
  await page.waitForTimeout(600);

  const scene9Active = await page.$eval('#scene-9', el => el.classList.contains('active'));
  console.log(`✓ Jumped to Tech Stack (Scene 9 active): ${scene9Active}`);

  const snap9 = path.resolve(process.cwd(), 'Pitch', 'video_scene_5_tech.png');
  await page.screenshot({ path: snap9 });
  console.log(`📸 Saved Scene 5 Tech screenshot: ${snap9}`);

  // Test 'R' to restart
  await page.keyboard.press('KeyR');
  await page.waitForTimeout(200);

  const scene0Restored = await page.$eval('#scene-0', el => el.classList.contains('active'));
  console.log(`✓ Pressed 'R' -> Reset back to Scene 0: ${scene0Restored}`);
  if (!scene0Restored) throw new Error('Reset failed');

  await browser.close();
  console.log('🎉 1920x1080 Video Pitch Verification PASSED completely!');
}

verifyVideoPitch().catch(err => {
  console.error('❌ Video pitch test failed:', err);
  process.exit(1);
});
