use soroban_sdk::{contracttype, symbol_short, Address, String, Symbol};

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq, Default)]
pub struct State {
    pub activate: bool,
}

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Employee {
    name: String,
    account_id: Address,
    budger: i128,
    partial_payment: i128,
}

pub const NAME: Symbol = symbol_short!("NAME");
pub const EMPLOYEES: Symbol = symbol_short!("EMPS");
pub const OWNER: Symbol = symbol_short!("OWNER");
pub const USDC: Symbol = symbol_short!("USDC");
pub const STATE: Symbol = symbol_short!("STATE");
