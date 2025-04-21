import json
from web3 import Web3
from django.conf import settings

MIN_PRICE = 100

# Initialize Web3
def get_web3():
    return Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{settings.INFURA_API_KEY}'))

def get_fraxtal():
    return Web3(Web3.HTTPProvider(f'https://rpc.frax.com'))

# ERC20 ABI - common interface for token contracts
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

# Load the SQUILLDROP ABI from file
def get_squilldrop_abi():
    with open(f"{settings.BASE_DIR}/bot/squilldrop.json", 'r') as file:
        return json.load(file)


# Resolve ENS name to address
def resolve_ens(ens_name):
    w3 = get_web3()
    return w3.ens.address(ens_name)

# Check if a string is a valid Ethereum address
def is_valid_eth_address(address):
    w3 = get_web3()
    try:
        w3.to_checksum_address(address)
        return True
    except ValueError:
        return False

# Get token information (symbol, decimals)
def get_token_info(token_address):
    w3 = get_web3()
    checksum_address = w3.to_checksum_address(token_address)
    token_contract = w3.eth.contract(address=checksum_address, abi=ERC20_ABI)
    
    try:
        symbol = token_contract.functions.symbol().call()
        decimals = token_contract.functions.decimals().call()
        return {
            'symbol': symbol,
            'decimals': decimals
        }
    except Exception as e:
        return {
            'symbol': 'UNKNOWN',
            'decimals': 18,
            'error': str(e)
        }


def gatekeep(addr):
    w3 = get_web3()
    eth_address = w3.to_checksum_address(addr)

    squill_check, squill_reason = check_squill_balance(eth_address)
    if squill_check:
        return True, squill_reason 

    rsr_check, rsr_reason = check_rsr_balance(eth_address)
    if rsr_check:
        return True, rsr_reason

    squid_check, squid_reason = check_squid_balance(eth_address)
    if squid_check:
        return True, squid_reason

    airdrop_bal = get_airdrop_balance(eth_address)
    if airdrop_bal > 10 ** 18:
        return False, f"HINT: Try <a href='https://leviathannews.substack.com/p/leviathan-launches-squill'>claiming your SQUILL-drop</a> and rerunning this command"

    return False, f"Entry requires your wallet holds at least ${MIN_PRICE} worth of <a href='https://leviathannews.substack.com/p/leviathan-launches-squill'>$SQUILL</a>, <a href='https://leviathannews.substack.com/p/leviathan-news-squid-token-the-ultimate'>$SQUID</a> or <a href='https://www.coingecko.com/en/coins/reserve-rights'>$RSR</a>.  Click on the token links for more info."
   

def get_token_balance(w3, address, token):
    token_addr = w3.to_checksum_address(token)
    token_contract = w3.eth.contract(address=token_addr, abi=ERC20_ABI)
    return token_contract.functions.balanceOf(address).call()

def format_token_bal(val, symbol):
    return f"{val/10 ** 18:,.0f} ${symbol}"

def check_squill_balance(address):
    squill_addr = "0x7ebab7190d3d574ce82d29f2fa1422f18e29969c"
    bal = get_token_balance(get_web3(), address, squill_addr)
    return (bal > 0), format_token_bal(bal, "SQUILL")

def check_rsr_balance(address):
    rsr_price = .006 * 10 ** 18
    rsr_addr = "0x320623b8e4ff03373931769a31fc52a4e78b5d70"
    bal = get_token_balance(get_web3(), address, rsr_addr)
    return (bal > MIN_PRICE * rsr_price), format_token_bal(bal, "RSR")

def check_squid_balance(address):
    squid_price = .014 * 10 ** 18
    squid_addr = "0x6e58089d8e8f664823d26454f49a5a0f2ff697fe"
    fraxtal = get_fraxtal()

    # Naked SQUID
    bal = get_token_balance(fraxtal, address, squid_addr)
    if bal > MIN_PRICE * squid_price:
        return True, format_token_bal(bal, "SQUID")

    # 1 LP token == $10
    squid_lp = '0x277FA53c8a53C880E0625c92C92a62a9F60f3f04'
    lp_bal = get_token_balance(fraxtal, address, squid_lp)
    if lp_bal > (MIN_PRICE / 10) * 10 ** 18:
        return True, format_token_bal(lp_bal, "SQUID LP")

    squid_gauge = '0xe5E5ed1B50AE33E66ca69dF17Aa6381FDe4e9C7e'
    gauge_bal = get_token_balance(fraxtal, address, squid_gauge)
    if gauge_bal > (MIN_PRICE / 10) * 10 ** 18:
        return True, format_token_bal(gauge_bal, "SQUID Gauge")

    squid_cvx = '0x29FF8F9ACb27727D8A2A52D16091c12ea56E9E4d'
    cvx_bal = get_token_balance(fraxtal, address, squid_cvx)
    if cvx_bal > (MIN_PRICE / 10) * 10 ** 18:
        return True, format_token_bal(cvx_bal, "SQUID Convex")

    return False, "Insufficient SQUID"

def get_airdrop_balance(address):
    w3 = get_web3()
    squilldrop_address = w3.to_checksum_address("0x0065780b1fe32927f14448446882f1261d936d12")
    squilldrop_contract = w3.eth.contract(address=squilldrop_address, abi=get_squilldrop_abi())
    return squilldrop_contract.functions.eligible_addresses(address).call()

