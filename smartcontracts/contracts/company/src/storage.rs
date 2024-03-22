use soroban_sdk::{contracttype, symbol_short, Symbol};

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq, Default)]
pub struct State {
    pub activate: bool,
}

pub const NAME: Symbol = symbol_short!("NAME");
pub const DESCRIPTION: Symbol = symbol_short!("DESC");
pub const EMPLOYEES: Symbol = symbol_short!("EMPS");
pub const OWNER: Symbol = symbol_short!("OWNER");
pub const USDC: Symbol = symbol_short!("USDC");
pub const STATE: Symbol = symbol_short!("STATE");
