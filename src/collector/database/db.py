import logging
import sys
from time import sleep
from playhouse.pool import PooledMySQLDatabase
from src import MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT

logger = logging.getLogger(__name__)

db = PooledMySQLDatabase(
    MYSQL_DATABASE,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    stale_timeout=300
)


def wait_for_db():
    for _ in range(30):
        try:
            db.connect()
            db.close()
            logger.info('Successfully connected to the database.')
            return
        except Exception as e:
            logger.exception(e)
            logger.warning(
                f'Database connection failed. Retrying in {5} seconds...'
            )
            sleep(5)

    logger.error('Failed to connect to the database after multiple attempts.')
    sys.exit(1)
