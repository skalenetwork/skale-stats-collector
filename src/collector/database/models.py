import logging

from peewee import (Model, SqliteDatabase, PrimaryKeyField, IntegerField, FloatField,
                    DateField, CharField)
from src import DB_FILE_PATH

logger = logging.getLogger(__name__)


class BaseModel(Model):
    database = SqliteDatabase(DB_FILE_PATH)

    class Meta:
        database = SqliteDatabase(DB_FILE_PATH)


class PulledBlocks(BaseModel):
    schain_name = CharField()
    block_number = IntegerField()

    class Meta:
        indexes = (
            (('schain_name', 'block_number'), True),
        )


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
