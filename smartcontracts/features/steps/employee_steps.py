from stellar_sdk import Keypair

def generate_random_account_id() -> str:
    """Generate a random Stellar account ID"""
    return Keypair.random().public_key

def create_employee_list(count: int, total_budget: float) -> list[dict]:
    """Create a list of employees with random account IDs and distributed budget"""
    employees = []
    base_salary = total_budget / count

    for i in range(count):
        employees.append(
            {
                "name": f"Employee_{i+1}",
                "account_id": generate_random_account_id(),
                "budget": base_salary,
            }
        )
    return employees

@given("I have a list of 100 employees with total budget of 100K USDC")
def step_create_employee_list(context):
    """Create list of 100 employees with total budget of 100K USDC"""
    context.employees = create_employee_list(100, 100000)
    assert len(context.employees) == 100, "Failed to create 100 employees"
    total_budget = sum(emp["budget"] for emp in context.employees)
    assert abs(total_budget - 100000) < 0.01, "Total budget does not match 100K USDC" 