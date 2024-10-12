import random

from loguru import logger

from tools.add_logger import add_logger
from tools.executor import single_executor
from tools.other_utils import read_file, get_proxied_session
from user_data.config import mobile_proxy, shuffle_accounts

if __name__ == '__main__':
    add_logger(version='v2.0')
    try:
        lines = read_file('user_data/private.txt')
        if shuffle_accounts:
            random.shuffle(lines)

        session = get_proxied_session(proxy=mobile_proxy)
        for index, line in enumerate(lines, start=1):
            single_executor(index=index, line=line, session=session)
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        logger.exception(e)
