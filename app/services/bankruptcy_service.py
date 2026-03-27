import asyncio
from app.db.session import AsyncSessionLocal
from app.db.repository import Repository
from app.parcer.fedresurs_parser import FedresursParser
from app.parcer.kad_parser import KadParser
from app.logging_config import logger


class BankruptcyService:

    def __init__(self, max_concurrent_tasks: int = 5):
        self.fedresurs_parser = FedresursParser()
        self.kad_parser = KadParser()
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def process_inns(self, inns: list[str]):
        """
        Основной pipeline:
        ИНН → Fedresurs → case_number → KAD → сохранение
        """

        for inn in inns:
            await self._process_single_inn(inn)

    async def _process_single_inn(self, inn: str):
        async with self.semaphore:  # ограничиваем параллельность
            try:
                async with AsyncSessionLocal() as session:
                    repo = Repository(session)

                    # Проверка существования
                    if await repo.exists_fedresurs(inn):
                        logger.info(f"[SKIP] Already exists: {inn}")
                        return

                    # 1️⃣ Парсим Fedresurs
                    fedresurs_data = await self.fedresurs_parser.parse_inn(inn)

                    if not fedresurs_data or not fedresurs_data.get("case_number"):
                        logger.warning(f"[NO CASE] No case found for INN {inn}")
                        return

                    case_number = fedresurs_data["case_number"]

                    # 2️⃣ Парсим KAD
                    kad_data = await self.kad_parser.parse_case(case_number)

                    # 3️⃣ Объединяем данные
                    combined_data = {
                        **fedresurs_data,
                        **kad_data,
                    }

                    # 4️⃣ Сохраняем
                    await repo.save_full_record(combined_data)

                    logger.info(f"[SUCCESS] INN {inn} processed")

            except Exception as e:
                logger.error(f"[ERROR] Failed processing INN {inn}: {e}")
