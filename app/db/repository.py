from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import FedresursRecord, KadRecord


class Repository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists_fedresurs(self, inn: str) -> bool:
        """Проверяет, существует ли запись с данным ИНН в таблице FedresursRecord."""
        result = await self.session.execute(select(FedresursRecord.id).where(FedresursRecord.inn == inn))
        return result.scalar_one_or_none() is not None

    async def save_full_record(self, data: dict):
        """Сохраняет данные из Fedresurs и Kad в одну транзакцию."""
        fedresurs_record = FedresursRecord(
            inn=data["inn"],
            case_number=data.get("case_number"),
            last_date=data.get("last_date"),
            document_name=data.get("document_name"),
        )

        self.session.add(fedresurs_record)
        await self.session.flush()  # получаем fedresurs_record.id

        # Создаем запись Kad (если нужно хранить отдельно)
        kad_record = KadRecord(
            case_number=data["case_number"],
            last_date=data.get("last_date"),
            document_name=data.get("document_name"),
            fedresurs_id=fedresurs_record.id,
        )

        self.session.add(kad_record)

        await self.session.commit()
