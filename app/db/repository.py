from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import FedresursRecord, KadRecord

class Repository:

    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------- Fedresurs -------------------
    async def exists_fedresurs(self, inn: str) -> bool:
        result = await self.session.execute(
            select(FedresursRecord).where(FedresursRecord.inn == inn)
        )
        return result.scalar() is not None

    async def save_fedresurs(self, data: dict):
        record = FedresursRecord(
            inn=data["inn"],
            case_number=data.get("case_number"),
            last_date=data.get("last_date"),
        )
        self.session.add(record)
        await self.session.commit()

    # ------------------- Kad -------------------
    async def exists_kad(self, case_number: str) -> bool:
        result = await self.session.execute(
            select(KadRecord).where(KadRecord.case_number == case_number)
        )
        return result.scalar() is not None

    async def save_kad(self, data: dict):
        record = KadRecord(
            case_number=data["case_number"],
            last_date=data.get("last_date"),
            document_name=data.get("document_name"),
        )
        self.session.add(record)
        await self.session.commit()
