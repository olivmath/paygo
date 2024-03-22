use soroban_sdk::contracterror;

#[contracterror]
#[derive(Copy, Clone, Debug, Eq, PartialEq, PartialOrd, Ord)]
#[repr(u32)]
pub enum Error {
    EmptyEmployeeList = 1,
    InvalidEmployeeAccount = 2,
    DuplicateEmployee = 3,
    InsufficientAllowance = 4,
    InvokerNotExist = 5,
}
