from app.db.session import run_migrations
from app.logging_config import logger

if __name__ == '__main__':
    run_migrations()