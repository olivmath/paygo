from stellar_sdk import Keypair, scval
from stellar_sdk.contract import ContractClient


def deploy_wasm(context, wasm_id: str, deployer_keypair: Keypair, init_args):
    """
    Deploy a WASM contract with initialization arguments

    Args:
        context: Behave context
        wasm_id: WASM hash ID
        deployer_keypair: Keypair of the deployer
        init_args: List of SCVal arguments for contract initialization
    """
    print(f"\n🚀 Deploying contract...")
    try:
        contract_id = ContractClient.create_contract(
            wasm_id,
            deployer_keypair.public_key,
            deployer_keypair,
            context.soroban_server,
            init_args,
        )
        print(f"✅ Contract deployed successfully!")
        print(f"Contract ID: {contract_id}")
        return contract_id

    except Exception as e:
        print(f"❌ Failed to deploy contract")
        raise Exception(f"Failed to deploy contract: {str(e)}")
