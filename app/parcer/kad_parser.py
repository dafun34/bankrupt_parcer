import asyncio
from datetime import date
from app.logging_config import logger

class KadParser:

    async def parse_case(self, case_number: str) -> dict:
        logger.info(f"Parsing case: {case_number} (fake data)")
        await asyncio.sleep(0.5)
        return {
            "case_number": case_number,
            "last_date": date(2025, 5, 5),
            "document_name": "О завершении реализации имущества гражданина",
        }
