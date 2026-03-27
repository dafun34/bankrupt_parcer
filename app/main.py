import asyncio
import os
from pathlib import Path
from app.db.session import run_migrations
from app.logging_config import logger
from app.services.bankruptcy_service import BankruptcyService
from app.utils.excel_reader import read_excel_file
from app.config import settings

async def main():

    file_path = settings.base_dir_path / settings.INPUT_FILE_PATH

    if not file_path:
        logger.error("Environment variable INPUT_FILE is not set")
        return

    logger.info(f"Starting bankruptcy parser. File: {file_path}")

    values = read_excel_file(file_path)

    if not values:
        logger.warning("No INNs found in Excel file")
        return

    logger.info(f"Loaded {len(values)} INNs")

    service = BankruptcyService()

    # Обработка списка ИНН (100+)
    await service.process_inns(values)

    logger.info("Processing completed")


if __name__ == "__main__":
    run_migrations()
    asyncio.run(main())