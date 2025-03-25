from behave import given

from features.steps.contract.utils_steps import deployer_create_the_contract_with_args


@given("admin create the paygo contract")
def step_impl(context):
    deployer_create_the_contract_with_args(
        context,
        "admin",  # deployer
        "paygo",  # contract
        "--usdc",
        context.contracts["contract_id"]["token"],
        "--company-wasm-hash",
        context.contracts["wasm_hash"]["company"],
    )

