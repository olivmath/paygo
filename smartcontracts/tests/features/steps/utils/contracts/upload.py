from stellar_sdk.contract import ContractClient


def upload_wasm(context, wasm_bin, uploader_keypair):

    wasm_id = ContractClient.upload_contract_wasm(
        wasm_bin, uploader_keypair.public_key, uploader_keypair, context.soroban_server
    )
    print(f"contract wasm id: {wasm_id.hex()}")

    return wasm_id.hex()
