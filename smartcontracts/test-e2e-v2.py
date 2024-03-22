from itertools import cycle
import random
from stellar_sdk import Keypair, Network, SorobanServer, TransactionBuilder, scval, xdr, Server
from stellar_sdk.soroban_rpc import GetTransactionStatus, SendTransactionStatus
from stellar_sdk.exceptions import PrepareTransactionException, NotFoundError
import time
from requests import get, RequestException
from threading import Thread

# Configuration
ADMIN_PRIVATE_KEY = "SDLXNGAV34DZJMUO3MZMDQLUWQPFY6J3JVVG77T2G7VA3HJYETBEBVZO"
OWNER_PRIVATE_KEY = "SCI34MBIA7EIDM3VOIMNGMGWCGD7IZAJ76GHPSFBMDIXT4GIOPFGPAFL"  # Replace with actual owner private key
RPC_URL = "http://localhost:8000/soroban/rpc"
HORIZON_URL = "http://localhost:8000"

# Initialize keypairs and servers
admin_keypair = Keypair.from_secret(ADMIN_PRIVATE_KEY)
owner_keypair = Keypair.from_secret(OWNER_PRIVATE_KEY)
soroban_server = SorobanServer(server_url=RPC_URL)
horizon_server = Server(horizon_url=HORIZON_URL)

def create_account(public_key, server: Server):
    """Create a new account using Friendbot"""
    url = "http://localhost:8000/friendbot"
    params = {"addr": public_key}
    
    try:
        r = get(url, params=params, timeout=30)
        r.raise_for_status()
        print(f"✅ Account created successfully: {public_key}")
        return server.load_account(public_key)
    except RequestException as e:
        raise ValueError(f"Error getting funds from Friendbot: {str(e)}") from e

def validate_account(public_key, server: Server):
    """Check if account exists; if not, create it."""
    try:
        return server.load_account(public_key)
    except NotFoundError:
        print(f"🚫 Account {public_key} doesn't exist!")
        print("🔧 Creating account...")
        return create_account(public_key, server)

