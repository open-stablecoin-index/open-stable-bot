import boa
from django.conf import settings

boa.fork(settings.RPC)

def load_erc20(addr):
    erc20 = boa.load_vyi(f"{settings.BASE_DIR}/bot/erc20.vyi")
    return erc20.at(addr)

def get_squill_balance(addr):
    squill = load_erc20("0x7ebab7190d3d574ce82d29f2fa1422f18e29969c") 
    return(squill.balanceOf(addr)) 

def get_airdrop_balance(addr):
    squill_drop_abi = boa.load_abi(f"{settings.BASE_DIR}/bot/squilldrop.json")
    squill_drop = squill_drop_abi.at('0x0065780b1fe32927f14448446882f1261d936d12')
    return squill_drop(addr)
