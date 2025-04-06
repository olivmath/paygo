from behave import given, when, then
from stellar_sdk import Keypair, Server
from decimal import Decimal


@given("the following wallets are created and funded")
def step_impl(context):
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
def step_impl(context):
    """
    Verify that all required smart contracts are compiled
    """
    # Add contract compilation verification logic here
    pass
