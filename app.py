import json
from json import JSONEncoder
from web3 import Web3, IPCProvider
from dotenv.main import load_dotenv
import os

load_dotenv()

g_Web3 = None
g_Comptroller_Contract = None
g_Venus_Cake_Contract = None
g_Venus_Usdt_Contract = None
g_Position_Manager_Contract = None
g_Cake_Contract = None
g_Usdt_Contract = None

MIN_SUPPLY_AMOUNT = 1.5
CAKE_PRICE = 1.06
BORROW_THERSHOLD = 0.8

TICK_LOWER = -500
TICK_UPPER = 1550
PANCAKE_V3_FEE = 2500

BSC_RPC_URI = os.environ['BSC_RPC_URI']
OWNER_ADDRESS = os.environ['OWNER_ADDRESS']
OWNER_PRIVATE_KEY = os.environ['OWNER_PRIVATE_KEY']
COMPTROLLER_CONTRACT_ADDRESS = os.environ['COMPTROLLER_CONTRACT_ADDRESS']
VENUS_CAKE_ADDRESS = os.environ['VENUS_CAKE_ADDRESS']
VENUS_USDT_ADDRESS = os.environ['VENUS_USDT_ADDRESS']
POSITION_MANAGER_ADDRESS = os.environ['POSITION_MANAGER_ADDRESS']
CAKE_ADDRESS = os.environ['CAKE_ADDRESS']
USDT_ADDRESS = os.environ['USDT_ADDRESS']

def getWeb3() -> None:
    global g_Web3
    g_Web3 = Web3(Web3.HTTPProvider(BSC_RPC_URI))

def getContract() -> None:
    getWeb3()
    
    abi = []
    with open("./abi/comptroller_abi.json") as f:
        abi = json.load(f)

    global g_Comptroller_Contract
    g_Comptroller_Contract = g_Web3.eth.contract(
        address=COMPTROLLER_CONTRACT_ADDRESS, abi=abi)
    
    abi = []
    with open("./abi/venus_usdt_abi.json") as f:
        abi = json.load(f)

    global g_Venus_Usdt_Contract
    g_Venus_Usdt_Contract = g_Web3.eth.contract(
        address=VENUS_USDT_ADDRESS, abi=abi)
    
    abi = []
    with open("./abi/venus_cake_abi.json") as f:
        abi = json.load(f)

    global g_Venus_Cake_Contract
    g_Venus_Cake_Contract = g_Web3.eth.contract(
        address=VENUS_CAKE_ADDRESS, abi=abi)
    
    abi = []
    with open("./abi/position_manager_abi.json") as f:
        abi = json.load(f)

    global g_Position_Manager_Contract
    g_Position_Manager_Contract = g_Web3.eth.contract(
        address=POSITION_MANAGER_ADDRESS, abi=abi)
    
    abi = []
    with open("./abi/erc20_abi.json") as f:
        abi = json.load(f)

    global g_Cake_Contract
    g_Cake_Contract = g_Web3.eth.contract(
        address=CAKE_ADDRESS, abi=abi)
    
    global g_Usdt_Contract
    g_Usdt_Contract = g_Web3.eth.contract(
        address=USDT_ADDRESS, abi=abi)

def checkMarketAssets() -> None:
    vTokens = g_Comptroller_Contract.functions.getAssetsIn(OWNER_ADDRESS).call()
    if not VENUS_CAKE_ADDRESS in vTokens or not VENUS_USDT_ADDRESS in vTokens:
        enterMarkets()
        
def supplyTether() -> None:
    nonce = g_Web3.eth.get_transaction_count(OWNER_ADDRESS)
    
    chain_id = g_Web3.eth.chain_id
    call_function = g_Venus_Usdt_Contract.functions.mint(g_Web3.to_wei(MIN_SUPPLY_AMOUNT, 'ether')).build_transaction({
        "chainId": chain_id,
        "from": OWNER_ADDRESS,
        "nonce": nonce,
        "gas": 300000,
        "gasPrice": g_Web3.to_wei('3', 'gwei')
    })
    
    signed_tx = g_Web3.eth.account.sign_transaction(call_function, private_key=OWNER_PRIVATE_KEY)
    send_tx = g_Web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    g_Web3.eth.wait_for_transaction_receipt(send_tx)
    print('Successfully supplied Tether.')
    
