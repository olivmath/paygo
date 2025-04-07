from stellar_sdk import Keypair


def generate_random_account_id() -> str:
    """Generate a random Stellar account ID"""
    return Keypair.random().public_key
