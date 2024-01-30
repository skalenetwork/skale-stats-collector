#   -*- coding: utf-8 -*-
#
#   This file is part of skale-stats-collector
#
#   Copyright (C) 2024 SKALE Labs
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

import boto3
import logging
import os
import requests
import tarfile

from datetime import datetime
from src import (
    AWS_S3_BUCKET_NAME, AWS_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY, DATA_DIR, UPTIME_KUMA_URL,
    RETRY_DELAY, RETRY_ATTEMPTS_COUNT
)
from src.utils.meta import get_last_backup_date, update_last_backup_date
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)

TAR_FILE = 'stats_backup.tar'
FILES = ["stats-dump.db", "meta-dump.json", "network-stats.json"]


def archive_files(backup_dir=DATA_DIR):

    backup_file = tarfile.open(TAR_FILE, 'w')
    logger.info(f'Files to archive: {FILES}')
    for x in FILES:
        logger.info((os.path.join(backup_dir, x)))
        backup_file.add(os.path.join(backup_dir, x))

    for x in backup_file.getnames():
        logger.info(f'file {x} added to archive {TAR_FILE}')
    backup_file.close()
    logger.info('Archiving completed')


def send_to_s3(tar_file=TAR_FILE):
    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    response = s3_client.upload_file(tar_file, AWS_S3_BUCKET_NAME, tar_file)

    logger.info(f'upload_log_to_aws response: {response}')
    logger.info(f'Uploading of {TAR_FILE} to S3 bucket completed')


@retry(stop=stop_after_attempt(RETRY_ATTEMPTS_COUNT), wait=wait_fixed(RETRY_DELAY))
def heartbeat(url=UPTIME_KUMA_URL):
    response = requests.get(url)
    if response.status_code == 200:
        logger.info('Heartbeat signal is successfully sent')


def backup_data():
    current_date = str(datetime.utcnow().date())
    if current_date == get_last_backup_date():
        logger.info('Skipping backup - archive file was created today')
        return
    archive_files()
    send_to_s3()
    update_last_backup_date(current_date)
    heartbeat()
