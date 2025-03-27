import logging
from itertools import cycle
from stellar_sdk import Network, TransactionBuilder, scval, xdr
from stellar_sdk.soroban_rpc import GetTransactionStatus, SendTransactionStatus
from stellar_sdk.exceptions import PrepareTransactionException
from behave import given, when
from features.steps.contract.utils_steps import deployer_create_the_contract_with_args

def employee_to_scval(employee_dict):
    name_key = scval.to_symbol("name")
    account_id_key = scval.to_symbol("account_id")
    budget_key = scval.to_symbol("budget")
    
    name_val = scval.to_symbol(employee_dict["name"])
    account_id_val = scval.to_address(employee_dict["account_id"])
    budget_val = scval.to_int128(int(float(employee_dict["budget"]) * 10000000))
    
    return scval.to_map({
        name_key: name_val,
        account_id_key: account_id_val,
        budget_key: budget_val,
    })

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

@when('owner create a company called "Petrobras" in the paygo passing all 100 employee')
def step_create_company(context):
    owner_keypair = context.wallets["owner"]["keypair"]
    owner_public_key = context.wallets["owner"]["pub"]
    employees = context.employees

    company_name = "Petrobras"
    company_description = "A oil and gas exploration SA"

    owner_scval = scval.to_address(owner_public_key)
    company_name_scval = scval.to_symbol(company_name)
    company_description_scval = scval.to_symbol(company_description)

    employee_scvals = [employee_to_scval(emp) for emp in employees]
    employees_scval = scval.to_vec(employee_scvals)

    params = [owner_scval, company_name_scval, company_description_scval, employees_scval]

    result = invoke_contract_function_sdk(
        context,
        contract_name="paygo",
        source_keypair=owner_keypair,
        function_name="create_company",
        params=params,
    )
    context.company_account_id = result  # Salva o resultado para steps futuros, se necessário

def invoke_contract_function_sdk(context, contract_name, source_keypair, function_name, params):
    sender_account = context.soroban_server.load_account(source_keypair.public_key)
    contract_id = context.contracts["contract_id"].get(contract_name)

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
        tx = context.soroban_server.prepare_transaction(tx)
    except PrepareTransactionException as e:
        print("🚨 Erro antes de enviar a transação", "👇" * 30, e.simulate_transaction_response.error, sep="\n")
        return None

    tx.sign(source_keypair)

    try:
        response = context.soroban_server.send_transaction(tx)
    except Exception as e:
        print("🚨 Erro ao enviar a transação:", e)
        return None

    if response.status == SendTransactionStatus.ERROR:
        print("🚨 Erro ao enviar a transação:", response)
        return None

    tx_hash = response.hash
    clocks = cycle(["|", "/", "-", "\\"])
    while True:
        print(f"\r⏰ Esperando transação confirmar {next(clocks)}", end="")
        get_transaction_data = context.soroban_server.get_transaction(tx_hash)
        if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
            break

    print("\r" + " " * 50, end="\r")

    if get_transaction_data.status != GetTransactionStatus.SUCCESS:
        print(f"🚨 Transação falhou: {get_transaction_data.result_xdr}")
        return None

    transaction_meta = xdr.TransactionMeta.from_xdr(get_transaction_data.result_meta_xdr)
    result = scval.to_native(transaction_meta.v3.soroban_meta.return_value)
    return result