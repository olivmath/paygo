from behave import given
from utils.wallets.fund_account import deposit_fund
from utils.wallets.random import generate_random_account_id


@given("I have a list of employees with the following details")
def step_create_employee_list_with_details(context):
    """Create a list of employees with specific details from the table"""
    context.employees = []

    # Create employees from the table data
    for row in context.table:
        employee = {
            "name": row["name"],
            "account_id": generate_random_account_id(),
            "budget": int(row["budget"]),
        }
        context.employees.append(employee)
        deposit_fund(context, employee["account_id"])

    # Store total budget for later verification
    context.total_employee_budget = sum(emp["budget"] for emp in context.employees)
