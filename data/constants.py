from datatypes.crypto import ChainItem, Token
from user_data.config import taiko_rpc

taiko_chain = ChainItem(
    name='taiko',
    id=167000,
    rpc=taiko_rpc,
    explorer='https://taikoscan.io/tx',
    orbiter_code=9020
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

CLAIM_CONTRACT = "0x95345D5A092623D79a56a016001f7878FA9Da3Ef"
ORBITER_CONTRACT = "0xe4edb277e41dc89ab076a1f049f4a3efa700bce8"
XY_CONTRACTS = {
    'opt': "0x7a6e01880693093abACcF442fcbED9E0435f1030",
    'eth': "0x4315f344a905dC21a08189A117eFd6E1fcA37D57",
    'arb': "0x33383265290421C704c6b09F4BF27ce574DC4203",
    'scroll': "0x778C974568e376146dbC64fF12aD55B2d1c4133f",
    'linea': "0x73Ce60416035B8D7019f6399778c14ccf5C9c7A1",
    'base': "0x73Ce60416035B8D7019f6399778c14ccf5C9c7A1",
    'taiko': "0x73Ce60416035B8D7019f6399778c14ccf5C9c7A1"
}
XY_AGGREGATOR_CONTRACT = "0x18b1751a6f4ec773faf8e1a24ed0c3b271e538c"
ETH_CONTRACT = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
