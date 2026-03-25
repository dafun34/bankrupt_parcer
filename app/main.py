from app.db.session import run_migrations
from app.logging_config import logger

import argparse
import asyncio

from app.services.bankruptcy_service import BankruptcyService
from app.utils.excel_reader import read_excel_file


def parse_args():
    parser = argparse.ArgumentParser(description="Bankruptcy Parser")

    parser.add_argument(
        "--mode",
        type=str,
        required=True,
        choices=["fedresurs", "kad"],
        help="Parsing mode",
    )

    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to Excel file",
    )

    return parser.parse_args()


async def main():
    args = parse_args()

    logger.info(f"Starting in mode: {args.mode}")

    values = read_excel_file(args.file)

    if not values:
        logger.warning("No data found in Excel file")
        return

    service = BankruptcyService()

    if args.mode == "fedresurs":
        await service.process_inns(values)

    elif args.mode == "kad":
        await service.process_cases(values)


if __name__ == '__main__':
    run_migrations()
    asyncio.run(main())