from loguru import logger as logging

class BankruptcyService():
    async def process_inns(self, inns: list[str]):
        for inn in inns:
            logging.info(f"Processing INN: {inn}")

    async def process_cases(self, cases: list[str]):
        for case in cases:
            logging.info(f"Processing case: {case}")
