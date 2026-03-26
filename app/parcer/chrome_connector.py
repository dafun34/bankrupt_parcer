import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class ChromeConnector:

    def __init__(self, cdp_url: str = "http://localhost:9222"):
        self.cdp_url = cdp_url
        self.playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    async def connect(self):
        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.connect_over_cdp(
            self.cdp_url
        )

        self.context = self.browser.contexts[0]
        self.page = self.context.pages[0]

        return self.page

    async def close(self):
        if self.playwright:
            await self.playwright.stop()
