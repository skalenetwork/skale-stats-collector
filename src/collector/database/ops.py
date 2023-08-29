import logging
from datetime import datetime, timedelta

from peewee import fn
from src.collector.database.models import (DailyStatsRecord, PulledBlocks, UserStats, DailyPrices)

logger = logging.getLogger(__name__)


def insert_new_block_data(schain_name, number, date, txs, gas):
    daily_record, created = DailyStatsRecord.get_or_create(date=date, schain_name=schain_name)
    daily_record.block_count_total += 1
    daily_record.tx_count_total += txs
    daily_record.gas_total_used += gas
    daily_record.save()
    PulledBlocks.create(schain_name=schain_name, block_number=number).save()


def insert_new_daily_users(schain_name, date, users):
    _users = [{'address': user, 'date': date, 'schain_name': schain_name} for user in users]
    for i in range(0, len(_users), 1000):
        UserStats.insert_many(_users[i:i + 1000]).on_conflict_ignore().execute()
    daily_record, created = DailyStatsRecord.get_or_create(date=date, schain_name=schain_name)
    day_users = UserStats.select().where(
        (UserStats.date == date) &
        (UserStats.schain_name == schain_name)).count()
    daily_record.user_count_total = day_users
    daily_record.save()


def update_daily_prices(prices):
    _prices = [{'date': k, 'eth_price': prices[k][0], 'gas_price': prices[k][1]} for k in prices]
    DailyPrices.insert_many(_prices).on_conflict_ignore().execute()


def refetch_daily_price_stats(schain_name):
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


def get_schain_stats(schain_name):
    return {
        'group_by_month': get_montly_data(schain_name),
        'total': get_total_data(schain_name),
        'total_7d': get_total_data(schain_name, days_before=7),
        'total_30d': get_total_data(schain_name, days_before=30)
    }


def get_montly_data(schain_name):
    tx_total = fn.SUM(DailyStatsRecord.tx_count_total)
    gas_total = fn.SUM(DailyStatsRecord.gas_total_used)
    gas_fees_total_gwei = fn.SUM(DailyStatsRecord.gas_fees_total_gwei)
    gas_fees_total_eth = fn.SUM(DailyStatsRecord.gas_fees_total_eth)
    gas_fees_total_usd = fn.SUM(DailyStatsRecord.gas_fees_total_usd)
    blocks_total = fn.SUM(DailyStatsRecord.block_count_total)
    users_total = fn.COUNT(UserStats.address.distinct()).alias('users_count_total')
    stats_query = (DailyStatsRecord
                   .select(fn.strftime('%Y-%m', DailyStatsRecord.date),
                           tx_total, gas_total, gas_fees_total_gwei,
                           gas_fees_total_eth, gas_fees_total_usd, blocks_total)
                   .where((DailyStatsRecord.schain_name == schain_name))
                   .group_by(fn.strftime('%Y-%m', DailyStatsRecord.date))).dicts()
    users_query = (UserStats
                   .select(fn.strftime('%Y-%m', UserStats.date), users_total)
                   .where((UserStats.schain_name == schain_name))
                   .group_by(fn.strftime('%Y-%m', UserStats.date))).dicts()
    stats_dict = {}
    for item in stats_query:
        date = item.pop('date')
        stats_dict[date] = item
    for item in users_query:
        date = item.pop('date')
        stats_dict[date].update(item)
    return stats_dict


def get_total_data(schain_name, days_before=None):
    tx_total = fn.SUM(DailyStatsRecord.tx_count_total)
    gas_total = fn.SUM(DailyStatsRecord.gas_total_used)
    gas_fees_total_gwei = fn.SUM(DailyStatsRecord.gas_fees_total_gwei)
    gas_fees_total_eth = fn.SUM(DailyStatsRecord.gas_fees_total_eth)
    gas_fees_total_usd = fn.SUM(DailyStatsRecord.gas_fees_total_usd)
    blocks_total = fn.SUM(DailyStatsRecord.block_count_total)
    users_total = fn.COUNT(UserStats.address.distinct()).alias('users_count_total')
    condition_a = DailyStatsRecord.schain_name == schain_name
    condition_b = UserStats.schain_name == schain_name
    if days_before:
        condition_a = condition_a & (DailyStatsRecord.date.between(
                        datetime.now().today() - timedelta(days=days_before),
                        datetime.now().today()
                    ))
        condition_b = condition_b & (UserStats.date.between(
                        datetime.now().today() - timedelta(days=days_before),
                        datetime.now().today()
                    ))
    query = DailyStatsRecord.select(tx_total, gas_total, gas_fees_total_gwei,
                                    gas_fees_total_eth, gas_fees_total_usd,
                                    blocks_total).where(condition_a).dicts()
    query_b = UserStats.select(users_total).where(condition_b).dicts()
    stats_dict = {}
    for item in query:
        stats_dict.update(item)
    for item in query_b:
        stats_dict.update(item)
    return stats_dict


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