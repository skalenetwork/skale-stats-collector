import logging
import datetime
from peewee import SqliteDatabase
from src import DB_FILE_PATH

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

db = SqliteDatabase(DB_FILE_PATH)


def run():
    logger.info('Running migration: 001_regroup_userstats')

    today = datetime.date.today()
    cutoff_date = today - datetime.timedelta(days=30)
    logger.info(f'Cutoff date: {cutoff_date}')

    with db.atomic():
        # Create a replacement table
        db.execute_sql('''
            CREATE TABLE IF NOT EXISTS userstats_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT NOT NULL,
                date DATE NOT NULL,
                schain_name TEXT NOT NULL,
                UNIQUE(address, schain_name, date)
            );
        ''')

        # Copy recent (>= cutoff) rows as-is
        db.execute_sql('''
            INSERT INTO userstats_new (address, date, schain_name)
            SELECT address, date, schain_name
            FROM userstats
            WHERE date >= ?;
        ''', (cutoff_date,))

        # Aggregate older (< cutoff) rows into one per (address, schain_name, month)
        # Use date(date, 'start of month') to normalize to the 1st of the month.
        db.execute_sql('''
            INSERT OR IGNORE INTO userstats_new (address, date, schain_name)
            SELECT
                address,
                date(date, 'start of month') AS date,
                schain_name
            FROM userstats
            WHERE date < ?
            GROUP BY address, schain_name, strftime('%Y-%m', date);
        ''', (cutoff_date,))

        db.execute_sql('DROP TABLE userstats;')
        db.execute_sql('ALTER TABLE userstats_new RENAME TO userstats;')

        # Change userstats index order
        logger.info('Recreating old userstats indexes')
        db.execute_sql('DROP INDEX IF EXISTS userstats_address_date_schain_name;')
        db.execute_sql('CREATE UNIQUE INDEX IF NOT EXISTS userstats_schain_name_date_address ON userstats (schain_name, date, address);')

        # Create the LastPulledData table if it doesn’t exist
        db.execute_sql('''
            CREATE TABLE IF NOT EXISTS lastpulleddata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schain_name TEXT UNIQUE NOT NULL,
                block_number INTEGER NOT NULL
            );
        ''')

        # Insert or update the latest block per schain_name
        db.execute_sql('''
            INSERT INTO lastpulleddata (schain_name, block_number)
            SELECT schain_name, MAX(block_number) AS last_block
            FROM pulledblocks
            GROUP BY schain_name
            ON CONFLICT(schain_name)
            DO UPDATE SET block_number = excluded.block_number
            WHERE excluded.block_number > lastpulleddata.block_number;
        ''')

        db.execute_sql('DROP TABLE pulledblocks;')

        logger.info('LastPulledData table migrated successfully')

    # Reclaim free space
    logger.info('Running VACUUM to reclaim free space...')
    db.execute_sql('VACUUM;')
    logger.info('Database VACUUM complete')

    logger.info("Migration 001_regroup_userstats completed successfully.")

if __name__ == '__main__':
    run()
