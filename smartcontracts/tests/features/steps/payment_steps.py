from behave import when, then

@when("owner approves 100K USDC to PayGo contract")
def step_approve_usdc(context):
    """Approve USDC spending to PayGo contract using stellar_sdk"""
    # ... existing implementation ...

@when("owner creates a company with the employee list")
def step_create_company(context):
    """Create company with employee list using stellar_sdk"""
    # ... existing implementation ...

@when("owner calls pay_employees on the company contract")
def step_pay_employees(context):
    """Execute pay_employees function using stellar_sdk"""
    # ... existing implementation ...

@then("all 100 employee wallets should receive their correct payment")
def step_verify_payments(context):
    """Verificar pagamentos via Soroban RPC"""
    # ... existing implementation ... 