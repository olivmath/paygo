from behave import given

from stellar_sdk import (
    Keypair,
    SorobanServer,
    TransactionBuilder,
    StrKey,
    xdr as stellar_xdr,
)
from stellar_sdk.soroban_rpc import GetTransactionStatus, SendTransactionStatus
from stellar_sdk.exceptions import PrepareTransactionException
import subprocess
import os


def build_contract(contract_path: str) -> None:
    """Build a contract using cargo"""
    try:
        subprocess.run(
            ["cargo", "build", "--target", "wasm32-unknown-unknown", "--release"],
            cwd=contract_path,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        raise AssertionError(f"Failed to build contract {contract_path}: {e.stderr}")


def get_wasm_path(contract_path: str) -> str:
    """Get the path to the compiled WASM file"""
    contract_name = contract_path.split("/")[-1]
    workspace_root = os.path.abspath(os.path.join(contract_path, "../../"))
    wasm_path = os.path.join(
        workspace_root,
        "target/wasm32-unknown-unknown/release",
        f"{contract_name}.wasm",
    )
    return os.path.normpath(wasm_path)


def upload_wasm_via_sdk(context, wasm_path: str, admin_keypair: Keypair) -> str:
    """Upload contract WASM to Stellar network

    Args:
        context: Behave context containing server info
        wasm_path: Path to the WASM file
        admin_keypair: Keypair of the admin account

    Returns:
        str: The WASM ID of the uploaded contract
    """

    # Read contract binary
    f = open("target/wasm32-unknown-unknown/release/company.wasm", "rb")
    contract_bin = f.read()
    f.close()

    # Build transaction
    source_account = context.server.load_account(admin_keypair.public_key)
    tx = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=context.network,
            base_fee=100,
        )
        .set_timeout(300)
        .append_upload_contract_wasm_op(contract=contract_bin)
        .build()
    )

    # Prepare and sign transaction
    try:
        tx = context.soroban_server.prepare_transaction(tx)
    except PrepareTransactionException as e:
        raise Exception(
            f"Failed to prepare transaction: {e.simulate_transaction_response}"
        )
        tx.sign(admin_keypair)

    # Send transaction
    try:
        response = context.soroban_server.send_transaction(tx)
        if response.status != SendTransactionStatus.PENDING:
            raise Exception(f"Failed to send transaction: {response.status}")
    except Exception as e:
        raise Exception(f"Error sending transaction: {str(e)}")

    # Wait for confirmation and get WASM ID
    get_transaction_data = context.soroban_server.get_transaction(response.hash)
    while get_transaction_data.status == GetTransactionStatus.NOT_FOUND:
        get_transaction_data = context.soroban_server.get_transaction(response.hash)

    if get_transaction_data.status == GetTransactionStatus.SUCCESS:
        transaction_meta = stellar_xdr.TransactionMeta.from_xdr(
            get_transaction_data.result_meta_xdr
        )
        wasm_hash = transaction_meta.v3.soroban_meta.return_value.bytes.sc_bytes.hex()
        return wasm_hash
    else:
        raise Exception(f"Transaction failed: {get_transaction_data.result_xdr}")


def create_wasm_sdk(context, wasm_hash: str, admin_keypair: Keypair) -> str:
    """Create contract instance from uploaded WASM

    Args:
        context: Behave context containing server info
        wasm_hash: WASM ID from uploaded contract
        admin_keypair: Keypair of the admin account

    Returns:
        str: The contract ID of the created instance
    """
    soroban_server = SorobanServer(context.stellar_url)

    # Build transaction
    source_account = context.server.load_account(admin_keypair.public_key)
    tx = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=context.network,
            base_fee=100,
        )
        .set_timeout(300)
        .append_create_contract_op(
            wasm_hash=wasm_hash, address=admin_keypair.public_key
        )
        .build()
    )

    # Prepare and sign transaction
    try:
        tx = soroban_server.prepare_transaction(tx)
        tx.sign(admin_keypair)
    except PrepareTransactionException as e:
        raise Exception(
            f"Failed to prepare transaction: {e.simulate_transaction_response}"
        )

    # Send transaction
    try:
        response = soroban_server.send_transaction(tx)
        if response.status != SendTransactionStatus.PENDING:
            raise Exception(f"Failed to send transaction: {response.status}")
    except Exception as e:
        raise Exception(f"Error sending transaction: {str(e)}")

    # Wait for confirmation and get contract ID
    get_transaction_data = soroban_server.get_transaction(response.hash)
    while get_transaction_data.status == GetTransactionStatus.NOT_FOUND:
        get_transaction_data = soroban_server.get_transaction(response.hash)

    if get_transaction_data.status == GetTransactionStatus.SUCCESS:
        transaction_meta = stellar_xdr.TransactionMeta.from_xdr(
            get_transaction_data.result_meta_xdr
        )
        result = transaction_meta.v3.soroban_meta.return_value.address.contract_id.hash
        contract_id = StrKey.encode_contract(result)
        return contract_id
    else:
        raise Exception(f"Transaction failed: {get_transaction_data.result_xdr}")


