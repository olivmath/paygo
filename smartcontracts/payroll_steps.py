from stellar_sdk import (
    Keypair,
    Network,
    Server,
    TransactionBuilder,
    xdr as stellar_xdr,
    SorobanServer,
)
import requests
import subprocess
import os
import base64
from stellar_sdk import Address


# Helper functions
def generate_random_account_id() -> str:
    """Generate a random Stellar account ID"""
    return Keypair.random().public_key


def create_employee_list(count: int, total_budget: float) -> list[dict]:
    """Create a list of employees with random account IDs and distributed budget"""
    employees = []
    base_salary = total_budget / count

    for i in range(count):
        employees.append(
            {
                "name": f"Employee_{i+1}",
                "account_id": generate_random_account_id(),
                "budget": base_salary,
            }
        )
    return employees


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


def upload_contract(context, wasm_path: str, admin_keypair: Keypair) -> str:
    """Upload contract WASM using Soroban"""
    soroban_server = SorobanServer(context.stellar_url)

    with open(wasm_path, "rb") as f:
        contract_code = f.read()

    # Simular transação
    tx = (
        TransactionBuilder(
            source_account=admin_keypair, network_passphrase=context.network
        )
        .append_upload_contract_wasm_op(contract_code)
        .build()
    )

    simulate_resp = soroban_server.simulate_transaction(tx)
    tx.set_footpoint(simulate_resp.footprint)
    tx.sign(admin_keypair)

    send_resp = soroban_server.send_transaction(tx)
    get_resp = soroban_server.get_transaction(send_resp.hash)

    if get_resp.status == TransactionStatus.SUCCESS:
        return get_resp.wasm_id.hex()  # ID do WASM carregado
    else:
        raise Exception(f"Falha no upload: {get_resp.result_xdr}")


def create_contract(context, wasm_id: str, admin_keypair: Keypair) -> str:
    """Criar instância do contrato usando WASM ID"""
    soroban_server = SorobanServer(context.stellar_url)

    # Simular transação
    tx = (
        TransactionBuilder(
            source_account=admin_keypair, network_passphrase=context.network
        )
        .append_create_contract_op(wasm_id=wasm_id)
        .build()
    )

    simulate_resp = soroban_server.simulate_transaction(tx)
    tx.set_footpoint(simulate_resp.footprint)
    tx.sign(admin_keypair)

    send_resp = soroban_server.send_transaction(tx)
    get_resp = soroban_server.get_transaction(send_resp.hash)

    if get_resp.status == TransactionStatus.SUCCESS:
        return get_resp.contract_id  # ID da instância do contrato
    else:
        raise Exception(f"Falha na criação: {get_resp.result_xdr}")


def deploy_contract(context, wasm_path: str, admin_keypair: Keypair) -> str:
    """Deploy a contract using stellar_sdk"""
    with open(wasm_path, "rb") as f:
        contract_code = f.read()

    soroban_server = SorobanServer(context.stellar_url)
    source_account = context.server.load_account(admin_keypair.public_key)

    transaction = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=context.network,
            base_fee=100000,
        )
        .append_deploy_contract_op(contract_code)
        .build()
    )

    transaction.sign(admin_keypair)
    response = soroban_server.send_transaction(transaction)

    get_result = soroban_server.get_transaction(response.hash)
    if get_result.status == "SUCCESS":
        return get_result.contract_id
    else:
        raise Exception(f"Failed to deploy contract: {get_result.status}")


# Given steps
@given("the Stellar network is running")
def step_check_stellar_network(context):
    """Verify Stellar network is accessible"""
    try:
        context.server = Server(context.stellar_url)
        context.network = Network.STANDALONE_NETWORK_PASSPHRASE
        response = requests.get(f"{context.stellar_url}")
        assert response.status_code == 200, "Stellar RPC not accessible"
    except Exception as e:
        raise AssertionError(f"🔴 Node Stellar are running? ERROR: {str(e)}")


@given("I have an admin wallet funded")
def step_setup_admin_wallet(context):
    """Setup and fund admin wallet"""
    context.admin_keypair = Keypair.random()
    try:
        requests.get(
            f"{context.stellar_url}/friendbot?addr={context.admin_keypair.public_key}"
        )
    except Exception as e:
        raise AssertionError(f"Could not fund admin wallet: {str(e)}")


@given("I have an owner wallet funded")
def step_setup_owner_wallet(context):
    """Setup and fund owner wallet"""
    context.owner_keypair = Keypair.random()
    try:
        requests.get(
            f"{context.stellar_url}/friendbot?addr={context.owner_keypair.public_key}"
        )
    except Exception as e:
        raise AssertionError(f"Could not fund owner wallet: {str(e)}")


@given("I have a list of 100 employees with total budget of 100K USDC")
def step_create_employee_list(context):
    """Create list of 100 employees with total budget of 100K USDC"""
    context.employees = create_employee_list(100, 100000)
    assert len(context.employees) == 100, "Failed to create 100 employees"
    total_budget = sum(emp["budget"] for emp in context.employees)
    assert abs(total_budget - 100000) < 0.01, "Total budget does not match 100K USDC"


