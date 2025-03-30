from behave import given

import requests
from stellar_sdk import Keypair


def generate_random_account_id() -> str:
    """Generate a random Stellar account ID"""
    return Keypair.random().public_key


def create_employee_list(context, count: int) -> list[dict]:
    """Create a list of employees with random account IDs and distributed budget"""
    employees = []
    base_salary = 2700

    for i in range(count):
        employees.append(
            {
                "name": f"Employee_{i+1}",
                "account_id": generate_random_account_id(),
                "budget": base_salary,
            }
        )

    for emp in employees:
        requests.get(
            f"{context.stellar_url}/friendbot?addr={emp['account_id']}", timeout=30
        )
    return employees


@given('I have a list of "{number}" employees with total budget of 100K USDC')
def step_create_employee_list(context, number):
    """Create list of {number} employees with total budget of 100K USDC"""
    number = int(number)

    context.employees = create_employee_list(context, number)
    assert len(context.employees) == number, f"Failed to create {number} employees"

    total_budget = sum(emp["budget"] for emp in context.employees)
    assert total_budget < 100_000, "Total budget does not match 100K USDC"