def upload_wasm_via_cli(context, wasm_path: str, admin_keypair: Keypair) -> str:
    """Upload contract WASM to Stellar network using CLI

    Args:
        wasm_path: Path to the WASM file
        admin_keypair: Keypair of the admin account

    Returns:
        str: The WASM ID of the uploaded contract
    """
    # Build the command to upload the WASM file using Stellar CLI
    command = [
        "stellar",
        "contract",
        "upload",
        "--wasm",
        wasm_path,
        "--source",
        admin_keypair.secret,
    ]

    # Execute the command
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        wasm_hash = result.stdout.strip()
        return wasm_hash
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to upload WASM: {e.stderr}")


def create_wasm_cli(
    context, wasm_hash: str, admin_keypair: Keypair, *args: list[str]
) -> str:
    """Create contract instance from uploaded WASM using CLI

    Args:
        wasm_hash: WASM ID from uploaded contract
        admin_keypair: Keypair of the admin account

    Returns:
        str: The contract ID of the created instance
    """

    # Build the command to create the contract instance
    command = [
        "stellar",
        "contract",
        "deploy",
        "--wasm-hash",
        wasm_hash,
        "--source",
        admin_keypair.secret,
        "--",
        *args,
    ]

    # Execute the command
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        contract_id = result.stdout.strip()
        return contract_id
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to create contract: {e.stderr}")


@given("all contracts are successfully compiled")
def step_compile_contracts(context):
    contracts = [
        "contracts/company",
        "contracts/paygo",
        "contracts/token",
    ]

    for contract_path in contracts:
        try:
            build_contract(contract_path)
            wasm_path = get_wasm_path(contract_path)
            if not os.path.exists(wasm_path):
                raise AssertionError(f"WASM file not found at {wasm_path}")
        except Exception as e:
            raise AssertionError(f"Error validating {contract_path}: {str(e)}")


@given('"{uploader}" upload the "{contract_name}" contract to Stellar')
def step_upload_company_contract(context, uploader, contract_name):
    """Uploader upload some contract to Stellar"""
    # Implement the upload logic here
    wasm_path = get_wasm_path(f"contracts/{contract_name}")
    wasm_hash = upload_wasm_via_cli(
        context, wasm_path, context.wallets[uploader]["keypair"]
    )
    context.contracts["wasm_hash"][contract_name] = wasm_hash


def deployer_create_the_contract_with_args(context, deployer, contract_name, *args):
    deployer_keypair = context.wallets[deployer]["keypair"]
    wasm_hash = context.contracts["wasm_hash"].get(contract_name)
    context.contracts["contract_id"][contract_name] = create_wasm_cli(
        context, wasm_hash, deployer_keypair, *args
    )


def invoke_contract_function_cli(
    context,
    contract_name: str,
    source_keypair: Keypair,
    function_name: str,
    *args: list[str],
) -> str:
    """Invoke a contract function using CLI

    Args:
        context: Behave context
        contract_name: Name of the contract
        function_name: Name of the function to call
        source_keypair: Keypair of the caller
        args: Arguments for the function call

    Returns:
        str: Result of the function call
    """
    contract_id = context.contracts["contract_id"].get(contract_name)

    command = [
        "stellar",
        "contract",
        "invoke",
        "--id",
        contract_id,
        "--source-account",
        source_keypair.secret,
        "--",
        function_name,
        *args,
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to invoke contract function: {e.stderr}")


def get_current_ledger_number(context) -> int:
    """Get the current ledger number from the Stellar network

    Args:
        context: Behave context containing server info

    Returns:
        int: Current ledger number
    """
    try:
        latest_ledger = context.soroban_server.get_latest_ledger()
        return latest_ledger.sequence
    except Exception as e:
        raise Exception(f"Failed to get current ledger number: {str(e)}")
