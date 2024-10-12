from loguru import logger

from tools.add_logger import add_logger
from tools.other_utils import get_reward
from tools.other_utils import read_file, get_proxied_session
from user_data.config import mobile_proxy

if __name__ == '__main__':
    add_logger(version='v2.0')
    try:
        addresses = read_file('user_data/address.txt')
        session = get_proxied_session(proxy=mobile_proxy)

        total_reward = 0
        for index, address in enumerate(addresses, start=1):
            reward = get_reward(session=session, address=address)
            if reward.value:
                value = round(float(reward.value), 2)
                total_reward += value
                logger.info(f"#{index} | {address}: {value} $TAIKO, cumulative: {round(total_reward, 2)} $TAIKO.")
            else:
                logger.warning(f"#{index} | {address}: not eligible.")
        logger.info(f'total reward: {round(total_reward, 2)} $TAIKO.')
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        logger.exception(e)
