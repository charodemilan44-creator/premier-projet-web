// Usage: node render.js preview 1.5 4 ...   |   node render.js full
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const { spawn } = require('child_process');
const path = require('path');
(async () => {
  const [mode, ...times] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.resolve(__dirname, 'scene.html'));
  await page.evaluate(() => document.fonts.ready);
  const frame = async t => {
    await page.evaluate(async t => {
      render(t);
      await Promise.all([...document.images].map(i => i.decode().catch(() => {})));
    }, t);
  };
  if (mode === 'preview') {
    for (const t of times) { await frame(+t); await page.screenshot({ path: `${process.env.OUT || '.'}/f_${t}.png` }); }
  } else {
    const FPS = 30, N = 60 * FPS;
    const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-i', 'music.wav', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
      '-profile:v', 'high', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', process.env.OUTFILE || 'out.mp4'],
      { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = 0; i < N; i++) {
      await frame(i / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.error('frame', i);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
