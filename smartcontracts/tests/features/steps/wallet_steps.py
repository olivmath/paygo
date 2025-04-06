from behave import given
from stellar_sdk import Keypair
from .utils.wallets.fund_account import deposit_fund


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

        deposit_fund(context, keypair.public_key)
