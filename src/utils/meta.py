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

from src import META_DATA_PATH
from src.utils.helper import write_json, read_json


def create_meta_file():
    empty_data = {
        'schains': {}
    }
    write_json(META_DATA_PATH, empty_data)


def get_meta_file():
    return read_json(META_DATA_PATH)


def get_schain_meta(schain_name):
    meta = get_meta_file()['schains']
    return meta.get(schain_name)


def get_schain_endpoint(schain_name):
    meta = get_schain_meta(schain_name)
    if meta:
        return meta.get('endpoint')
    else:
        return None


def update_last_price_date(last_update_date):
    meta = get_meta_file()
    meta['last_price_update'] = last_update_date
    update_meta_file(meta)


def update_last_block(schain_name, last_block):
    meta = get_meta_file()
    meta['schains'][schain_name]['last_updated_block'] = last_block
    update_meta_file(meta)


def get_last_block(schain_name):
    return get_schain_meta(schain_name).get('last_updated_block', 0)


def get_last_price_date():
    meta = get_meta_file()
    return meta.get('last_price_update', '2021-01-01')


def update_meta_file(meta_data):
    write_json(META_DATA_PATH, meta_data)


def get_last_backup_date():
    meta = get_meta_file()
    return meta.get('last_backup_date', '2021-01-01')


def update_last_backup_date(last_backup_date):
    meta = get_meta_file()
    meta['last_backup_date'] = last_backup_date
    update_meta_file(meta)
