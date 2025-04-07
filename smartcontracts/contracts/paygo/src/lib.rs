#![no_std]

pub mod error;
pub mod storage;
mod test;

use error::Error;
use soroban_sdk::token::Client as TokenClient;
use soroban_sdk::{contract, contractimpl, Address, BytesN, Env, IntoVal, Symbol, Val, Vec};
use storage::{Employee, COMP_WASM, USDC};

#[contract]
pub struct PayGo;

#[contractimpl]
impl PayGo {
    pub fn __constructor(
        e: Env,
        usdc: Address,
        company_wasm_hash: BytesN<32>,
    ) -> Result<(), Error> {
        e.storage().instance().set(&USDC, &usdc);
        e.storage().instance().set(&COMP_WASM, &company_wasm_hash);
        Ok(())
    }

    pub fn create_company(
        e: Env,
        owner: Address,
        company_name: Symbol,
        employees: Vec<Employee>,
    ) -> Result<bool, Error> {
        owner.require_auth();

        // validate employees
        // calc total cost
        // validate allowance
        // deploy company
        // transfer balance from owner to company contract
        // Return company id
        Ok(true)
    }
}

// ✅ CASE 1
// 1 Owner add company
// 1.1 Company must have: name, description, list of employee, account_id, owner
// 1.1.1 Employee must have: name, account_id, budget
// 1.2 Owner fund company
// 1.3 Owner call function and pay a percent of budget to all employees
