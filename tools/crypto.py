import time
from decimal import Decimal

from loguru import logger
from web3 import Web3
from web3.exceptions import TimeExhausted

from data.constants import taiko_chain, CLAIM_CONTRACT, taiko_token, ORBITER_CONTRACT, XY_CONTRACTS, \
    XY_AGGREGATOR_CONTRACT, ETH_CONTRACT
from datatypes.crypto import Balance
from user_data.chains import ChainItem
from user_data.config import gas_multiplier


def get_balance(address: str, rpc: str):
    web3 = Web3(Web3.HTTPProvider(rpc))
    balance = web3.eth.get_balance(web3.to_checksum_address(address))
    return Balance(
        int=balance,
        float=round(web3.from_wei(balance, 'ether'), 6)
    )


def get_balance_of(contract: str, address: str, rpc: str, denomination: int = 10 ** 18):
    web3 = Web3(Web3.HTTPProvider(rpc))
    abi = '''
    [
        {
            "constant":true,
            "inputs":[{"name":"_owner","type":"address"}],
            "name":"balanceOf",
            "outputs":[{"name":"balance","type":"uint256"}],
            "type":"function"
        }
    ]
    '''

    token_contract = web3.eth.contract(address=web3.to_checksum_address(contract), abi=abi)
    balance = token_contract.functions.balanceOf(web3.to_checksum_address(address)).call()

    return Balance(
        int=balance,
        float=round(balance / denomination, 8)
    )


def sign_and_wait(w3: Web3, transaction: {}, private_key: str, timeout: int = 120):
    account = w3.eth.account.from_key(private_key)
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    try:
        txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(txn_hash, timeout=timeout)

        if receipt.status == 1:
            return txn_hash.hex()
        else:
            return None
    except TimeExhausted:
        logger.error(f"{account.address}: {txn_hash.hex()} not confirmed in {timeout} seconds.")
        return None
    except ValueError as e:
        logger.error(f"{account.address}: {e.args[0]}.")


def get_gas(w3: Web3()):
    latest_block = w3.eth.block_number
    fee_history = w3.eth.fee_history(1, latest_block, reward_percentiles=[50])
    base_fee_per_gas1 = fee_history['baseFeePerGas'][0]
    max_priority_fee_per_gas = int(fee_history['reward'][0][0] * 1.1)

    max_fee_per_gas = int(base_fee_per_gas1 + max_priority_fee_per_gas * 1.1)

    base_fee_per_gas2 = w3.eth.get_block('latest')['baseFeePerGas']
    if int(base_fee_per_gas2) > max_fee_per_gas:
        max_fee_per_gas = int(base_fee_per_gas2 * 1.1)

    return int(max_priority_fee_per_gas), int(max_fee_per_gas)


def pad_to_32_bytes(value):
    return value.rjust(64, '0')


def claim_taiko_tx(private_key: str, amount: float, proof: str, args: int):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    claim_contract = w3.to_checksum_address(CLAIM_CONTRACT)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    amount_int = int(Decimal(str(amount)) * Decimal(taiko_token.denomination))
    data = "0x3d13f874" + \
           pad_to_32_bytes(account.address[2:].lower()) + \
           pad_to_32_bytes(hex(amount_int)[2:]) + \
           pad_to_32_bytes("60") + pad_to_32_bytes(str(args)) + proof

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': claim_contract,
            'value': 0,
            'data': data
        }) * 1.1)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": claim_contract,
            "value": 0,
            "data": data,
            "gas": gas_limit,
            "maxFeePerGas": max_fee_per_gas,
            "maxPriorityFeePerGas": max_priority_fee_per_gas,
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        if '0x83b9ec9b' in str(e):
            return 'already claimed'
        else:
            logger.exception(e)


