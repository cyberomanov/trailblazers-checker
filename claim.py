import os
import random
import re
import time

from loguru import logger

from tools.add_logger import add_logger, LOG_OUTPUT
from tools.executor import single_executor
from tools.other_utils import read_file, get_proxied_session
from user_data.config import mobile_proxy, shuffle_accounts

if __name__ == '__main__':
    if os.path.exists(LOG_OUTPUT):
        os.remove(LOG_OUTPUT)

    add_logger(version='v2.0')
    try:
        lines = read_file('user_data/private.txt')
        if shuffle_accounts:
            random.shuffle(lines)

        session = get_proxied_session(proxy=mobile_proxy)
        for index, line in enumerate(lines, start=1):
            single_executor(index=index, line=line, session=session)

        insufficient_addresses = []
        log_lines = read_file('log/taiko.log')
        for line in log_lines:
            if 'insufficient' in line:
                wallet_match = re.search(r'0x[a-fA-F0-9]{40}', line)
                wallet_address = wallet_match.group(0) if wallet_match else None
                if wallet_address:
                    insufficient_addresses.append(wallet_address)

        if insufficient_addresses:
            insufficient_addresses = set(insufficient_addresses)
            logger.info(f'found {len(insufficient_addresses)} addresses with insufficient balance: \n')
            time.sleep(3)
            for address in insufficient_addresses:
                print(address)

    except KeyboardInterrupt:
        exit()
    except Exception as e:
        logger.exception(e)
