import logging
from stellar_sdk import Network, SorobanServer

def start_stellar_node():
    """Start the Stellar node container"""
    pass  # Implemente conforme necessário

def stop_stellar_node():
    """Stop the Stellar node container"""
    pass  # Implemente conforme necessário

def before_all(context):
    """Configuração global antes de todos os testes"""
    # Configuração do ambiente
    context.stellar_url = "http://localhost:8000"
    context.network_passphrase = Network.STANDALONE_NETWORK_PASSPHRASE
    context.wallets = {}
    context.contracts = {}
    context.contracts["wasm_hash"] = {}
    context.contracts["contract_id"] = {}
    context.soroban_server = SorobanServer("http://localhost:8000/soroban/rpc")

def after_all(context):
    # Cleanup global após todos os testes
    stop_stellar_node()

def before_feature(context, feature):
    # Setup antes de cada feature
    ...

def after_feature(context, feature):
    # Cleanup após cada feature
    ...

def before_scenario(context, scenario):
    # Reset antes de cada cenário
    context.employees = []
    context.admin_keypair = None
    context.owner_keypair = None
    context.company_contract_hash = None
    context.usdc_contract_id = None
    context.paygo_contract_id = None
    context.company_account_id = None

def after_scenario(context, scenario):
    # Cleanup após cada cenário
    ...