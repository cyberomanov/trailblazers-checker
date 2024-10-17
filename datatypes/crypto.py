from pydantic import BaseModel


class Balance(BaseModel):
    int: int
    float: float


class ChainItem(BaseModel):
    name: str
    id: int
    rpc: str
    explorer: str
    orbiter_code: int

    def __hash__(self):
        return hash((self.name, self.id, self.rpc, self.explorer))


class Token(BaseModel):
    address: str
    ticker: str
    denomination: int
