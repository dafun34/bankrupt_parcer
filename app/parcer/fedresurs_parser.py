import asyncio
from app.logging_config import logger
from datetime import date

class FedresursParser:

    async def parse_inn(self, inn: str) -> dict:
        logger.info(f"Parsing INN: {inn} (fake data)")
        # Заглушка, позже заменим на Playwright
        await asyncio.sleep(0.5)  # имитация задержки
        return {
            "inn": inn,
            "case_number": "А40-12345/2025",
            "last_date": date(2025, 5, 5),
        }