import asyncio

from app.db.repository import Repository
from app.db.session import AsyncSessionLocal
from app.logging_config import logger
from app.parcer.chrome_connector import ChromeConnector
from app.parcer.fedresurs_parser import FedresursParser
from app.parcer.kad_parser import KadParser


class BankruptcyService:
    def __init__(self, chrome_connector: ChromeConnector, max_concurrent_tasks: int):
        self.chrome = chrome_connector
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.fedresurs_parser = FedresursParser(chrome_connector)
        self.kad_parser = KadParser(chrome_connector)

    async def process_inns(self, inns: list[str]):
        """Обрабатывает список ИНН, создавая для каждого отдельную задачу.

        Контролирует количество одновременных задач через семафор.
        """
        tasks = [asyncio.create_task(self._process_single_inn(inn)) for inn in inns]
        await asyncio.gather(*tasks)

    async def _with_retry(self, coro_factory, attempts: int = 3):
        for attempt in range(attempts):
            page = None
            try:
                page = await self.chrome.new_page()
                return await coro_factory(page)
            except Exception as e:
                logger.warning(f"Retry {attempt + 1} due to {e}")
                await asyncio.sleep(2**attempt)
            finally:
                if page and not page.is_closed():
                    await page.close()
        return None

    async def _parse_fedresurs(self, inn: str):
        return await self._with_retry(lambda page: self.fedresurs_parser.parse_inn(inn, page))

    async def _parse_kad(self, case_number: str):
        return await self._with_retry(lambda page: self.kad_parser.parse_case(case_number, page))

    async def _process_single_inn(self, inn: str):
        async with self.semaphore:
            async with AsyncSessionLocal() as session:
                repo = Repository(session)

                if await repo.exists_fedresurs(inn):
                    logger.info(f"[SKIP] Already exists: {inn}")
                    return

                fedresurs_data = await self._parse_fedresurs(inn)

                if not fedresurs_data or not fedresurs_data.get("case_number"):
                    logger.warning(f"[NO CASE] No case found for INN {inn}")
                    return

                kad_data = await self._parse_kad(fedresurs_data["case_number"])

                combined_data = {**fedresurs_data, **(kad_data or {})}
                await repo.save_full_record(combined_data)

                logger.info(f"[SUCCESS] INN {inn} processed")
