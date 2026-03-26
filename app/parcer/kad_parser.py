import asyncio
import re
from datetime import datetime
from app.parcer.chrome_connector import ChromeConnector
from app.logging_config import logger

class KadParser:
    def __init__(self):
        self.chrome_connector = ChromeConnector()

    async def parse_case(self, case_number: str) -> dict:
        page = await self.chrome_connector.connect()

        await page.goto("https://kad.arbitr.ru/")

        # Ждем появления контейнера поиска
        await page.wait_for_selector('#sug-cases', timeout=20000)

        search_input = page.locator('#sug-cases input')

        await search_input.wait_for(timeout=10000)
        await search_input.click()
        await search_input.fill(case_number)
        await search_input.press("Enter")

        # Ждем появления результатов
        await page.wait_for_selector('a.num_case', timeout=20000)

        # 2️⃣ Переходим по первой ссылке на дело
        await page.wait_for_selector('a.num_case', timeout=10000)

        async with page.context.expect_page() as new_page_info:
            await page.locator('a.num_case').first.click()

        page = await new_page_info.value
        await page.wait_for_load_state("networkidle")

        # 3️⃣ Переходим на вкладку "Электронное дело"
        chrono_btn = page.locator('.b-case-chrono-button-text').filter(has_text="Электронное дело")
        await chrono_btn.wait_for(timeout=10000)
        await chrono_btn.click()


        # Ждём загрузку блока "Электронное дело"
        await page.wait_for_selector('#chrono_ed_content', timeout=20000)

        # Берем первый документ (самый свежий)
        first_item = page.locator('#chrono_ed_content li.b-case-chrono-ed-item').first

        await first_item.wait_for(timeout=10000)

        # 📅 Дата
        date_text = await first_item.locator('.b-case-chrono-ed-item-date').text_content()
        date_text = date_text.strip() if date_text else None

        last_date = (
            datetime.strptime(date_text, "%d.%m.%Y")
            if date_text else None
        )

        # 📄 Название документа
        document_name = await first_item.locator(
            '.b-case-chrono-ed-item-link'
        ).inner_text()

        document_name = re.sub(r'\[.*?\]', '', document_name).strip()
        document_name = document_name if document_name else None

        return {
            "case_number": case_number,
            "last_date": last_date,
            "document_name": document_name,
        }

async def main(case_number: str):
    parser: KadParser = KadParser()
    parsed_data = await parser.parse_case(case_number)
    print(parsed_data)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main(case_number="А32-28873/2024"))
