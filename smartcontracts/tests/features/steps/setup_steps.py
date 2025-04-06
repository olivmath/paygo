import subprocess
from behave import given, when, then
from stellar_sdk import Keypair, Server
from decimal import Decimal
import requests


@given("the following wallets are created and funded")
def step_create_and_fund_wallets(context):
    """
    Create and fund wallets based on the data table
    """
    for row in context.table:
        secret = row["secret"]
        role = row["role"]
        keypair = Keypair.from_secret(secret)

        context.wallets[role] = {"keypair": keypair, "pub": keypair.public_key}

        # Fund the account if needed
        server = Server(context.stellar_url)
        try:
            server.load_account(keypair.public_key)
        except:
            context.execute_steps(
                f"""
                Given the account "{keypair.public_key}" is funded
            """
            )


@given("all smart contracts are compiled successfully")
def step_verify_contracts_compiled(context):
    """
    Verify that all required smart contracts are compiled
    """
    try:
        subprocess.run(
            ["cargo", "build", "--target", "wasm32-unknown-unknown", "--release"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        raise AssertionError(f"Failed to build contract : {e.stderr}")


@given('the account "{account_id}" is funded')
def step_fund_account(context, account_id):
    """
    Fund a Stellar account using the friendbot service
    """
    response = requests.get(f"{context.stellar_url}/friendbot?addr={account_id}")
    assert response.status_code == 200, f"Failed to fund account {account_id}"

    # Verify account exists and is funded
    server = Server(context.stellar_url)
    account = server.load_account(account_id)
    assert account is not None, f"Account {account_id} was not created"
