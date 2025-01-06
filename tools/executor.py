import ast
import random

import requests
from loguru import logger
from web3 import Web3

from data.constants import taiko_chain, taiko_token
from modules.orbiter import orbiter_bridge
from modules.xy import xy_bridge
from tools.change_ip import execute_change_ip
from tools.crypto import claim_taiko_tx, get_balance_of, transfer_token_tx, get_balance, simulate_claim_taiko_tx
from tools.other_utils import get_reward, sleep_in_range
from user_data import config, chains
from user_data.chains import ChainItem
from user_data.config import sleep_between_accounts


def bridge_deposit(
        index: int,
        address: str,
        private_key: str,
        source_chains: [ChainItem]):
    source_chain = None
    amount_to_bridge = 0

    for chain in source_chains:
        chain_balance = get_balance(address=address, rpc=chain.rpc)
        if chain_balance.float > config.deposit_to_taiko_amount[1]:
            source_chain = chain
            amount_to_bridge = round(
                random.uniform(config.deposit_to_taiko_amount[0], config.deposit_to_taiko_amount[1]),
                random.randint(5, 8)
            )
            break

    if source_chain:
        bridge_to_use = random.choice(config.bridges_to_use)
        if 'orbiter' in bridge_to_use:
            orbiter_bridge(
                index=index,
                private_key=private_key,
                source_chain=chain,
                recipient_chain=taiko_chain,
                amount_to_bridge=amount_to_bridge
            )
        elif 'xy' in bridge_to_use:
            xy_bridge(
                index=index,
                private_key=private_key,
                source_chain=chain,
                recipient_chain=taiko_chain,
                amount_to_bridge=amount_to_bridge
            )
    else:
        logger.info(f"#{index} | {address}: no chain with balance > {config.deposit_to_taiko_amount[1]} $ETH.")


def single_executor(index: int, line: str, session: requests.Session()):
    try:
        if '##' in line:
            private_key, recipient_address = line.split('##')
        else:
            private_key = line
            recipient_address = ''

        address = Web3(Web3.HTTPProvider()).eth.account.from_key(private_key).address

        if config.change_ip_url:
            change_ip = execute_change_ip(change_ip_url=config.change_ip_url)
            if change_ip:
                logger.info(f"#{index} | {address} | ip has been changed.")
            else:
                logger.error(f"#{index} | {address} | ip has not been changed.")
                return

        reward = get_reward(session=session, address=address)

        if reward.value:
            value = round(float(reward.value), 2)
            proof_list = ast.literal_eval(reward.proof)
            proof = "".join(address[2:] for address in proof_list)
            logger.success(f"#{index} | {address} | {value} $TAIKO.")

            simulate = simulate_claim_taiko_tx(
                private_key=private_key, amount=value, proof=proof, args=len(proof_list) - 6
            )
            if 'already claimed' not in simulate:
                if config.deposit_from_source_chains:
                    taiko_eth_balance = get_balance(address=address, rpc=taiko_chain.rpc)
                    if taiko_eth_balance.float < config.deposit_to_taiko_amount[0]:
                        bridge_deposit(
                            index=index,
                            address=address,
                            private_key=private_key,
                            source_chains=chains.source_chains
                        )

                claim_tx = claim_taiko_tx(private_key=private_key, amount=value, proof=proof, args=len(proof_list) - 6)
                if claim_tx:
                    if "already claimed" in claim_tx:
                        logger.warning(f"#{index} | {address} | claim_tx | already claimed.")
                    else:
                        logger.info(f"#{index} | {address} | claim_tx | {taiko_chain.explorer}/{claim_tx}")
                        sleep_in_range(sec_from=31, sec_to=61)

                if recipient_address:
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
                            sleep_in_range(sec_from=sleep_between_accounts[0], sec_to=sleep_between_accounts[1],
                                           log=True)
                    else:
                        logger.warning(
                            f"#{index} | {address} | "
                            f"transfer_tx | nothing to transfer: {taiko_balance.float} $TAIKO."
                        )

            else:
                logger.warning(f"#{index} | {address} | claim_tx | already claimed.")
        else:
            logger.warning(f"#{index} | {address}: not eligible.")
    except Exception as e:
        logger.exception(e)
