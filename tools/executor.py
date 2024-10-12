import ast

import requests
from loguru import logger
from web3 import Web3

from data.constants import taiko_chain, taiko_token
from tools.crypto import claim_taiko_tx, get_balance_of, transfer_token_tx
from tools.other_utils import get_reward, sleep_in_range
from user_data.config import sleep_between_accounts


def single_executor(index: int, line: str, session: requests.Session()):
    private_key, recipient_address = line.split('##')

    address = Web3(Web3.HTTPProvider()).eth.account.from_key(private_key).address
    reward = get_reward(session=session, address=address)

    if reward.value:
        value = round(float(reward.value), 2)
        proof = "".join(address[2:] for address in ast.literal_eval(reward.proof))
        logger.success(f"#{index} | {address} | {value} $TAIKO.")

        claim_tx = claim_taiko_tx(private_key=private_key, amount=value, proof=proof)
        if claim_tx:
            if "already claimed" in claim_tx:
                logger.warning(f"#{index} | {address} | claim_tx | already claimed.")
            else:
                logger.info(f"#{index} | {address} | claim_tx | {taiko_chain.explorer}/{claim_tx}")
                sleep_in_range(sec_from=sleep_between_accounts[0], sec_to=sleep_between_accounts[1])

        taiko_balance = get_balance_of(address=address, rpc=taiko_chain.rpc, contract=taiko_token.address)
        if taiko_balance.int:
            transfer_tx = transfer_token_tx(
                private_key=private_key, amount=taiko_balance.int, recipient_address=recipient_address
            )
            if transfer_tx:
                logger.info(
                    f"#{index} | {address} | "
                    f"transfer {taiko_balance.float} $TAIKO -> {recipient_address} | "
                    f"{taiko_chain.explorer}/{transfer_tx}"
                )
                sleep_in_range(sec_from=sleep_between_accounts[0], sec_to=sleep_between_accounts[1], log=True)
        else:
            logger.warning(
                f"#{index} | {address} | "
                f"transfer_tx | nothing to transfer: {taiko_balance.float} $TAIKO."
            )

    else:
        logger.warning(f"#{index} | {address}: not eligible.")
