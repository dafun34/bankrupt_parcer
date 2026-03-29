from sqlalchemy import String, Date, Text, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base


class FedresursRecord(Base):
    __tablename__ = "fedresurs_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    inn: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    case_number: Mapped[str] = mapped_column(String(50))  # последний case_number
    last_date: Mapped[datetime] = mapped_column(nullable=True)  # дата последнего документа по делу
    document_name: Mapped[str] = mapped_column(String(500), nullable=True)  # название документа
    parsed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Если в будущем захотим несколько дел
    kad_cases: Mapped[list["KadRecord"]] = relationship("KadRecord", back_populates="fedresurs")


class KadRecord(Base):
    __tablename__ = "kad_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    last_date: Mapped[datetime] = mapped_column(nullable=True)  # дата последнего документа по делу
    document_name: Mapped[str] = mapped_column(String, nullable=True)
    parsed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    fedresurs_id: Mapped[int] = mapped_column(ForeignKey("fedresurs_records.id"))
    fedresurs: Mapped[FedresursRecord] = relationship("FedresursRecord", back_populates="kad_cases")
