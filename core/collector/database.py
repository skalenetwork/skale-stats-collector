import logging

from playhouse.shortcuts import model_to_dict
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


def insert_new_block(schain_name, date, txs, users):
    _users = [{'address': user, 'date':date, 'schain_name':schain_name} for user in users]
    UserStats.insert_many(_users).on_conflict_ignore().execute()
    day_users = UserStats.select().where(UserStats.date==date and UserStats.schain_name==schain_name).count()
    DailyStatsRecord.update({
        DailyStatsRecord.schain_name: schain_name,
        DailyStatsRecord.date: date,
        DailyStatsRecord.block_count_total: DailyStatsRecord.block_count_total + 1,
        DailyStatsRecord.tx_count_total: DailyStatsRecord.tx_count_total + txs,
        DailyStatsRecord.user_count_total: day_users
    }).execute()


def get_data(schain_name, date):
    return model_to_dict(DailyStatsRecord.select().where(
        DailyStatsRecord.date == date and
        DailyStatsRecord.schain_name == schain_name).get())


def create_tables():
    if not DailyStatsRecord.table_exists():
        logger.info('Creating DailyStatsRecord table...')
        DailyStatsRecord.create_table()

    if not UserStats.table_exists():
        logger.info('Creating UserStats table...')
        UserStats.create_table()
