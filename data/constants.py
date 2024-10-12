from datatypes.crypto import ChainItem, Token
from user_data.config import taiko_rpc

taiko_chain = ChainItem(
    name='taiko',
    id=167000,
    rpc=taiko_rpc,
    explorer='https://taikoscan.io/tx'
)


eth_token = Token(
    address='0x0000000000000000000000000000000000000000',
    ticker='ETH',
    denomination=10 ** 18
)

taiko_token = Token(
    address='0xa9d23408b9ba935c230493c40c73824df71a0975',
    ticker='TAIKO',
    denomination=10 ** 18
)


CLAIM_CONTRACT = "0x290265ACd21816EE414E64eEC77dd490d8dd9f51"
