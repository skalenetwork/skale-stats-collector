#   -*- coding: utf-8 -*-
#
#   This file is part of skale-stats-collector
#
#   Copyright (C) 2023 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
