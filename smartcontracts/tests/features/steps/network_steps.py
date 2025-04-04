import requests 
from stellar_sdk import Server, Network
from behave import given


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
