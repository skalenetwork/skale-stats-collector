import logging

from peewee import (Model, SqliteDatabase, PrimaryKeyField, IntegerField, FloatField, DateField, CharField)
from core import DB_FILE_PATH

logger = logging.getLogger(__name__)


class BaseModel(Model):
    database = SqliteDatabase(DB_FILE_PATH)

    class Meta:
        database = SqliteDatabase(DB_FILE_PATH)


class PulledBlocks(BaseModel):
    schain_name = CharField()
    block_number = IntegerField()


class Prices(BaseModel):
    date = DateField()
    gas_price = IntegerField(default=0)
    eth_price = FloatField(default=0)


class UserStats(BaseModel):
    address = CharField()
    date = DateField()
    schain_name = CharField()

    class Meta:
        indexes = (
            (('address', 'date', 'schain_name'), True),
        )



class DailyStatsRecord(BaseModel):
    id = PrimaryKeyField()
    date = DateField()
    schain_name = CharField()

    user_count_total = IntegerField(default=0)
    tx_count_total = IntegerField(default=0)
    block_count_total = IntegerField(default=0)
    gas_total_used = FloatField(default=0)
    gas_fees_total_gwei = FloatField(default=0)
    gas_fees_total_eth = FloatField(default=0)
    gas_fees_total_usd = FloatField(default=0)


def insert_new_block(schain_name, number, date, txs, users, gas):
    is_block_pulled = PulledBlocks.select().where(
        (PulledBlocks.block_number == number) &
        (PulledBlocks.schain_name == schain_name)).count()
    if is_block_pulled == 0:
        _users = [{'address': user, 'date': date, 'schain_name': schain_name} for user in users]
        UserStats.insert_many(_users).on_conflict_ignore().execute()
        day_users = UserStats.select().where(
            (UserStats.date == date) &
            (UserStats.schain_name == schain_name)).count()
        daily_record, created = DailyStatsRecord.get_or_create(date=date, schain_name=schain_name)
        daily_record.block_count_total += 1
        daily_record.tx_count_total += txs
        daily_record.user_count_total = day_users
        daily_record.gas_total_used += gas
        daily_record.save()
        PulledBlocks.create(schain_name=schain_name, block_number=number).save()
    else:
        logger.debug(f'Block {number} was already pulled')


def get_data(schain_name, date):
    return DailyStatsRecord.select().where((DailyStatsRecord.schain_name ==schain_name)).dicts()


def create_tables():
    if not DailyStatsRecord.table_exists():
        logger.info('Creating DailyStatsRecord table...')
        DailyStatsRecord.create_table()

    if not UserStats.table_exists():
        logger.info('Creating UserStats table...')
        UserStats.create_table()

    if not PulledBlocks.table_exists():
        logger.info('Creating PulledBlocks table...')
        PulledBlocks.create_table()
