from loguru import logger
from web3 import Web3

from tools.crypto import get_balance, orbiter_bridge_tx, wait_for_new_balance
from user_data.chains import ChainItem


def orbiter_bridge(
        index: int,
        private_key: str,
        source_chain: ChainItem,
        recipient_chain: ChainItem,
        amount_to_bridge: float
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_source_balance = get_balance(address=account.address, rpc=source_chain.rpc)
    old_recipient_balance = get_balance(address=account.address, rpc=recipient_chain.rpc)

    logger.info(f'#{index} | {account.address}: {old_source_balance.float} $ETH on {source_chain.name}, '
                f'{amount_to_bridge} $ETH to bridge to {recipient_chain.name}.')

    bridge_tx = orbiter_bridge_tx(
        private_key=private_key,
        source_chain=source_chain,
        recipient_chain=recipient_chain,
        amount_to_bridge=amount_to_bridge
    )
    if bridge_tx:
        new_recipient_balance = wait_for_new_balance(
            old_balance=old_recipient_balance,
            address=account.address,
            chain=recipient_chain
        )
        logger.info(f'#{index} | {account.address}: orbiter | {source_chain.explorer}/{bridge_tx}')
    else:
        logger.error(f'#{index} | {account.address}: orbiter tx has failed.')