def borrowCake() -> None:
    nonce = g_Web3.eth.get_transaction_count(OWNER_ADDRESS)
    
    formatted_amount = "{:.3f}".format(MIN_SUPPLY_AMOUNT * BORROW_THERSHOLD / CAKE_PRICE)
    
    chain_id = g_Web3.eth.chain_id
    call_function = g_Venus_Cake_Contract.functions.borrow(g_Web3.to_wei(formatted_amount, 'ether')).build_transaction({
        "chainId": chain_id,
        "from": OWNER_ADDRESS,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": g_Web3.to_wei('3', 'gwei')
    })
    
    signed_tx = g_Web3.eth.account.sign_transaction(call_function, private_key=OWNER_PRIVATE_KEY)
    send_tx = g_Web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    g_Web3.eth.wait_for_transaction_receipt(send_tx)
    print('Successfully borrowed Cake.')

def enterMarkets() -> None:
    arr = []
    arr.append(Web3.to_checksum_address(VENUS_CAKE_ADDRESS))
    arr.append(Web3.to_checksum_address(VENUS_USDT_ADDRESS))
    
    nonce = g_Web3.eth.get_transaction_count(OWNER_ADDRESS)
    
    chain_id = g_Web3.eth.chain_id
    call_function = g_Comptroller_Contract.functions.enterMarkets(arr).build_transaction({
        "chainId": chain_id,
        "from": OWNER_ADDRESS,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": g_Web3.to_wei('3', 'gwei')
    })
    
    signed_tx = g_Web3.eth.account.sign_transaction(call_function, private_key=OWNER_PRIVATE_KEY)
    send_tx = g_Web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    g_Web3.eth.wait_for_transaction_receipt(send_tx)
    print('Successfully assets registered.')
    
def approveToken(token_contract: dict, spender: str, amount: str) -> None:
    nonce = g_Web3.eth.get_transaction_count(OWNER_ADDRESS)
    
    chain_id = g_Web3.eth.chain_id
    call_function = token_contract.functions.approve(spender, g_Web3.to_wei(amount, 'ether')).build_transaction({
        "chainId": chain_id,
        "from": OWNER_ADDRESS,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": g_Web3.to_wei('3', 'gwei')
    })
    
    signed_tx = g_Web3.eth.account.sign_transaction(call_function, private_key=OWNER_PRIVATE_KEY)
    send_tx = g_Web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    g_Web3.eth.wait_for_transaction_receipt(send_tx)
    print('Successfully approved token.')

def addLiquidity() -> None:
    # approveToken(g_Cake_Contract, POSITION_MANAGER_ADDRESS, '1')
    # approveToken(g_Usdt_Contract, POSITION_MANAGER_ADDRESS, '1.215')
    
    params = {
        "token0": CAKE_ADDRESS,
        "token1": USDT_ADDRESS,
        "fee": PANCAKE_V3_FEE,
        "tickLower": TICK_LOWER,
        "tickUpper": TICK_UPPER,
        "amount0Desired": g_Web3.to_wei('1', 'ether'),
        "amount1Desired": g_Web3.to_wei('1.215', 'ether'),
        'amount0Min': g_Web3.to_wei('0.946', 'ether'),
        'amount1Min': g_Web3.to_wei('1.158', 'ether'),
        'recipient': OWNER_ADDRESS,
        'deadline': 1697740471
    }
    
    nonce = g_Web3.eth.get_transaction_count(OWNER_ADDRESS)
    
    chain_id = g_Web3.eth.chain_id
    call_function = g_Position_Manager_Contract.functions.mint(params).build_transaction({
        "chainId": chain_id,
        "from": OWNER_ADDRESS,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": g_Web3.to_wei('3', 'gwei')
    })
    
    signed_tx = g_Web3.eth.account.sign_transaction(call_function, private_key=OWNER_PRIVATE_KEY)
    send_tx = g_Web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    g_Web3.eth.wait_for_transaction_receipt(send_tx)
    print('Successfully added liquidity.')

def main() -> None:
    getContract()
    # checkMarketAssets()
    # supplyTether()
    # borrowCake()
    
    addLiquidity()
    
main()