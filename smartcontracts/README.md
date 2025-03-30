# Ultimate Stellar - People CRUD Contract

This project implements a CRUD (Create, Read, Update, Delete) contract for managing People records on the Stellar blockchain using Soroban smart contracts.

## Prerequisites

- Rust (latest stable version)
- Soroban CLI
- Stellar Development Environment
- Git

## Installation Requirements

1. Install Rust:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

2. Install Stellar CLI:

```bash
cargo install --locked stellar-cli --features opt
```

3. Install Wasm Target:

```bash
rustup target add wasm32-unknown-unknown
```

4. Autocompletion

```bash
source <(stellar completion --shell zsh) # bash
echo "source <(stellar completion --shell zsh)" >> ~/.zshrc # bash
```

## Configure keys and Faucet

```bash
stellar keys generate --global alice --network testnet --fund
```

## Project Structure

5. Create a People Data Base Project

```
stellar contract init --name people-db .
```

6. Your project folders structures

```bash
ultimate-stellar/
├── Cargo.toml
├── README.md
└── contracts
    └── people-db
        ├── Cargo.toml
        ├── Makefile
        └── src
            ├── lib.rs
            └── test.rs

4 directories, 6 files
```

7. Build your Smartcontracts

```bash
cargo build --target wasm32-unknown-unknown --release
```

## Testing the Project

Run the test suite:

```bash
cargo test
```

# VERSION 1 (Manual)

## Create a Company

<details>
<summary>Create a Company</summary>

```bash
participant Admin
participant Owner
participant Stellar
participant TokenContract
participant PaygoContract

Admin->>Stellar: Create & fund wallet "admin"
Admin->>Stellar: Create & fund wallet "owner"

Admin->>Stellar: Upload Company contract
Admin->>Stellar: Upload Token contract
Admin->>Stellar: Upload Paygo contract

Admin->>Stellar: Create Token contract
Stellar->TokenContract: Token Deployed!
TokenContract-->Admin: Token account-id

Admin->>Stellar: Create Paygo contract
Stellar->PaygoContract: Paygo Deployed!
PaygoContract-->Admin: Paygo account-id

Admin->>Stellar: Mint 200K USDC to Owner
Stellar->TokenContract: Mint 200K USDC to Owner
TokenContract-->>Owner: Transfer 200K USDC to Owner


Owner->>Stellar: Approve 100K USDC to Paygo
Stellar->TokenContract: Approved 100k from Owner to Paygo
TokenContract-->>PaygoContract: Allowance set (100K) from Owner

Owner->>Stellar: Create company
Stellar->PaygoContract: createCompany("Petrobras", 100 employees)
PaygoContract->CompanyContract: Company Deployed!
CompanyContract-->PaygoContract: Company account-id

PaygoContract->TokenContract: TransferFrom(from: Owner, to: Company, amount: 100k)
TokenContract-->CompanyContract: Transfer 100K USDC
PaygoContract-->>Owner: Company contract-id


Owner->>Stellar: Pay Employees
Stellar->CompanyContract: pay_employees()
CompanyContract->TokenContract: Transfer 10KUSDC to Employee-1
TokenContract-->Employee-1: transfer 10K usdc
CompanyContract->TokenContract: Transfer 10KUSDC to Employee-2
TokenContract-->Employee-2: transfer 10K usdc
CompanyContract->TokenContract: Transfer 10KUSDC to Employee-3
TokenContract-->Employee-3: transfer 10K usdc
```

</details>

![](./documentation/assets/create-company.png)



## Pay Employees
# VERSION 2 (Auto)

```bash
participant Admin
participant USDC
participant Owner
participant Paygo
participant Backend
participant Company

// UPLOAD COMPANY
Admin->Company: upload Company contract to Stellar Blockchain


// FUND COMPANY
Owner->USDC: approve(paygo, 100)

// VALIDATE
Owner->Paygo: create_company(name, description, list of employees)
Paygo->Paygo: validate company must not empty employee list
Paygo->Paygo: validate company must not not has any employee with invalid account id
Paygo->Paygo: validate company must not has duplicated employee in list
Paygo->Paygo: validate owner pay with `USDC` token
Paygo->Paygo: calculate employee total cost
Paygo->USDC: validate owner approve balance enough to cover total cost
USDC-->Paygo: owner allowance 100


// WRITE
Paygo->Company: Instantiate company with owner data
Company-->Paygo: return account id
Paygo->USDC: Transfer 100 USDC to Company
USDC-->Company: pay 100 USDC

// RETURN
Paygo-->Backend: [emit event] new company: account id


// PAYMENT
Backend->Company: call pay function
Company->Employee1: pay 1 USDC
Company->Employee2: pay 1 USDC
Company->Employee3: pay 1 USDC
Company->Employee4: pay 1 USDC
Company->Employee5: pay 1 USDC

// NEW BLOCK
Paygo-->Backend: "new block"


// PAYMENT
Backend->Company: call pay function
Company->Employee1: pay 1 USDC
Company->Employee2: pay 1 USDC
Company->Employee3: pay 1 USDC
Company->Employee4: pay 1 USDC
Company->Employee5: pay 1 USDC

// NEW BLOCK
Paygo-->Backend: "new block"


// PAYMENT
Backend->Company: call pay function
Company->Employee1: pay 1 USDC
Company->Employee2: pay 1 USDC
Company->Employee3: pay 1 USDC
Company->Employee4: pay 1 USDC
Company->Employee5: pay 1 USDC
```
