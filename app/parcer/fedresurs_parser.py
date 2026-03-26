import re

from datetime import datetime
from app.parcer.chrome_connector import ChromeConnector
from app.logging_config import logger


class FedresursParser:
    def __init__(self):
        self.chrome_connector = ChromeConnector()

    async def parse_inn(self, inn: str) -> dict:
        page = await self.chrome_connector.connect()

        # 1️⃣ Переходим на страницу и вводим ИНН
        await page.goto("https://fedresurs.ru/")
        await page.wait_for_selector('input[formcontrolname="searchString"]')
        await page.fill('input[formcontrolname="searchString"]', inn)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(5000)

        # Ждем появления ссылочного блока "Вся информация"
        element = await page.query_selector('a.info.info_position >> text=Вся информация')

        if not element:
            logger.warning(f"ИНН {inn}: данные не найдены, элемент 'Вся информация' отсутствует")
            # Возвращаем результат с None
            return {
                "inn": inn,
                "case_number": None,
                "last_date": None,
            }

        # Если элемент есть — кликаем и продолжаем как обычно
        await element.click()
        await page.wait_for_timeout(2000)  # даем странице подгрузить содержимое


        # 3️⃣ Разворачиваем блок "Сведения о банкротстве"
        elements = await page.query_selector_all('div.nav-menu-item-description')
        for el in elements:
            text = await el.text_content()
            if text and "Сведения о банкротстве" in text:
                parent = await el.evaluate_handle("el => el.parentElement")
                await parent.click()
                break

        await page.wait_for_timeout(2000)

        # 1️⃣ № дела
        case_number_el = await page.query_selector('a.info-header.underlined')
        case_number = (await case_number_el.text_content()).strip() if case_number_el else None

        # 2️⃣ Последний документ (берем первый элемент публикации)
        pub_item_el = await page.query_selector(
            'div.info-item-value entity-card-bankruptcy-publication-wrapper:first-child a.underlined')
        last_date_text = (await pub_item_el.text_content()).strip() if pub_item_el else None

        # Выделяем только дату
        last_date_match = re.search(r'от (\d{2}\.\d{2}\.\d{4})', last_date_text)
        date_str = last_date_match.group(1) if last_date_match else None
        last_date = datetime.strptime(date_str, "%d.%m.%Y")

        result = {
            "inn": inn,
            "case_number": case_number,
            "last_date": last_date,
        }
        return result
