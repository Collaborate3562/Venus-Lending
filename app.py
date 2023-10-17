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

BSC_RPC_URI = os.environ['BSC_RPC_URI']
OWNER_ADDRESS = os.environ['OWNER_ADDRESS']
OWNER_PRIVATE_KEY = os.environ['OWNER_PRIVATE_KEY']
COMPTROLLER_CONTRACT_ADDRESS = os.environ['COMPTROLLER_CONTRACT_ADDRESS']
VENUS_CAKE_ADDRESS = os.environ['VENUS_CAKE_ADDRESS']
VENUS_USDT_ADDRESS = os.environ['VENUS_USDT_ADDRESS']

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
        address=VENUS_CAKE_ADDRESS, abi=abi)
    
    abi = []
    with open("./abi/venus_cake_abi.json") as f:
        abi = json.load(f)

    global g_Venus_Cake_Contract
    g_Venus_Cake_Contract = g_Web3.eth.contract(
        address=VENUS_USDT_ADDRESS, abi=abi)

def checkMarketAssets() -> None:
    vTokens = g_Comptroller_Contract.functions.getAssetsIn(OWNER_ADDRESS).call()
    if not VENUS_CAKE_ADDRESS in vTokens or not VENUS_USDT_ADDRESS in vTokens:
        enterMarkets()
        
def supplyTether() -> None:
    None

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
        "gas": 500000,
        "gasPrice": g_Web3.to_wei('10', 'gwei')
    })
    
    signed_tx = g_Web3.eth.account.sign_transaction(call_function, private_key=OWNER_PRIVATE_KEY)
    send_tx = g_Web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    g_Web3.eth.wait_for_transaction_receipt(send_tx)
    print('Successfully assets registered.')

def main() -> None:
    getContract()
    checkMarketAssets()
    
main()