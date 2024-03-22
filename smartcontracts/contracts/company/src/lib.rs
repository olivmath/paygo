#![no_std]

pub mod storage;
mod test;

use soroban_sdk::{
    contract, contractimpl, contracttype, token::TokenClient, Address, Env, String, Symbol, Vec,
};
use storage::{State, DESCRIPTION, EMPLOYEES, NAME, OWNER, STATE, USDC};

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Employee {
    name: String,
    account_id: Address,
    budger: i128,
    partial_payment: i128,
}

#[contract]
pub struct Company;

#[contractimpl]
impl Company {
    pub fn __constructor(
        e: Env,
        name: Symbol,
        description: Symbol,
        employees: Vec<Employee>,
        owner: Address,
        usdc: Address,
    ) {
        e.storage().instance().set(&DESCRIPTION, &description);
        e.storage().instance().set(&STATE, &State::default());
        e.storage().instance().set(&EMPLOYEES, &employees);
        e.storage().instance().set(&OWNER, &owner);
        e.storage().instance().set(&USDC, &usdc);
        e.storage().instance().set(&NAME, &name);
    }

    pub fn get_name(e: Env) -> Symbol {
        e.storage().instance().get(&NAME).unwrap()
    }

    pub fn get_description(e: Env) -> Symbol {
        e.storage().instance().get(&DESCRIPTION).unwrap()
    }

    pub fn get_employees(e: Env) -> Vec<Employee> {
        e.storage().instance().get(&EMPLOYEES).unwrap()
    }

    pub fn get_owner(e: Env) -> Address {
        e.storage().instance().get(&OWNER).unwrap()
    }

    pub fn get_total_cost(e: Env) -> Address {
        e.storage().instance().get(&OWNER).unwrap()
    }

    pub fn get_employee_by_account_id(e: Env, account_id: Address) -> Option<Employee> {
        let employees = Company::get_employees(e);
        employees
            .into_iter()
            .find(|emp| emp.account_id == account_id)
    }

    pub fn pay_employees(e: Env) {
        let owner = Company::get_owner(e.clone());
        owner.require_auth();

        let usdc_address = e
            .storage()
            .instance()
            .get::<Symbol, Address>(&USDC)
            .unwrap();
        let token_client = TokenClient::new(&e, &usdc_address);

        let employees = Company::get_employees(e.clone());
        for employee in employees.iter() {
            token_client.transfer(
                &e.current_contract_address(),
                &employee.account_id,
                &employee.partial_payment,
            );
        }
    }
}
