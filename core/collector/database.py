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


class DailyPrices(BaseModel):
    date = DateField(unique=True)
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
    # logger.info('A')
    # is_block_pulled = PulledBlocks.select().where(
    #     (PulledBlocks.block_number == number) &
    #     (PulledBlocks.schain_name == schain_name)).count()
    # if is_block_pulled == 0:
    # logger.info('B')
    _users = [{'address': user, 'date': date, 'schain_name': schain_name} for user in users]
    UserStats.insert_many(_users).on_conflict_ignore().execute()
    day_users = UserStats.select().where(
        (UserStats.date == date) &
        (UserStats.schain_name == schain_name)).count()
    # logger.info('C')
    daily_record, created = DailyStatsRecord.get_or_create(date=date, schain_name=schain_name)
    daily_record.block_count_total += 1
    daily_record.tx_count_total += txs
    daily_record.user_count_total = day_users
    daily_record.gas_total_used += gas
    daily_record.save()
    # logger.info('D')
    PulledBlocks.create(schain_name=schain_name, block_number=number).save()
    # logger.info('E')
    # else:
    #     logger.debug(f'Block {number} was already pulled')


def update_daily_prices(prices):
    _prices = [{'date': k, 'eth_price': prices[k][0], 'gas_price': prices[k][1]} for k in prices]
    DailyPrices.insert_many(_prices).on_conflict_ignore().execute()
    for i in DailyPrices.select().dicts():
        logger.info(i)


def refetch_daily_price_stats(schain_name):
    unfetched_days = DailyStatsRecord.select().where(
        (DailyStatsRecord.schain_name == schain_name) &
        (DailyStatsRecord.gas_fees_total_gwei == 0) &
        (DailyStatsRecord.gas_total_used != 0)
    )
    for day in unfetched_days:
        logger.info(day.date)
        prices = DailyPrices.select().where(DailyPrices.date == day.date).get_or_none()
        logger.info(prices)
        if prices:
            day.gas_fees_total_gwei = day.gas_total_used * prices.gas_price / 10 ** 9
            day.gas_fees_total_eth = day.gas_total_used * prices.gas_price / 10 ** 18
            day.gas_fees_total_usd = day.gas_fees_total_eth * prices.eth_price
            day.save()


def get_data(schain_name):
    return DailyStatsRecord.select().where(DailyStatsRecord.schain_name == schain_name).dicts()


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

    if not DailyPrices.table_exists():
        logger.info('Creating DailyPrices table...')
        DailyPrices.create_table()
