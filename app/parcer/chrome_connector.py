from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import asyncio
import random

class ChromeConnector:
    def __init__(self, cdp_url: str, headless: bool = True):
        self.cdp_url = cdp_url
        self.headless = headless
        self.playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect_over_cdp(self.cdp_url)

        if self.browser.contexts:
            self.context = self.browser.contexts[0]
        else:
            self.context = await self.browser.new_context()

        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def new_page(self) -> Page:
        page = await self.context.new_page()
        # случайная пауза перед началом работы
        await asyncio.sleep(random.uniform(0.5, 2.0))
        return page
