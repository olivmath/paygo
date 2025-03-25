from behave import given, when

from features.steps.contract.utils_steps import deployer_create_the_contract_with_args, invoke_contract_function


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


@when('owner create a company called "Petrobras" in the paygo passing all 100 employee')
def step_create_company(context):
    owner_keypair = context.wallets["owner"]["keypair"]
    owner_public_key = context.wallets["owner"]["pub"]
    employees = context.employees  # Assuming employees are already created in context

    # Prepare company name and description
    company_name = "Petrobras"
    company_description = "A company for oil and gas exploration"

    # Create the company in the paygo contract
    invoke_contract_function(
        context,
        "paygo",
        owner_keypair,
        "create_company",
        "--owner",
        owner_public_key,
        "--company_name",
        company_name,
        "--company_description",
        company_description,
        "--employees",
        *[f"{emp['name']}:{emp['account_id']}:{emp['budget']}" for emp in employees],  # Format employees
    )
