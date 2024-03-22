use soroban_sdk::{contracttype, symbol_short, Address, Symbol};

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct EmployeeInput {
    pub name: Symbol,
    pub account_id: Address,
    pub budget: i128,
}

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Employee {
    pub name: Symbol,
    pub account_id: Address,
    pub budget: i128,
    pub partial_payment: i128,
}

pub const USDC: Symbol = symbol_short!("USDC");
pub const WASM: Symbol = symbol_short!("WASM");
pub const PAY_BLOCK: Symbol = symbol_short!("PAY_BLOCK");
