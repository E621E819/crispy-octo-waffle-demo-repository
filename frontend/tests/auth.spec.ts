import { test, expect } from '@playwright/test'

test('评审登录入口明确展示 OAuth 状态和隐私说明', async ({ page }) => {
  await page.goto('/')
  await page.locator('.profile').click()
  await expect(page.getByRole('dialog')).toContainText('登录 / 切换账号')
  await page.getByRole('button', { name: '登录 / 切换账号' }).click()
  const dialog = page.getByRole('dialog')
  await expect(dialog).toContainText('登录 Exam Radar')
  await expect(dialog).toContainText('登录用于保存你的学习进度')
  const oauthButton = dialog.getByRole('button', { name: /使用知乎登录/ })
  if (await oauthButton.count()) await expect(oauthButton).toBeVisible()
  else await expect(dialog).toContainText('知乎登录暂不可用')
})