class TestE2E:
    def __init__(self):
        self.token_contract_id = None
        self.company_wasm_hash = None
        self.paygo_contract_id = None
        self.company_contract_id = None
        self.employees = []
        
        # Validate admin and owner accounts
        self.admin_account = validate_account(admin_keypair.public_key, horizon_server)
        self.owner_account = validate_account(owner_keypair.public_key, horizon_server)

    def deploy_contract(self, contract_name):
        """
        Deploy a contract and return its contract ID
        """
        print(f"📝 Uploading {contract_name} contract WASM...")
        # Load contract binary
        with open(f"target/wasm32-unknown-unknown/release/{contract_name}.wasm", "rb") as f:
            contract_bin = f.read()

        # Build transaction to upload the contract
        tx = (
            TransactionBuilder(
                source_account=self.admin_account,
                network_passphrase=Network.STANDALONE_NETWORK_PASSPHRASE,
                base_fee=100,
            )
            .set_timeout(300)
            .append_upload_contract_wasm_op(contract=contract_bin)
            .build()
        )

        # Prepare and send transaction
        try:
            tx = soroban_server.prepare_transaction(tx)
            tx.sign(admin_keypair)
            response = soroban_server.send_transaction(tx)
            
            # Wait for confirmation
            while True:
                get_transaction_data = soroban_server.get_transaction(response.hash)
                if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
                    break
                time.sleep(1)

            if get_transaction_data.status == GetTransactionStatus.SUCCESS:
                transaction_meta = xdr.TransactionMeta.from_xdr(get_transaction_data.result_meta_xdr)
                wasm_id = transaction_meta.v3.soroban_meta.return_value.bytes.sc_bytes.hex()
                print(f"✅ Contract WASM uploaded with ID: {wasm_id}")
                
                # Now create the contract instance
                print(f"📝 Creating {contract_name} contract instance...")
                tx = (
                    TransactionBuilder(
                        source_account=self.admin_account,
                        network_passphrase=Network.STANDALONE_NETWORK_PASSPHRASE,
                        base_fee=100,
                    )
                    .set_timeout(300)
                    .append_create_contract_op(
                        wasm_id=wasm_id,
                        address=admin_keypair.public_key,
                    )
                    .build()
                )
                
                tx = soroban_server.prepare_transaction(tx)
                tx.sign(admin_keypair)
                response = soroban_server.send_transaction(tx)
                
                # Wait for confirmation
                while True:
                    get_transaction_data = soroban_server.get_transaction(response.hash)
                    if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
                        break
                    time.sleep(1)

                if get_transaction_data.status == GetTransactionStatus.SUCCESS:
                    transaction_meta = xdr.TransactionMeta.from_xdr(get_transaction_data.result_meta_xdr)
                    contract_id = transaction_meta.v3.soroban_meta.return_value.address.contract_id.hex()
                    print(f"✅ Contract instance created with ID: {contract_id}")
                    return contract_id
                else:
                    raise Exception(f"Contract instance creation failed: {get_transaction_data.result_xdr}")
            else:
                raise Exception(f"WASM upload failed: {get_transaction_data.result_xdr}")

        except Exception as e:
            print(f"🚨 Error deploying contract: {e}")
            raise

    def invoke_contract_function(self, contract_id, function_name, params, signer_keypair=None):
        """
        Invoke a contract function and return the result
        """
        if signer_keypair is None:
            signer_keypair = admin_keypair

        sender_account = soroban_server.load_account(signer_keypair.public_key)

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
            tx = soroban_server.prepare_transaction(tx)
        except PrepareTransactionException as e:
            print(f"🚨 Transaction preparation error: {e.simulate_transaction_response.error}")
            return None

        tx.sign(signer_keypair)

        try:
            response = soroban_server.send_transaction(tx)
            if response.status == SendTransactionStatus.ERROR:
                print(f"🚨 Transaction send error: {response}")
                return None

            tx_hash = response.hash
            
            # Wait for transaction confirmation
            while True:
                get_transaction_data = soroban_server.get_transaction(tx_hash)
                if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
                    break
                time.sleep(1)

            if get_transaction_data.status != GetTransactionStatus.SUCCESS:
                print(f"🚨 Transaction failed: {get_transaction_data.result_xdr}")
                return None

            transaction_meta = xdr.TransactionMeta.from_xdr(get_transaction_data.result_meta_xdr)
            return scval.to_native(transaction_meta.v3.soroban_meta.return_value)

        except Exception as e:
            print(f"🚨 Error: {e}")
            return None

    def deploy_token_contract(self):
        """
        Deploy the token contract with specified parameters
        """
        print("📝 Deploying token contract...")
        wasm_id = self.deploy_contract("token")
        self.token_contract_id = wasm_id
        
        # Initialize token contract
        result = self.invoke_contract_function(
            self.token_contract_id,
            "initialize",
            [
                scval.to_address(admin_keypair.public_key),
                scval.to_uint32(18),  # decimals
                scval.to_string("dolar"),  # name
                scval.to_string("USDC"),  # symbol
            ]
        )
        print("✅ Token contract deployed and initialized")
        return result

    def upload_company_contract(self):
        """
        Upload the company contract and save its hash
        """
        print("📝 Uploading company contract...")
        wasm_id = self.deploy_contract("company")
        self.company_wasm_hash = wasm_id  # Store the WASM ID for company contract
        print("✅ Company contract uploaded")

    def deploy_paygo_contract(self):
        """
        Deploy the PayGo contract with token and company contract references
        """
        print("📝 Deploying PayGo contract...")
        wasm_id = self.deploy_contract("paygo")
        self.paygo_contract_id = wasm_id
        
        # Initialize PayGo contract with token contract address and company WASM hash
        result = self.invoke_contract_function(
            self.paygo_contract_id,
            "initialize",
            [
                scval.to_string(self.token_contract_id),  # Token contract ID as string
                scval.to_string(self.company_wasm_hash),  # Company WASM hash as string
            ]
        )
        print("✅ PayGo contract deployed and initialized")
        return result

    def create_employee_wallets(self, count=100):
        """
        Create employee wallets with budgets
        """
        print(f"👥 Creating {count} employee wallets...")
        total_budget = 100_000 * 1e18  # 100K USDC with 18 decimals
        budget_per_employee = total_budget / count

        for i in range(count):
            employee_keypair = Keypair.random()
            employee = {
                "name": f"Employee {i+1}",
                "account_id": employee_keypair.public_key,
                "budget": int(budget_per_employee),
                "private_key": employee_keypair.secret,
            }
            self.employees.append(employee)
        
        print(f"✅ Created {count} employee wallets")

    def mint_tokens(self):
        """
        Mint 100K USDC to admin
        """
        print("💰 Minting tokens to admin...")
        amount = 100_000 * 1e18  # 100K USDC with 18 decimals
        result = self.invoke_contract_function(
            self.token_contract_id,
            "mint",
            [
                scval.to_address(admin_keypair.public_key),
                scval.to_int128(amount)
            ]
        )
        print("✅ Tokens minted to admin")
        return result

    def approve_tokens(self):
        """
        Owner approves 100K USDC to PayGo contract
        """
        print("👍 Approving tokens to PayGo contract...")
        amount = 100_000 * 1e18  # 100K USDC with 18 decimals
        result = self.invoke_contract_function(
            self.token_contract_id,
            "approve",
            [
                scval.to_address(self.paygo_contract_id),
                scval.to_int128(amount)
            ],
            signer_keypair=owner_keypair
        )
        print("✅ Tokens approved to PayGo contract")
        return result

    def create_company(self):
        """
        Create a new company with employees
        """
        print("🏢 Creating company...")
        employee_data = [
            [
                scval.to_string(emp["name"]),
                scval.to_address(emp["account_id"]),
                scval.to_int128(emp["budget"])
            ]
            for emp in self.employees
        ]

        result = self.invoke_contract_function(
            self.paygo_contract_id,
            "create_company",
            [
                scval.to_string("BANCO"),
                scval.to_string("Very good"),
                scval.to_vec(employee_data)
            ],
            signer_keypair=owner_keypair
        )
        self.company_contract_id = result
        print("✅ Company created")
        return result

    def pay_employees(self):
        """
        Execute payment to employees
        """
        print("💸 Paying employees...")
        result = self.invoke_contract_function(
            self.company_contract_id,
            "pay_employee",
            [],
            signer_keypair=owner_keypair
        )
        print("✅ Employees paid")
        return result

    def validate_payments(self):
        """
        Validate employee payments
        """
        print("🔍 Validating payments...")
        for employee in self.employees:
            expected_payment = employee["budget"] / 432_000
            balance = self.invoke_contract_function(
                self.token_contract_id,
                "balance",
                [scval.to_address(employee["account_id"])]
            )
            
            if balance == expected_payment:
                print(f"✅ Employee {employee['name']} received correct payment")
            else:
                print(f"❌ Employee {employee['name']} payment mismatch. Expected: {expected_payment}, Got: {balance}")

    def run_all_tests(self):
        """
        Run all tests in sequence
        """
        try:
            print("🚀 Starting end-to-end tests...")
            
            self.deploy_token_contract()
            self.upload_company_contract()
            self.deploy_paygo_contract()
            self.create_employee_wallets()
            self.mint_tokens()
            self.approve_tokens()
            self.create_company()
            self.pay_employees()
            self.validate_payments()
            
            print("✅ All tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            raise

if __name__ == "__main__":
    test = TestE2E()
    test.run_all_tests() 