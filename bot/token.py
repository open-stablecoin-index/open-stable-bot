import boa
import threading
from django.conf import settings
from boa.contracts.abi.abi_contract import ABIContractFactory

# Thread-local storage to ensure each thread has its own boa context
_thread_local = threading.local()

def _initialize_boa():
    """Initialize boa for the current thread if not already initialized"""
    if not hasattr(_thread_local, 'initialized'):
        boa.fork(settings.RPC, allow_dirty=True)
        _thread_local.initialized = True

def load_erc20(addr):
    _initialize_boa()
    erc20 = boa.load_vyi(f"{settings.BASE_DIR}/bot/erc20.vyi")
    return erc20.at(addr)

def get_squill_balance(addr):
    _initialize_boa()
    squill = load_erc20("0x7ebab7190d3d574ce82d29f2fa1422f18e29969c") 
    return(squill.balanceOf(addr)) 

def get_airdrop_balance(addr):
    _initialize_boa()
    squill_drop_abi = boa.load_abi(f"{settings.BASE_DIR}/bot/squilldrop.json")
    squill_drop = squill_drop_abi.at('0x0065780b1fe32927f14448446882f1261d936d12')
    return squill_drop.eligible_addresses(addr)
