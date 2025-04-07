import requests


def deposit_fund(context, account_id):
    try:
        requests.get(f"{context.stellar_url}/friendbot?addr={account_id}")
    except Exception as e:
        raise AssertionError(f"Could not fund {account_id} wallet: {str(e)}")
