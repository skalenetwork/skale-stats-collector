import json
import logging
from functools import wraps
from time import sleep

logger = logging.getLogger(__name__)


def read_json(path, mode='r'):
    with open(path, mode=mode, encoding='utf-8') as data_file:
        return json.load(data_file)


def write_json(path, content):
    with open(path, 'w') as outfile:
        json.dump(content, outfile, indent=4)


def update_dict(target_dict, chain_dict):
    for key in chain_dict:
        if type(chain_dict[key]) is dict:
            if target_dict.get(key) is None:
                target_dict[key] = {}
            update_dict(target_dict[key], chain_dict[key])
        else:
            target_dict[key] = target_dict.get(key, 0) + chain_dict[key]


def daemon(delay=60):
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f'Initiating {func.__name__}')
            while True:
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    logger.exception(f'{e}')
                    logger.warning(f'Restarting {func.__name__}...')
                sleep(delay)
        return wrapper
    return actual_decorator