@given("all contracts are successfully compiled")
def step_validate_contract_compilation(context):
    """Validate that all contracts are successfully compiled"""
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


@given("admin uploads the company contract to Stellar")
def step_upload_company_contract(context):
    """Upload company contract to Stellar"""
    try:
        wasm_path = get_wasm_path("contracts/company")
        context.company_contract_hash = upload_contract(
            context, wasm_path, context.admin_keypair
        )
        assert context.company_contract_hash, "Failed to upload company contract"
    except Exception as e:
        raise AssertionError(f"Failed to upload company contract: {str(e)}")


@given("admin upload and instantiates the USDC contract")
def step_setup_usdc_contract(context):
    """Upload e criação do contrato USDC"""
    try:
        # 1. Upload do WASM
        wasm_path = get_wasm_path("contracts/token")
        wasm_id = upload_contract(context, wasm_path, context.admin_keypair)

        # 2. Criar instância
        context.usdc_contract_id = create_contract(
            context, wasm_id, context.admin_keypair
        )

        assert context.usdc_contract_id, "USDC contract não criado"
    except Exception as e:
        raise AssertionError(f"Falha USDC: {str(e)}")


@given("admin uploads and instantiates the PayGo contract")
def step_setup_paygo_contract(context):
    """Upload and instantiate PayGo contract"""
    try:
        wasm_path = get_wasm_path("contracts/paygo")
        context.paygo_contract_id = deploy_contract(
            context, wasm_path, context.admin_keypair
        )
        assert context.paygo_contract_id, "Failed to setup PayGo contract"
    except Exception as e:
        raise AssertionError(f"Failed to deploy PayGo contract: {str(e)}")


# When steps
@when("owner approves 100K USDC to PayGo contract")
def step_approve_usdc(context):
    """Approve USDC spending to PayGo contract using stellar_sdk"""
    soroban_server = SorobanServer(context.stellar_url)
    source_account = context.server.load_account(context.owner_keypair.public_key)

    amount = 100000 * 10**7  # Assuming 7 decimals

    transaction = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=context.network,
            base_fee=100000,
        )
        .append_invoke_contract_function_op(
            contract_id=context.usdc_contract_id,
            function_name="approve",
            parameters=[context.paygo_contract_id, amount],
        )
        .build()
    )

    transaction.sign(context.owner_keypair)
    response = soroban_server.send_transaction(transaction)

    get_result = soroban_server.get_transaction(response.hash)
    if get_result.status != "SUCCESS":
        raise Exception(f"Failed to approve USDC: {get_result.status}")


@when("owner creates a company with the employee list")
def step_create_company(context):
    """Create company with employee list using stellar_sdk"""
    name = "Test Company"
    description = "Test Description"
    employees = []
    for emp in context.employees:
        employee = [
            {"type": "string", "value": emp["name"]},
            {"type": "address", "value": emp["account_id"]},
            {"type": "i128", "value": int(emp["budget"] * 10**7)},
        ]
        employees.append({"type": "struct", "value": employee})
    args = [
        {"type": "string", "value": name},
        {"type": "string", "value": description},
        {"type": "vec", "value": employees},
    ]
    tx = context.server.soroban().invoke_contract(
        context.owner_keypair,
        context.paygo_contract_id,
        "create_company",
        args,
    )
    tx.sign(context.owner_keypair)
    response = context.server.submit_transaction(tx)
    if response["successful"]:
        # Assumindo que create_company retorna o ID da empresa como string
        return_value = response["result"]["soroban_transaction_data"]["return_value"]
        context.company_account_id = base64.b64decode(return_value).decode("utf-8")
    else:
        raise Exception(f"Failed to create company: {response['error']}")


@when("owner calls pay_employees on the company contract")
def step_pay_employees(context):
    """Execute pay_employees function using stellar_sdk"""
    tx = context.server.soroban().invoke_contract(
        context.owner_keypair,
        context.company_account_id,
        "pay_employees",
        [],
    )
    tx.sign(context.owner_keypair)
    response = context.server.submit_transaction(tx)
    if not response["successful"]:
        raise Exception(f"Failed to pay employees: {response['error']}")


@then("all 100 employee wallets should receive their correct payment")
def step_verify_payments(context):
    """Verificar pagamentos via Soroban RPC"""
    for employee in context.employees:
        try:
            # Consultar saldo diretamente no contrato
            key = stellar_xdr.LedgerKey.contract_data(
                stellar_xdr.LedgerKeyContractData(
                    contract_id=stellar_xdr.Hash(
                        bytes.fromhex(context.usdc_contract_id)
                    ),
                    key=stellar_xdr.SCVal.scv_address(
                        Address(employee["account_id"]).to_xdr_sc_val()
                    ),
                    durability=stellar_xdr.ContractDataDurability.PERSISTENT,
                )
            )

            entry = context.soroban_server.get_ledger_entry(key)
            balance = Int128.from_xdr_sc_val(entry.xdr_data).to_int()

            expected = int(employee["budget"] * 10**7)
            assert balance == expected, f"Saldo incorreto: {balance} vs {expected}"
        except Exception as e:
            raise AssertionError(f"Verificação falhou: {str(e)}")
