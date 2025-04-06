from behave import given
from utils.contracts.compile import compile_all_smartcontracts


@given("all smart contracts are compiled successfully")
def step_verify_contracts_compiled(context):
    """
    Verify that all required smart contracts are compiled
    """

    compile_all_smartcontracts()


@given("all smart contracts are compiled successfully")
def step_impl(context):
    raise NotImplementedError(
        "STEP: Given all smart contracts are compiled successfully"
    )
