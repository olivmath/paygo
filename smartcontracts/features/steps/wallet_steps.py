from stellar_sdk import Keypair
import requests

def create_and_fund_wallet(context, wallet_name):
    """Create and fund a wallet with a given name."""
    keypair = Keypair.random()
    setattr(context, f"{wallet_name}_keypair", keypair)
    try:
        requests.get(f"{context.stellar_url}/friendbot?addr={keypair.public_key}")
    except Exception as e:
        raise AssertionError(f"Could not fund {wallet_name} wallet: {str(e)}")

@given('I have a "{wallet_name}" wallet funded')
def step_setup_wallet(context, wallet_name):
    create_and_fund_wallet(context, wallet_name)