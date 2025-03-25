from behave import given

from stellar_sdk import Keypair
import requests


@given('I create a wallet from "{wallet_priv}" called "{wallet_name}" and funded')
def step_impl(context, wallet_priv, wallet_name):
    """Create a wallet from a given seed and assign it a name."""
    keypair = Keypair.from_secret(wallet_priv)

    context.wallets[wallet_name] = {
        "prv": keypair.public_key,
        "pub": keypair.secret,
        "keypair": keypair,
    }

    try:
        requests.get(f"{context.stellar_url}/friendbot?addr={keypair.public_key}")
    except Exception as e:
        raise AssertionError(f"Could not fund {wallet_name} wallet: {str(e)}")
