#![no_std]

pub mod error;
pub mod storage;
mod test;

use error::Error;
use soroban_sdk::token::Client as TokenClient;
use soroban_sdk::{contract, contractimpl, Address, BytesN, Env, IntoVal, Symbol, Val, Vec};
use storage::{Employee, EmployeeInput, PAY_BLOCK, USDC, WASM};

#[contract]
pub struct PayGo;

#[contractimpl]
impl PayGo {
    pub fn __constructor(e: Env, usdc: Address, wasm_hash: BytesN<32>) -> Result<(), Error> {
        e.storage().instance().set(&USDC, &usdc);
        e.storage().instance().set(&WASM, &wasm_hash);
        e.storage().instance().set(&PAY_BLOCK, &432_000);
        Ok(())
    }

    pub fn create_company(
        e: Env,
        owner: Address,
        company_name: Symbol,
        company_description: Symbol,
        employees: Vec<EmployeeInput>,
    ) -> Result<Address, Error> {
        owner.require_auth();

        if employees.is_empty() {
            return Err(Error::EmptyEmployeeList);
        }

        for employee in employees.iter() {
            if employees.contains(&employee) {
                return Err(Error::DuplicateEmployee);
            }
        }

        let total_cost: i128 = employees.iter().map(|emp| emp.budget).sum();
        let pay_by_block = e
            .storage()
            .instance()
            .get::<Symbol, i128>(&PAY_BLOCK)
            .unwrap();

        let mut company_employees = Vec::new(&e);
        for emp in employees.iter() {
            company_employees.push_back(Employee {
                name: emp.name.clone(),
                account_id: emp.account_id.clone(),
                budget: emp.budget,
                partial_payment: emp.budget / pay_by_block,
            });
        }

        let token = &e
            .storage()
            .instance()
            .get::<Symbol, Address>(&USDC)
            .unwrap();

        let token_client = TokenClient::new(&e, token);

        if token_client.allowance(&owner, &e.current_contract_address()) < total_cost {
            return Err(Error::InsufficientAllowance);
        }

        // get wasm hash
        let wasm_hash = e
            .storage()
            .instance()
            .get::<Symbol, BytesN<32>>(&WASM)
            .unwrap();

        // mount company with data
        let constructor_args: Vec<Val> = (
            company_name,
            company_description,
            company_employees,
            &owner,
            token,
        )
            .into_val(&e);
        let salt = BytesN::from_array(&e, &[0; 32]);

        // instantiate company in blockchain
        let deployed_address = &e
            .deployer()
            .with_address(e.current_contract_address(), salt)
            .deploy_v2(wasm_hash, constructor_args);

        // transfer balance from owner to company contract
        token_client.transfer_from(
            &e.current_contract_address(),
            &owner,
            deployed_address,
            &total_cost,
        );

        // # Return company id
        Ok(deployed_address.clone())
    }
}

// ✅ CASE 1
// 1 Owner add company
// 1.1 Company must have: name, description, list of employee, account_id, owner
// 1.1.1 Employee must have: name, account_id, budget
// 1.2 Owner fund company
// 1.3 Owner call function and pay a percent of budget to all employees

// CASE 2
// 2. Owner remove company
// 2.1 Send back money to of balance to owner
// 2.2 company deleted

// CASE 3
// 3. Owner edit company
// 3.1 Owner add/edit/remove employee on some company
// 3.2 Company recalcule total cost
// 3.3 Owner call function and pay a percent of budget to all employees
