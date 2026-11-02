import { test } from '@playwright/test';
import { login, uniqueSuffix } from './helpers';

test('debug new user overflow', async ({ page }) => {
  const suffix = uniqueSuffix();
  const username = `dbg${suffix}`.slice(0, 16);
  const email = `dbg${suffix}@example.com`;
  const password = 'DbgUser123!';
  const reg = await page.request.post('/api/v1/auth/register', {
    data: { username, email, password, full_name: 'Debug User' },
  });
  console.log('REG', reg.status());
  await login(page, email, password);
  await page.waitForTimeout(1000);
  const info = await page.evaluate(() => {
    const items = Array.from(document.querySelectorAll('*')).map((el) => {
      const rect = el.getBoundingClientRect();
      const style = getComputedStyle(el);
      return {
        tag: el.tagName,
        cls: String((el as HTMLElement).className || '').slice(0, 120),
        text: (el as HTMLElement).innerText?.slice(0, 30),
        width: Math.round(rect.width),
        right: Math.round(rect.right),
        left: Math.round(rect.left),
        position: style.position,
        transform: style.transform,
        overflow: style.overflow,
      };
    });
    return {
      docScrollWidth: document.documentElement.scrollWidth,
      bodyScrollWidth: document.body.scrollWidth,
      innerWidth: window.innerWidth,
      offenders: items.filter((item) => item.right > window.innerWidth + 0.5).slice(0, 30),
      widest: items.sort((a, b) => b.right - a.right).slice(0, 10),
    };
  });
  console.log('OVERFLOW_DEBUG ' + JSON.stringify(info, null, 2));
});
