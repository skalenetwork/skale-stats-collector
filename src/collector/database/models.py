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
import os
from playhouse.pool import PooledMySQLDatabase
from peewee import (Model, PrimaryKeyField, IntegerField, BigIntegerField, DoubleField,
                    DateField, CharField)
import sys
from time import sleep

logger = logging.getLogger(__name__)


db = PooledMySQLDatabase(
    os.getenv('MYSQL_DATABASE'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    host=os.getenv('MYSQL_HOST'),
    port=int(os.getenv('MYSQL_PORT', 3306)),
    max_connections=8,
    stale_timeout=300,
)


class BaseModel(Model):
    class Meta:
        database = db


class PulledBlocks(BaseModel):
    schain_name = CharField()
    block_number = IntegerField()

    class Meta:
        indexes = (
            (('schain_name', 'block_number'), True),
        )


class DailyPrices(BaseModel):
    date = DateField(unique=True)
    gas_price = BigIntegerField(default=0)
    eth_price = DoubleField(default=0)


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
    gas_total_used = DoubleField(default=0)
    gas_fees_total_gwei = DoubleField(default=0)
    gas_fees_total_eth = DoubleField(default=0)
    gas_fees_total_usd = DoubleField(default=0)


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
