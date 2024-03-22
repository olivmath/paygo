"""
Cria uma ordem de compra de TOKENS
"""

from stellar_sdk import Keypair, Network, Server, TransactionBuilder, Asset

# Configurações iniciais
BOBPRIVATE_KEY = "SCXMBN6TNHYFN724ASTOVTTQTTHVDE72766SKNXZTHADRPP6D4AR5TWC"
bob_keypair = Keypair.from_secret(BOBPRIVATE_KEY)
horizon_server = Server("http://localhost:8000")
bob_account = horizon_server.load_account(bob_keypair.public_key)

# Configura o token e XLM como os ativos de compra e venda
token_asset = Asset("NRX", "GCYZHTQ2XKUXRLPPEJSUV4VUM5ST4SSKD3HT6N4ISQ2UOVJISZTNAWZJ")
native_asset = Asset.native()

args = {
    "selling": native_asset,
    "buying": token_asset,
    "amount": 1000,
    "price": 1,
    "source": bob_keypair.public_key,
}

transaction_args = {
    "source_account": bob_account,
    "network_passphrase": Network.STANDALONE_NETWORK_PASSPHRASE,
    "base_fee": 100,
}

buy_order_transaction = (
    TransactionBuilder(**transaction_args)
    .append_change_trust_op(
        asset=token_asset,
        limit=1000,
        source=bob_keypair.public_key,
    )
    .append_manage_buy_offer_op(**args)
    .set_timeout(30)
    .build()
)

buy_order_transaction.sign(bob_keypair)
response = horizon_server.submit_transaction(buy_order_transaction)
print("✅ Ordem de compra criada com sucesso!")


"""
Cria uma ordem de venda TOKENS
"""

from stellar_sdk import Keypair, Network, Server, TransactionBuilder, Asset

# Configurações iniciais
ALICE_PRIVATE_KEY = "SDLXNGAV34DZJMUO3MZMDQLUWQPFY6J3JVVG77T2G7VA3HJYETBEBVZO"
# CONTRACT_ID = input("👉 Enter contract id: ")
alice_keypair = Keypair.from_secret(ALICE_PRIVATE_KEY)
horizon_server = Server("http://localhost:8000")
alice_account = horizon_server.load_account(alice_keypair.public_key)

# Configura o token e XLM como os ativos de venda e compra
token_asset = Asset("NRX", alice_keypair.public_key)
native_asset = Asset.native()

order = {
    "selling": token_asset,
    "buying": native_asset,
    "amount": 1000,
    "price": 1,
    "source": alice_keypair.public_key,
}

transaction_args = {
    "source_account": alice_account,
    "network_passphrase": Network.STANDALONE_NETWORK_PASSPHRASE,
    "base_fee": 100,
}

sell_order_transaction = (
    TransactionBuilder(**transaction_args)
    .append_manage_sell_offer_op(**order)
    .set_timeout(30)
    .build()
)

sell_order_transaction.sign(alice_keypair)
response = horizon_server.submit_transaction(sell_order_transaction)
print("✅ Ordem de venda criada com sucesso!", response["hash"])

import balances