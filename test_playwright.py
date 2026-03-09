import asyncio
from playwright.async_api import async_playwright

async def test():
    print("🚀 Testing Playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://clutch.co/developers/artificial-intelligence")
        print(f"📄 Page title: {await page.title()}")
        await page.wait_for_timeout(3000)
        await browser.close()
    print("✅ Playwright works!")

asyncio.run(test())