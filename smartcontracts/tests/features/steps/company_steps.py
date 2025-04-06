from behave import given, when, then
from decimal import Decimal

@given('the contracts are deployed and initialized')
def step_impl(context):
    """
    Verify that all necessary contracts are deployed and ready
    """
    required_contracts = ['company', 'token', 'paygo']
    for contract in required_contracts:
        assert contract in context.contracts['contract_id'], \
            f"{contract} contract not found in context"

@when('owner creates a company with the following details')
def step_impl(context):
    """
    Create a new company with specified details
    """
    owner_keypair = context.wallets['owner']['keypair']
    paygo_contract = context.contracts['contract_id']['paygo']
    
    company_data = {row['property']: row['value'] for row in context.table}
    
    # Create company
    context.company_id = create_company(
        context,
        owner_keypair,
        paygo_contract,
        company_data
    )

@then('the company should be created successfully')
def step_impl(context):
    """
    Verify company creation was successful
    """
    assert context.company_id is not None, "Company ID not found"
    
    # Verify company exists on network
    try:
        context.soroban_server.get_ledger_entry(context.company_id)
    except Exception as e:
        raise AssertionError(f"Company not found: {str(e)}")

@then('the company should have the following properties')
def step_impl(context):
    """
    Verify company properties match expected values
    """
    for row in context.table:
        property_name = row['property']
        expected_value = row['value']
        
        actual_value = get_company_property(
            context,
            context.company_id,
            property_name
        )
        
        assert str(actual_value) == expected_value, \
            f"Expected {property_name} to be {expected_value}, got {actual_value}"

@given('a company "{name}" exists with funded balance')
def step_impl(context, name):
    """
    Verify company exists and has sufficient funds
    """
    # Implementation details here
    pass

@when('the monthly payroll process is triggered')
def step_impl(context):
    """
    Trigger the monthly payroll process
    """
    # Implementation details here
    pass

@then('each employee should receive their allocated payment')
def step_impl(context):
    """
    Verify all employees received their payments
    """
    # Implementation details here
    pass

@then("the company's USDC reserve should be updated accordingly")
def step_impl(context):
    """
    Verify company's USDC reserve was updated correctly
    """
    # Implementation details here
    pass

def create_company(context, owner_keypair, paygo_contract, company_data):
    """Helper function to create a company"""
    # Implementation details here
    pass

def get_company_property(context, company_id, property_name):
    """Helper function to get company property"""
    # Implementation details here
    pass 