def transfer_token_tx(private_key: str, recipient_address: str, amount: int):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    token_abi = [
        {
            "constant": False,
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        }
    ]

    token_contract = w3.eth.contract(address=w3.to_checksum_address(taiko_token.address), abi=token_abi)

    tx_data = token_contract.functions.transfer(
        w3.to_checksum_address(recipient_address),
        amount
    ).build_transaction({
        'chainId': taiko_chain.id,
        'from': account.address,
        'nonce': nonce,
        'value': 0,
    })

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': w3.to_checksum_address(taiko_token.address),
            'value': 0,
            'data': tx_data['data']
        }) * 3)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": w3.to_checksum_address(taiko_token.address),
            "value": 0,
            "data": tx_data['data'],
            "gas": gas_limit,
            "maxFeePerGas": max_fee_per_gas,
            "maxPriorityFeePerGas": max_priority_fee_per_gas,
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        logger.exception(e)


def orbiter_bridge_tx(
        private_key: str,
        source_chain: ChainItem,
        recipient_chain: ChainItem,
        amount_to_bridge: float
):
    w3 = Web3(Web3.HTTPProvider(source_chain.rpc))
    orbiter_recipient = w3.to_checksum_address(ORBITER_CONTRACT)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': orbiter_recipient,
        'value': Web3.to_wei(amount_to_bridge, 'ether') + recipient_chain.orbiter_code,
        'data': '0x'
    }) * gas_multiplier)

    transaction = {
        "chainId": source_chain.id,
        "from": account.address,
        "to": orbiter_recipient,
        "value": Web3.to_wei(amount_to_bridge, 'ether') + recipient_chain.orbiter_code,
        "data": "0x",
        "gas": gas_limit,
        "maxFeePerGas": max_fee_per_gas * gas_multiplier,
        "maxPriorityFeePerGas": max_priority_fee_per_gas * gas_multiplier,
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def xy_bridge_tx(
        private_key: str,
        source_chain: ChainItem,
        recipient_chain: ChainItem,
        amount_to_bridge: float
):
    w3 = Web3(Web3.HTTPProvider(source_chain.rpc))
    recipient = w3.to_checksum_address(XY_CONTRACTS[source_chain.name])

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    method = '0xcdc65927'
    data = method + \
           pad_to_32_bytes('0').lower() + \
           pad_to_32_bytes(ETH_CONTRACT[2:]).lower() + \
           pad_to_32_bytes(ETH_CONTRACT[2:]).lower() + \
           pad_to_32_bytes(account.address[2:]).lower() + \
           pad_to_32_bytes(hex(int(amount_to_bridge * 10 ** 18))[2:]).lower() + \
           pad_to_32_bytes(hex(int(amount_to_bridge * 10 ** 18))[2:]).lower() + \
           pad_to_32_bytes('1a0').lower() + \
           pad_to_32_bytes(hex(recipient_chain.id)[2:]).lower() + \
           pad_to_32_bytes(ETH_CONTRACT[2:]).lower() + \
           pad_to_32_bytes('0').lower() + \
           pad_to_32_bytes(hex(int(amount_to_bridge * 0.9 * 10 ** 18))[2:]).lower() + \
           pad_to_32_bytes('64').lower() + \
           pad_to_32_bytes(XY_AGGREGATOR_CONTRACT[2:]).lower() + \
           pad_to_32_bytes('1').lower() + \
           pad_to_32_bytes('0').lower()

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': Web3.to_wei(amount_to_bridge, 'ether'),
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": source_chain.id,
        "from": account.address,
        "to": recipient,
        "value": Web3.to_wei(amount_to_bridge, 'ether'),
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": max_fee_per_gas * gas_multiplier,
        "maxPriorityFeePerGas": max_priority_fee_per_gas * gas_multiplier,
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def wait_for_new_balance(address: str, old_balance: Balance, chain: ChainItem) -> Balance:
    tries = 0
    while True:
        new_recipient_balance = get_balance(address=address, rpc=chain.rpc)

        if new_recipient_balance.float != old_balance.float:
            return new_recipient_balance
        else:
            tries += 1
            if tries > 600:
                return new_recipient_balance
            time.sleep(1)
