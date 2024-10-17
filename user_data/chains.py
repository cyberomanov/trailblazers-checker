from pydantic import BaseModel


class ChainItem(BaseModel):
    name: str
    id: int
    orbiter_code: int
    rpc: str
    explorer: str

    def __hash__(self):
        return hash((self.name, self.id, self.orbiter_code, self.rpc, self.explorer))


source_chains = [
    ChainItem(
        name='opt',
        id=10,
        orbiter_code=9007,
        rpc='https://rpc.ankr.com/optimism',
        explorer='https://optimistic.etherscan.io/tx'
    ),
    ChainItem(
        name='arb',
        id=42161,
        orbiter_code=9002,
        rpc='https://rpc.ankr.com/arbitrum',
        explorer='https://arbiscan.io/tx'
    ),
    ChainItem(
        name='base',
        id=8453,
        orbiter_code=9021,
        rpc='https://rpc.ankr.com/base',
        explorer='https://basescan.org/tx'
    )
]