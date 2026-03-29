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
                page = None
                fedresurs_data = None
                try:
                    if await repo.exists_fedresurs(inn):
                        logger.info(f"[SKIP] Already exists: {inn}")
                        return

                    # --- Fedresurs ---
                    for attempt in range(3):
                        try:
                            page = await self.chrome.new_page()
                            fedresurs_data = await self.fedresurs_parser.parse_inn(inn, page)
                            break
                        except Exception as e:
                            logger.warning(f"Retry {attempt + 1} for INN {inn} due to {e}")
                            await asyncio.sleep(2**attempt)
                        finally:
                            if page and not page.is_closed():
                                await page.close()
                            page = None  # чтобы следующая попытка открыла новую страницу

                    if not fedresurs_data or not fedresurs_data.get("case_number"):
                        logger.warning(f"[NO CASE] No case found for INN {inn}")
                        return  # больше не идём в KAD

                    case_number = fedresurs_data["case_number"]

                    # --- KAD ---
                    kad_data = None
                    for attempt in range(3):
                        try:
                            page = await self.chrome.new_page()
                            kad_data = await self.kad_parser.parse_case(case_number, page)
                            break
                        except Exception as e:
                            logger.warning(f"Retry {attempt + 1} for case {case_number} due to {e}")
                            await asyncio.sleep(2**attempt)
                        finally:
                            if page and not page.is_closed():
                                await page.close()
                            page = None

                    # --- Сохраняем данные ---
                    combined_data = {**fedresurs_data, **(kad_data or {})}
                    await repo.save_full_record(combined_data)
                    logger.info(f"[SUCCESS] INN {inn} processed")

                except Exception as e:
                    logger.error(f"[ERROR] Failed processing INN {inn}: {e}")
                finally:
                    if page and not page.is_closed():
                        await page.close()
