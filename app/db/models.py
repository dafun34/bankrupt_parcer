from sqlalchemy import String, Date, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base


class FedresursRecord(Base):
    __tablename__ = "fedresurs_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    inn: Mapped[str] = mapped_column(String(20), nullable=False)
    case_number: Mapped[str] = mapped_column(String(100), nullable=True)
    last_date: Mapped[datetime] = mapped_column(nullable=True)
    parsed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("inn", name="uix_fedresurs_inn"),
    )


class KadRecord(Base):
    __tablename__ = "kad_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_number: Mapped[str] = mapped_column(String(50), nullable=False)
    last_date: Mapped[datetime] = mapped_column(nullable=True)
    document_name: Mapped[str] = mapped_column(Text, nullable=True)
    parsed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("case_number", name="uix_kad_case"),
    )