import json
from web3 import Web3
from django.conf import settings

# Initialize Web3
def get_web3():
    return Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{settings.INFURA_API_KEY}'))

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

# Get SQUILL token balance
def get_squill_balance(address):
    w3 = get_web3()
    # Convert address to checksum format
    checksum_address = w3.to_checksum_address(address)
    # SQUILL token contract address
    squill_address = w3.to_checksum_address("0x7ebab7190d3d574ce82d29f2fa1422f18e29969c")
    # Create contract instance
    squill_contract = w3.eth.contract(address=squill_address, abi=ERC20_ABI)
    # Call balanceOf function
    return squill_contract.functions.balanceOf(checksum_address).call()

# Get airdrop balance
def get_airdrop_balance(address):
    w3 = get_web3()
    # Convert address to checksum format
    checksum_address = w3.to_checksum_address(address)
    # SQUILL drop contract address
    squilldrop_address = w3.to_checksum_address("0x0065780b1fe32927f14448446882f1261d936d12")
    # Create contract instance
    squilldrop_contract = w3.eth.contract(address=squilldrop_address, abi=get_squilldrop_abi())
    # Call eligible_addresses function
    return squilldrop_contract.functions.eligible_addresses(checksum_address).call()

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
