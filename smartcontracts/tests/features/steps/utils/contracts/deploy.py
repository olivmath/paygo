from stellar_sdk.contract import ContractClient


def deploy_wasm(context, wasm_id: str, deployer_keypair, init_args):
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


def deploy_wasm_via_cli(wasm_id: str, deployer_keypair, init_args):
    import subprocess

    print(f"\n🚀 Deploying contract...")
    command = [
        "stellar",
        "contract",
        "deploy",
        "--wasm-hash",
        wasm_id,
        "--source",
        deployer_keypair.secret,
        "--",
        *init_args,
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        contract_id = result.stdout.strip()

        print(f"✅ Contract deployed successfully!")
        print(f"Contract ID: {contract_id}")
        return contract_id

    except Exception as e:
        print(f"❌ Failed to deploy contract")
        raise Exception(f"Failed to deploy contract: {str(e)}")
