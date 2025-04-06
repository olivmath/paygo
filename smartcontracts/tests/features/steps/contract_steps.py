from behave import given, when, then


@when("admin deploys the following contracts")
def step_impl(context):
    """
    Deploy contracts based on the data table
    """
    admin_keypair = context.wallets["admin"]["keypair"]

    for row in context.table:
        contract_name = row["contract"]
        initialization = row["initialization"]

        # Deploy contract
        contract_id = deploy_contract(
            context,
            admin_keypair,
            contract_name,
            parse_initialization_params(initialization),
        )

        # Store contract ID
        context.contracts["contract_id"][contract_name] = contract_id


@when('admin mints "{amount}" USDC tokens to owner')
def step_impl(context, amount):
    """
    Mint USDC tokens to owner's account
    """
    admin_keypair = context.wallets["admin"]["keypair"]
    owner_public = context.wallets["owner"]["pub"]
    token_id = context.contracts["contract_id"]["token"]

    mint_tokens(context, admin_keypair, token_id, owner_public, int(amount))


@when('owner approves "{amount}" USDC to paygo contract')
def step_impl(context, amount):
    """
    Approve USDC spending for paygo contract
    """
    owner_keypair = context.wallets["owner"]["keypair"]
    paygo_contract = context.contracts["contract_id"]["paygo"]
    token_id = context.contracts["contract_id"]["token"]

    approve_tokens(context, owner_keypair, token_id, paygo_contract, int(amount))


@then("all contracts should be deployed successfully")
def step_impl(context):
    """
    Verify all contracts are deployed and accessible
    """
    for contract_name in ["company", "token", "paygo"]:
        contract_id = context.contracts["contract_id"].get(contract_name)
        assert contract_id is not None, f"{contract_name} contract not deployed"

        # Verify contract exists on network
        try:
            context.soroban_server.get_ledger_entry(contract_id)
        except Exception as e:
            raise AssertionError(f"Contract {contract_name} not found: {str(e)}")


@then('owner should have "{amount}" USDC balance')
def step_impl(context, amount):
    """
    Verify owner's USDC balance
    """
    owner_public = context.wallets["owner"]["pub"]
    token_id = context.contracts["contract_id"]["token"]

    balance = get_token_balance(context, token_id, owner_public)
    assert balance == int(amount), f"Expected balance {amount}, got {balance}"


def deploy_contract(context, admin_keypair, contract_name, init_params):
    """Helper function to deploy a contract"""
    # Implementation details here
    pass


def parse_initialization_params(init_string):
    """Helper function to parse initialization parameters"""
    if init_string == "-":
        return {}

    params = {}
    for param in init_string.split(","):
        key, value = param.split("=")
        params[key.strip()] = value.strip()
    return params


def mint_tokens(context, admin_keypair, token_id, to_address, amount):
    """Helper function to mint tokens"""
    # Implementation details here
    pass


def approve_tokens(context, owner_keypair, token_id, spender, amount):
    """Helper function to approve token spending"""
    # Implementation details here
    pass


def get_token_balance(context, token_id, account):
    """Helper function to get token balance"""
    # Implementation details here
    pass
