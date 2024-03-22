from behave import given, when, then
from stellar_sdk import Server, Keypair, Network
from typing import List, Dict
import requests
import subprocess


# Helper functions
def generate_random_account_id() -> str:
    """Generate a random Stellar account ID"""
    return Keypair.random().public_key


def create_employee_list(count: int, total_budget: float) -> List[Dict]:
    """Create a list of employees with random account IDs and distributed budget"""
    employees = []
    # Calculate base salary (equal distribution for simplicity)
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


def upload_contract(context, wasm_path: str, admin_keypair: Keypair) -> str:
    """Upload a contract using stellar-cli"""
    try:
        # Build the contract
        subprocess.run(
            ["cargo", "build", "--target", "wasm32-unknown-unknown", "--release"],
            cwd=wasm_path.split("/target/")[0],
            check=True,
        )

        # Upload using stellar-cli
        result = subprocess.run(
            [
                "stellar",
                "contract",
                "upload",
                "--wasm",
                wasm_path,
                "--source",
                admin_keypair.secret,
                "--rpc-url",
                context.stellar_url,
                "--network-passphrase",
                context.network_passphrase,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to deploy contract: {e.stderr}")


def deploy_contract(context, wasm_path: str, admin_keypair: Keypair) -> str:
    """Deploy a contract using stellar-cli"""
    try:
        # Build the contract
        subprocess.run(
            ["cargo", "build", "--target", "wasm32-unknown-unknown", "--release"],
            cwd=wasm_path.split("/target/")[0],
            check=True,
        )

        # Deploy using stellar-cli
        result = subprocess.run(
            [
                "stellar",
                "contract",
                "deploy",
                "--wasm",
                wasm_path,
                "--source",
                admin_keypair.secret,
                "--rpc-url",
                context.stellar_url,
                "--network-passphrase",
                context.network_passphrase,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to deploy contract: {e.stderr}")


@given("the Stellar network is running")
def step_check_stellar_network(context):
    """Verify Stellar network is accessible"""
    try:
        context.server = Server(context.stellar_url)
        context.network = Network.STANDALONE_NETWORK_PASSPHRASE
        # Test connection
        response = requests.get(f"{context.stellar_url}")
        assert response.status_code == 200, "stellar RPC not accessible"
    except Exception as e:
        raise AssertionError(f"Stellar network not accessible: {str(e)}")


@given("I have an admin wallet funded")
def step_setup_admin_wallet(context):
    """Setup and fund admin wallet"""
    context.admin_keypair = Keypair.random()
    # Fund the admin account using friendbot (testnet) or local network
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
    # Fund the owner account
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


@given("admin uploads the company contract to Stellar")
def step_upload_company_contract(context):
    """Upload company contract to Stellar"""
    try:
        # Deploy the contract
        wasm_path = (
            "contracts/company/target/wasm32-unknown-unknown/release/company.wasm"
        )
        context.company_contract_hash = upload_contract(
            context, wasm_path, context.admin_keypair
        )
        assert context.company_contract_hash, "Failed to upload company contract"
    except Exception as e:
        raise AssertionError(f"Failed to deploy company contract: {str(e)}")


@given("admin upload and instantiates the USDC contract")
def step_setup_usdc_contract(context):
    """Upload and instantiate USDC contract"""
    try:
        # Deploy USDC contract
        wasm_path = "contracts/usdc/target/wasm32-unknown-unknown/release/usdc.wasm"
        context.usdc_contract_id = deploy_contract(
            context, wasm_path, context.admin_keypair
        )
        assert context.usdc_contract_id, "Failed to setup USDC contract"
    except Exception as e:
        raise AssertionError(f"Failed to deploy USDC contract: {str(e)}")


@given("admin uploads and instantiates the PayGo contract")
def step_setup_paygo_contract(context):
    """Upload and instantiate PayGo contract"""
    try:
        # Deploy PayGo contract
        wasm_path = "contracts/paygo/target/wasm32-unknown-unknown/release/paygo.wasm"
        context.paygo_contract_id = deploy_contract(
            context, wasm_path, context.admin_keypair
        )
        assert context.paygo_contract_id, "Failed to setup PayGo contract"
    except Exception as e:
        raise AssertionError(f"Failed to deploy PayGo contract: {str(e)}")


@when("owner approves 100K USDC to PayGo contract")
def step_approve_usdc(context):
    """Approve USDC spending to PayGo contract"""
    try:
        # Use stellar-cli to approve USDC
        subprocess.run(
            [
                "stellar",
                "contract",
                "invoke",
                "--id",
                context.usdc_contract_id,
                "--source",
                context.owner_keypair.secret,
                "--rpc-url",
                context.stellar_url,
                "--network-passphrase",
                context.network_passphrase,
                "--",
                "approve",
                "--spender",
                context.paygo_contract_id,
                "--amount",
                str(100000 * 10**7),
            ],  # Assuming 7 decimal places
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise AssertionError(f"Failed to approve USDC: {e.stderr}")


@when("owner creates a company with the employee list")
def step_create_company(context):
    """Create company with employee list"""
    try:
        # Prepare employee data for CLI
        employees_data = []
        for emp in context.employees:
            employees_data.extend(
                [
                    "--employee-name",
                    emp["name"],
                    "--employee-account",
                    emp["account_id"],
                    "--employee-budget",
                    str(int(emp["budget"] * 10**7)),
                ]
            )

        # Use stellar-cli to create company
        result = subprocess.run(
            [
                "stellar",
                "contract",
                "invoke",
                "--id",
                context.paygo_contract_id,
                "--source",
                context.owner_keypair.secret,
                "--rpc-url",
                context.stellar_url,
                "--network-passphrase",
                context.network_passphrase,
                "--",
                "create_company",
                "--name",
                "Test Company",
                "--description",
                "Test Description",
            ]
            + employees_data,
            capture_output=True,
            text=True,
            check=True,
        )

        context.company_account_id = result.stdout.strip()
        assert context.company_account_id, "Failed to get company account ID"
    except subprocess.CalledProcessError as e:
        raise AssertionError(f"Failed to create company: {e.stderr}")


@when("owner calls pay_employees on the company contract")
def step_pay_employees(context):
    """Execute pay_employees function"""
    try:
        # Use stellar-cli to execute payment
        subprocess.run(
            [
                "stellar",
                "contract",
                "invoke",
                "--id",
                context.company_account_id,
                "--source",
                context.owner_keypair.secret,
                "--rpc-url",
                context.stellar_url,
                "--network-passphrase",
                context.network_passphrase,
                "--",
                "pay_employees",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise AssertionError(f"Failed to execute payment: {e.stderr}")


@then("all 100 employee wallets should receive their correct payment")
def step_verify_payments(context):
    """Verify all employees received correct payment"""
    for employee in context.employees:
        try:
            account = context.server.load_account(employee["account_id"])
            # Find USDC balance
            usdc_balance = 0
            for balance in account.balances:
                if (
                    balance.asset_type == "credit_alphanum4"
                    and balance.asset_code == "USDC"
                ):
                    usdc_balance = float(balance.balance)
                    break

            expected_balance = employee["budget"]
            assert (
                abs(usdc_balance - expected_balance) < 0.01
            ), f"Incorrect payment for employee {employee['name']}: expected {expected_balance}, got {usdc_balance}"
        except Exception as e:
            raise AssertionError(
                f"Failed to verify payment for {employee['name']}: {str(e)}"
            )
