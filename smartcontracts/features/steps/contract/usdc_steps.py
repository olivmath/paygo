from behave import given, when
from features.steps.contract.utils_steps import (
    deployer_create_the_contract_with_args,
    invoke_contract_function_cli,
    get_current_ledger_number,
)


@given("admin create the token contract")
def step_impl(context):
    public_key = context.wallets["admin"]["pub"]
    deployer_create_the_contract_with_args(
        context,
        "admin",  # deployer
        "token",  # contract
        "--admin",
        public_key,
        "--decimal",
        "2",
        "--name",
        "dolar token",
        "--symbol",
        "USDC",
    )


@given("admin mint 200K USDC token to owner")
def step_impl(context):
    admin_keypair = context.wallets["admin"]["keypair"]
    owner_public_key = context.wallets["owner"]["pub"]

    # Mint 200,000 USDC (with 2 decimals, so 20000000)
    invoke_contract_function_cli(
        context,
        "token",
        admin_keypair,
        "mint",
        "--to",
        owner_public_key,
        "--amount",
        "20000000",  # 200K with 2 decimal places
    )


@when("owner approves 100K USDC to paygo")
def step_impl(context):
    owner_keypair = context.wallets["owner"]["keypair"]
    paygo_contract_id = context.contracts["contract_id"]["paygo"]
    
    # Get current ledger and add 4000 blocks
    current_ledger = get_current_ledger_number(context)
    expiration_ledger = current_ledger + 4000

    # Approve 100,000 USDC (with 2 decimals, so 10000000)
    invoke_contract_function_cli(
        context,
        "token",
        owner_keypair,
        "approve",
        "--from",
        owner_keypair.public_key,
        "--spender",
        paygo_contract_id,
        "--amount",
        "10000000",  # 100K with 2 decimal places
        "--expiration_ledger",
        str(expiration_ledger)  # Convert to string since CLI expects string arguments
    )
