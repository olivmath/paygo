from itertools import cycle
from stellar_sdk import Network, StrKey, TransactionBuilder, scval, xdr, Address
from stellar_sdk.soroban_rpc import GetTransactionStatus, SendTransactionStatus
from stellar_sdk.exceptions import PrepareTransactionException
from behave import given, when, then
from features.steps.contract.utils_steps import deployer_create_the_contract_with_args


@given("admin create the paygo contract")
def step_impl(context):
    deployer_create_the_contract_with_args(
        context,
        "admin",
        "paygo",
        "--usdc",
        context.contracts["contract_id"]["token"],
        "--company-wasm-hash",
        context.contracts["wasm_hash"]["company"],
    )


@when(
    'owner create a company called "{company_name}" in the paygo passing all employees'
)
def step_create_company(context, company_name):
    owner_keypair = context.wallets["owner"]["keypair"]
    owner_public_key = context.wallets["owner"]["pub"]
    employees = context.employees

    company_description = "OilGasExplorationa"

    print("\nCreating company with the following details:")
    print(f"Company name: {company_name}")
    print(f"Company description: {company_description}")
    print(f"Number of employees: {len(employees)}")
    print(f"Total budget: {sum(float(emp['budget']) for emp in employees)} USDC")
    print("\nEmployee details:")
    for emp in employees:
        print(f"- {emp['name']}: {emp['budget']} USDC")

    # Convert parameters to SCVal format
    owner_scval = scval.to_address(owner_public_key)
    company_name_scval = scval.to_symbol(company_name)
    company_description_scval = scval.to_symbol(company_description)

    # Convert employees to SCVal format
    employee_scvals = [employee_to_scval(emp) for emp in employees]
    employees_scval = scval.to_vec(employee_scvals)

    # Prepare parameters in the correct order
    params = [
        owner_scval,
        company_name_scval,
        company_description_scval,
        employees_scval,
    ]

    try:
        result = invoke_contract_function_sdk(
            context,
            contract_name="paygo",
            source_keypair=owner_keypair,
            function_name="create_company",
            params=params,
        )

        if result is None:
            raise ValueError("Company creation failed - no contract ID returned")

        print(f"\nCompany creation result: {result}")
        context.company_contract_id = result
        validate_contract_id(context, result)
    except Exception as e:
        print(f"\nFailed to create company: {e}")
        raise


def is_valid_contract_id_format(contract_id_str):
    try:
        # Try to decode the contract ID from its string representation
        StrKey.decode_contract(contract_id_str)
        return True
    except Exception:
        return False


def validate_contract_id(
    context,
    contract_id,
):
    # check the format
    StrKey.decode_contract(contract_id)

    # check existence
    ledger_key = xdr.LedgerKey(
        type=xdr.LedgerEntryType.CONTRACT_DATA,
        contract_data=xdr.LedgerKeyContractData(
            contract=Address(contract_id).to_xdr_sc_address(),
            key=xdr.SCVal(xdr.SCValType.SCV_LEDGER_KEY_CONTRACT_INSTANCE),
            durability=xdr.ContractDataDurability.PERSISTENT,
        ),
    )
    context.soroban_server.get_ledger_entries([ledger_key.to_xdr()])


def employee_to_scval(employee_dict: dict):
    from stellar_sdk import StrKey

    name_key = scval.to_symbol("name")
    account_id_key = scval.to_symbol("account_id")
    budget_key = scval.to_symbol("budget")

    name_val = scval.to_symbol(employee_dict["name"])
    print(
        f"Is valid address: {StrKey.is_valid_ed25519_public_key(employee_dict["account_id"])}"
    )
    account_id_val = scval.to_address(employee_dict["account_id"])

    # Convert budget to int with 7 decimal places (Stellar standard)
    budget = employee_dict["budget"]
    # The budget is in USDC, so we need to convert it to stroops (1 USDC = 10000000 stroops)
    budget_stroops = int(budget * 10000000)
    # Convert to i128 for the contract
    budget_val = scval.to_uint64(budget_stroops)

    print(f"Converting budget: {budget} USDC -> {budget_stroops} stroops")

    # Create the map with the employee data
    employee_map = {
        name_key: name_val,
        account_id_key: account_id_val,
        budget_key: budget_val,
    }

    # Convert the map to SCVal
    return scval.to_map(employee_map)


def invoke_contract_function_sdk(
    context, contract_name, source_keypair, function_name, params
):
    sender_account = context.soroban_server.load_account(source_keypair.public_key)
    contract_id = context.contracts["contract_id"].get(contract_name)

    if not contract_id:
        raise ValueError(f"Contract ID not found for {contract_name}")

    print(f"\nInvoking {function_name} on contract {contract_name}")
    print(f"Contract ID: {contract_id}")
    print(f"Source account: {source_keypair.public_key}")
    print("\nParameters:")
    for i, param in enumerate(params):
        print(f"Param {i}: {param}")

    tx = (
        TransactionBuilder(sender_account, Network.STANDALONE_NETWORK_PASSPHRASE, 100)
        .set_timeout(300)
        .append_invoke_contract_function_op(
            contract_id=contract_id,
            function_name=function_name,
            parameters=params,
        )
        .build()
    )

    try:
        print("\nPreparing transaction...")
        tx = context.soroban_server.prepare_transaction(tx)
        print("Transaction prepared successfully")
    except PrepareTransactionException as e:
        print(
            "\n🚨 Error preparing transaction",
            "👇" * 30,
            e.simulate_transaction_response.error,
            sep="\n",
        )
        raise

    tx.sign(source_keypair)

    try:
        print("\nSending transaction...")
        response = context.soroban_server.send_transaction(tx)
        print(f"Transaction sent with hash: {response.hash}")
    except Exception as e:
        print("\n🚨 Error sending transaction:", e)
        raise

    if response.status == SendTransactionStatus.ERROR:
        print("\n🚨 Transaction failed:", response)
        raise Exception(f"Transaction failed: {response}")

    tx_hash = response.hash
    clocks = cycle(["|", "/", "-", "\\"])
    while True:
        print(f"\r⏰ Waiting for transaction confirmation {next(clocks)}", end="")
        get_transaction_data = context.soroban_server.get_transaction(tx_hash)
        if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
            break

    print("\r" + " " * 50, end="\r")

    if get_transaction_data.status != GetTransactionStatus.SUCCESS:
        print(f"\n🚨 Transaction failed: {get_transaction_data.result_xdr}")
        raise Exception(f"Transaction failed: {get_transaction_data.result_xdr}")

    transaction_meta = xdr.TransactionMeta.from_xdr(
        get_transaction_data.result_meta_xdr
    )
    result = scval.to_native(transaction_meta.v3.soroban_meta.return_value)
    print(f"\nTransaction result: {result}")
    return result


@when("return the contract id to owner")
def step_impl(context):
    print(context.company_contract_id)
    assert context.company_contract_id == ""


@then('the paygo must have create a company called "Petrobras"')
def step_impl(context):
    raise NotImplementedError(
        'STEP: Then the paygo must have create a company called "Petrobras"'
    )


@then("with {number} employees")
def step_impl(context, number):
    raise NotImplementedError(f"STEP: Then with {number} employees")


@then("with 100K USDC of total cost")
def step_impl(context):
    raise NotImplementedError("STEP: Then with 100K USDC of total cost")


@then("with 100K USDC of reserve deposited")
def step_impl(context):
    raise NotImplementedError("STEP: Then with 100K USDC of reserve deposited")
