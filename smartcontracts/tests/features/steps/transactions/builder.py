from stellar_sdk import TransactionBuilder, Keypair
from .sender import send_tx


def upload_multiple_wasms(context, wasm_bin: list, uploader_keypair: Keypair):

    source_account = context.server.load_account(uploader_keypair.public_key)
    tx = TransactionBuilder(
        source_account=source_account,
        network_passphrase=context.network,
        base_fee=100,
    )

    for _, wasm in wasm_bin:
        tx.append_upload_contract_wasm_op(contract=wasm)

    tx.build()

    wasm_hash_list = send_tx(context, uploader_keypair, tx)

    print(wasm_hash_list)


def upload_wasm(context, wasm_bin, uploader_keypir: Keypair): ...


def deploy_contract(): ...


def invoke_function(): ...
