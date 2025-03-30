from behave import given

from stellar_sdk import Keypair
import requests


@given('I create a wallet from "{private_key}" called "{wallet_name}" and funded')
def step_impl(context, private_key, wallet_name):
    """Create a wallet from a given seed and assign it a name."""
    keypair = Keypair.from_secret(private_key)

    context.wallets[wallet_name] = {
        "pub": keypair.public_key,
        "prv": keypair.secret,
        "keypair": keypair,
    }

    try:
        requests.get(f"{context.stellar_url}/friendbot?addr={keypair.public_key}")
    except Exception as e:
        raise AssertionError(f"Could not fund {wallet_name} wallet: {str(e)}")
