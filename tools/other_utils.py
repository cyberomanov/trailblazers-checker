import random
import time

import requests
from loguru import logger


def read_file(path: str = 'data/mnemonic.txt'):
    with open(path) as file:
        not_empty = [line for line in file.read().splitlines() if line and not line.startswith('# ')]
    return not_empty


def sleep_in_range(sec_from: int, sec_to: int, log: bool = False):
    sleep_time = random.uniform(sec_from, sec_to)
    if log:
        logger.info(f"sleep {sleep_time} sec.")
    time.sleep(sleep_time)


def get_proxied_session(proxy: str):
    session = requests.Session()
    if proxy:
        session.proxies = {
            'http': proxy,
            'https': proxy
        }
    session.request = lambda *args, **kwargs: requests.Session.request(session, *args, timeout=60, **kwargs)
    return session
