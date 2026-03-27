import asyncio
from app.db.session import AsyncSessionLocal
from app.db.repository import Repository
from app.parcer.chrome_connector import ChromeConnector
from app.parcer.fedresurs_parser import FedresursParser
from app.parcer.kad_parser import KadParser
from app.logging_config import logger
import random

class BankruptcyService:
    def __init__(self, chrome_connector: ChromeConnector, max_concurrent_tasks: int = 2):
        self.chrome = chrome_connector
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.fedresurs_parser = FedresursParser(chrome_connector)
        self.kad_parser = KadParser(chrome_connector)

    async def process_inns(self, inns: list[str]):
        tasks = [asyncio.create_task(self._process_single_inn(inn)) for inn in inns]
        await asyncio.gather(*tasks)

    async def _process_single_inn(self, inn: str):
        async with self.semaphore:
            async with AsyncSessionLocal() as session:
                repo = Repository(session)

                if await repo.exists_fedresurs(inn):
                    logger.info(f"[SKIP] Already exists: {inn}")
                    return

                # --- retry на Fedresurs ---
                fedresurs_data = None
                for attempt in range(3):
                    try:
                        fedresurs_data = await self.fedresurs_parser.parse_inn(inn)
                        break
                    except Exception as e:
                        logger.warning(f"Retry {attempt+1} for INN {inn} due to {e}")
                        await asyncio.sleep(2 ** attempt)

                if not fedresurs_data or not fedresurs_data.get("case_number"):
                    logger.warning(f"[NO CASE] No case found for INN {inn}")
                    return

                case_number = fedresurs_data["case_number"]

                # --- retry на KAD ---
                kad_data = None
                for attempt in range(3):
                    try:
                        kad_data = await self.kad_parser.parse_case(case_number)
                        break
                    except Exception as e:
                        logger.warning(f"Retry {attempt+1} for case {case_number} due to {e}")
                        await asyncio.sleep(2 ** attempt)

                # Объединяем и сохраняем
                combined_data = {**fedresurs_data, **(kad_data or {})}
                await repo.save_full_record(combined_data)
                logger.info(f"[SUCCESS] INN {inn} processed")

                # небольшая случайная пауза после обработки
                await asyncio.sleep(random.uniform(1, 3))
