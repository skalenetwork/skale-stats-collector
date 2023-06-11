import logging

from peewee import (Model, SqliteDatabase, PrimaryKeyField, IntegerField, FloatField, DateField, CharField)
from core import DB_FILE_PATH

logger = logging.getLogger(__name__)

class BaseModel(Model):
    database = SqliteDatabase(DB_FILE_PATH)

    class Meta:
        database = SqliteDatabase(DB_FILE_PATH)


# class GlobalStatsRecord(BaseModel):
#     id = PrimaryKeyField()
#
#
# class SchainStatsRecord(BaseModel):
#     id = PrimaryKeyField()
#     schain_name = CharField()
#     stats_record = ForeignKeyField(GlobalStatsRecord, related_name='global_stats')
#
#
# class MonthlyStatsRecord(BaseModel):
#     id = PrimaryKeyField()
#     month = DateField()
#     stats_record = ForeignKeyField(SchainStatsRecord, related_name='schain_stats')


class UserStats(BaseModel):
    address = CharField()
    date = DateField()
    schain_name = CharField()


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


def create_tables():
    if not DailyStatsRecord.table_exists():
        logger.info('Creating DailyStatsRecord table...')
        DailyStatsRecord.create_table()

    if not UserStats.table_exists():
        logger.info('Creating UserStats table...')
        UserStats.create_table()
