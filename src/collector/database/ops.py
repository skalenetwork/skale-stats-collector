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
from datetime import datetime, timedelta

from peewee import fn, IntegrityError
from src.collector.database.models import (DailyStatsRecord, PulledBlocks, UserStats, DailyPrices)

logger = logging.getLogger(__name__)
MAX_ROWS_TO_INSERT = 1000


def insert_new_block_data(schain_name, number, date, txs, gas):
    try:
        PulledBlocks.create(schain_name=schain_name, block_number=number).save()
        daily_record, created = DailyStatsRecord.get_or_create(date=date, schain_name=schain_name)
        daily_record.block_count_total += 1
        daily_record.tx_count_total += txs
        daily_record.gas_total_used += gas
        daily_record.save()
    except IntegrityError:
        logger.warning(f'Could not write block {number} for {schain_name}')


def insert_new_daily_users(schain_name, date, users):
    _users = [{'address': user, 'date': date, 'schain_name': schain_name} for user in users]
    for i in range(0, len(_users), MAX_ROWS_TO_INSERT):
        UserStats.insert_many(_users[i:i + MAX_ROWS_TO_INSERT]).on_conflict_ignore().execute()
    daily_record, created = DailyStatsRecord.get_or_create(date=date, schain_name=schain_name)
    day_users = UserStats.select().where(
        (UserStats.date == date) &
        (UserStats.schain_name == schain_name)).count()
    daily_record.user_count_total = day_users
    daily_record.save()


def insert_new_daily_prices(prices):
    _prices = [{'date': k, 'eth_price': prices[k][0], 'gas_price': prices[k][1]} for k in prices]
    DailyPrices.insert_many(_prices).on_conflict_ignore().execute()


def update_daily_price_stats(schain_name):
    unfetched_days = DailyStatsRecord.select().where(
        (DailyStatsRecord.schain_name == schain_name) &
        (DailyStatsRecord.gas_fees_total_gwei == 0) &
        (DailyStatsRecord.gas_total_used != 0)
    )
    for day in unfetched_days:
        logger.debug(f'Updating {schain_name} gas fees saved for {day}')
        prices = DailyPrices.select().where(DailyPrices.date == day.date).get_or_none()
        if prices:
            day.gas_fees_total_gwei = day.gas_total_used * prices.gas_price / 10 ** 9
            day.gas_fees_total_eth = day.gas_total_used * prices.gas_price / 10 ** 18
            day.gas_fees_total_usd = day.gas_fees_total_eth * prices.eth_price
            day.save()


def get_total_data(schain_name, days_before=None, group_by_month=False):
    tx_total = fn.SUM(DailyStatsRecord.tx_count_total)
    gas_total = fn.SUM(DailyStatsRecord.gas_total_used)
    gas_fees_total_gwei = fn.SUM(DailyStatsRecord.gas_fees_total_gwei)
    gas_fees_total_eth = fn.SUM(DailyStatsRecord.gas_fees_total_eth)
    gas_fees_total_usd = fn.SUM(DailyStatsRecord.gas_fees_total_usd)
    blocks_total = fn.SUM(DailyStatsRecord.block_count_total)
    users_total = fn.COUNT(UserStats.address.distinct()).alias('users_count_total')

    metrics_stats = run_stats_query(schain_name, DailyStatsRecord,
                                    [tx_total, blocks_total, gas_total, gas_fees_total_gwei,
                                     gas_fees_total_eth, gas_fees_total_usd],
                                    days_before, group_by_month)
    users_stats = run_stats_query(schain_name, UserStats, [users_total],
                                  days_before, group_by_month)
    if group_by_month:
        for date in users_stats:
            metrics_stats[date].update(users_stats[date])
    else:
        metrics_stats.update(users_stats)
    return metrics_stats


def count_pulled_blocks(schain_name):
    return PulledBlocks.select().where(PulledBlocks.schain_name == schain_name).count()


def last_pulled_block(schain_name):
    last_block = PulledBlocks.select(fn.MAX(PulledBlocks.block_number)).where(
        PulledBlocks.schain_name == schain_name).scalar()
    if not last_block:
        return 0
    return last_block


def run_stats_query(schain_name, model, stats_fields, days_before=None,
                    group_by_month=False):
    condition = model.schain_name == schain_name
    if days_before:
        condition = condition & (model.date.between(
            datetime.utcnow().today() - timedelta(days=days_before),
            datetime.utcnow().today()
        ))
    if group_by_month:
        stats_month = fn.strftime('%Y-%m', model.date)
        stats_fields.append(stats_month)
        query = model.select(*stats_fields).where(condition).group_by(stats_month)
    else:
        query = model.select(*stats_fields).where(condition)
    raw_result = query.dicts()
    if not group_by_month:
        result = raw_result.get()
        for field in result:
            if not result[field]:
                result[field] = 0
        return result
    result_dict = {}
    for item in raw_result:
        date = item.pop('date')
        result_dict[date] = item
    return result_dict


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
