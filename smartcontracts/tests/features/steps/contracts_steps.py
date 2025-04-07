from behave import given, when
from stellar_sdk import scval
from utils.contracts.invoke import invoke_fn_in_contract
from utils.contracts.types import convert_arg
from utils.contracts.deploy import deploy_wasm, deploy_wasm_via_cli
from utils.contracts.wasm import get_wasm_path
from utils.contracts.upload import upload_wasm
from utils.contracts.compile import compile_all_smartcontracts
import os


@given("all smart contracts are compiled successfully")
def step_verify_contracts_compiled(context):
    """
    Verify that all required smart contracts are compiled
    """
    compile_all_smartcontracts()


def get_wasm_path(contract_name: str) -> str:
    """Get the path to the compiled WASM file for a contract"""
    target_dir = "target/wasm32-unknown-unknown/release"
    wasm_file = f"{contract_name}.wasm"
    wasm_path = os.path.join(target_dir, wasm_file)
    if not os.path.exists(wasm_path):
        raise AssertionError(
            f"Contract WASM not found: {wasm_path}. Did you compile the contracts?"
        )
    return wasm_path


@when("admin upload the following contracts")
def step_upload_contracts(context):
    """Upload the specified smart contracts to the Stellar network"""
    # Get admin keypair
    admin_keypair = context.wallets["admin"]["keypair"]

    # Collect all contract paths
    contracts = []
    for row in context.table:
        contract_name = row["contract"]
        wasm_path = get_wasm_path(contract_name)
        with open(wasm_path, "rb") as wasm_file:
            wasm_bin = wasm_file.read()
            contracts.append((contract_name, wasm_bin))

    for name, wasm_bin in contracts:
        wasm_hash_id = upload_wasm(context, wasm_bin, admin_keypair)
        context.contracts["wasm_hash_id"][name] = wasm_hash_id


@when("admin deploys the following contracts")
def step_deploy_contracts(context):
    """Deploy contracts with initialization arguments"""
    admin_keypair = context.wallets["admin"]["keypair"]

    for row in context.table:
        contract_name = row["contract"]
        init_args_str = row["initialization"].split(",")

        # Convert string arguments to SCVal
        init_args = []
        for arg in init_args_str:
            value, type_hint = arg.split(":")
            init_args.append(convert_arg(value, type_hint))

        print(f"\n📦 Deploying {contract_name} contract")
        print(f"Initialization arguments: {init_args_str}")

        wasm_hash_id = context.contracts["wasm_hash_id"][contract_name]
        contract_id = deploy_wasm(context, wasm_hash_id, admin_keypair, init_args)

        context.contracts["contract_id"][contract_name] = contract_id


@when("admin deploys paygo contracts with token address and company wasm_id")
def step_impl(context):
    from stellar_sdk import scval

    admin_keypair = context.wallets["admin"]["keypair"]

    usdc_token_address = context.contracts["contract_id"]["token"]
    company_wasm_hash_id = context.contracts["wasm_hash_id"]["company"]
    paygo_wasm_hash_id = context.contracts["wasm_hash_id"]["paygo"]

    contract_id = deploy_wasm_via_cli(
        paygo_wasm_hash_id,
        admin_keypair,
        ["--usdc", usdc_token_address, "--company_wasm_hash", company_wasm_hash_id],
    )

    context.contracts["contract_id"]["paygo"] = contract_id
    return

    # I don't understand, but when I try to deploy via SDK it gives me the following error:

    # Event log (newest first):
    # 0: [Diagnostic Event] topics:[error, Error(Context, InvalidAction)], data:["constructor invocation has failed with error", Error(WasmVm, InvalidAction)]
    # 1: [Failed Diagnostic Event (not emitted)] contract:CDK3X7X3LHQLB5XH4VZPF6QYL6UP3PWUL6IITGGUPQTNMXEQWPLZUU5M, topics:[error, Error(WasmVm, InvalidAction)], data:["VM call trapped: UnreachableCodeReached", __constructor]
    # 2: [Diagnostic Event] topics:[fn_call, CDK3X7X3LHQLB5XH4VZPF6QYL6UP3PWUL6IITGGUPQTNMXEQWPLZUU5M, __constructor], data:[CCXG4HQSJHVQV6SYIQ7CGJ4F7TISVDUEWMLYPNAKTPP73KK3Q2XHOTUH, Bytes(34393938663666333834656364383732616365326465616433656331346138303062623835623031343639636238393734643036343161656137663264333364)]

    # init_args = [
    #     scval.to_address(usdc_token_address),
    #     scval.to_bytes(company_wasm_hash_id.encode()),
    # ]

    # print("\n📦 Deploying PayGo contract")
    # print(f"Initialization arguments: {init_args}")

    # contract_id = deploy_wasm(context, paygo_wasm_hash_id, admin_keypair, init_args)

    # context.contracts["contract_id"]["paygo"] = contract_id


@when('admin mints "200000" USDC tokens to owner')
def step_impl(context):
    admin_keypair = context.wallets["admin"]["keypair"]
    token_contract_id = context.contracts["contract_id"]["token"]
    args = [scval.to_address(admin_keypair.public_key), scval.to_uint128(200000)]

    invoke_fn_in_contract(context, token_contract_id, "mint", admin_keypair, args)


@when('owner approves "100000" USDC to paygo contract')
def step_impl(context):
    raise NotImplementedError(
        'STEP: When owner approves "100000" USDC to paygo contract'
    )


@then("all contracts should be deployed successfully")
def step_impl(context):
    raise NotImplementedError(
        "STEP: Then all contracts should be deployed successfully"
    )


@then('owner should have "200000" USDC balance')
def step_impl(context):
    raise NotImplementedError('STEP: Then owner should have "200000" USDC balance')
