import asyncio
from app.db.session import AsyncSessionLocal
from app.db.repository import Repository
from app.parcer.fedresurs_parser import FedresursParser
from app.parcer.kad_parser import KadParser
from app.logging_config import logger

class BankruptcyService:

    def __init__(self):
        self.fedresurs_parser = FedresursParser()
        self.kad_parser = KadParser()

    async def process_inns(self, inns: list[str]):
        async with AsyncSessionLocal() as session:
            repo = Repository(session)
            for inn in inns:
                if await repo.exists_fedresurs(inn):
                    logger.info(f"Already exists in DB: {inn}")
                    continue
                data = await self.fedresurs_parser.parse_inn(inn)
                await repo.save_fedresurs(data)
                logger.info(f"Saved INN {inn} to DB")

    async def process_cases(self, cases: list[str]):
        async with AsyncSessionLocal() as session:
            repo = Repository(session)
            for case in cases:
                if await repo.exists_kad(case):
                    logger.info(f"Already exists in DB: {case}")
                    continue
                data = await self.kad_parser.parse_case(case)
                await repo.save_kad(data)
                logger.info(f"Saved case {case} to DB")
