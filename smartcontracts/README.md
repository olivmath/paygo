# Paygo

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

5. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

6. Install Python Dependencies

```bash
poetry install
```

## Documentation

### 1. Smart Contracts Overview

The project consists of three main smart contracts that work together to create a payroll system on the Stellar blockchain:

1. Token Contract (USDC)
2. PayGo Contract
3. Company Contract

### 2. Contract Details

#### Token Contract (USDC)

The token contract implements a standard Soroban token interface with the following key features:

- **Purpose**: Handles the USDC stablecoin operations for payroll payments
- **Key Functions**:
  - `mint`: Creates new tokens (admin only)
  - `approve`: Allows spending allowance for another address
  - `transfer`: Moves tokens between addresses
  - `transfer_from`: Allows approved spenders to move tokens
  - `balance`: Checks token balance
  - `allowance`: Checks spending allowance
- **Security Features**:
  - Admin authentication for minting
  - Negative amount checks
  - Expiration ledger for approvals

#### PayGo Contract

The PayGo contract serves as the main orchestrator for the payroll system:

- **Purpose**: Manages company creation and employee payroll processing
- **Key Functions**:
  - `create_company`: Creates a new company with:
    - Company name
    - List of employees and their budgets
    - Automatic calculation of payment schedules
  - **Validation Features**:
    - Prevents empty employee lists
    - Checks for duplicate employees
    - Verifies sufficient USDC allowance
- **Error Handling**:
  - `EmptyEmployeeList`
  - `InvalidEmployeeAccount`
  - `DuplicateEmployee`
  - `InsufficientAllowance`
  - `InvokerNotExist`

#### Company Contract

The Company contract manages individual company operations:

- **Purpose**: Handles company-specific operations and employee payments
- **Key Functions**:
  - `get_name`: Retrieves company name
  - `get_employees`: Lists all employees
  - `get_owner`: Returns company owner address
  - `get_total_cost`: Calculates total payroll cost
  - `pay_employees`: Processes payments to all employees
- **Data Structures**:
  - `Employee`: Stores employee information
    - Name
    - Account ID
    - Budget
    - Partial payment amount

### 3. BDD Testing

The project uses Behavior-Driven Development (BDD) testing with the following key scenarios:

#### Main Test Scenario: "Stellar Payroll System"

```gherkin
Feature: Stellar Payroll System
    As a company owner
    I want to process payroll through Stellar blockchain
    So that I can pay my employees automatically
```

#### Test Steps:

1. **Setup**:

- Initialize Stellar network
- Create admin and owner wallets
- Create test employees
- Compile all contracts

2. **Contract Deployment**:

- Upload company, token, and paygo contracts
- Initialize token contract
- Initialize paygo contract
- Mint initial USDC tokens to owner

3. **Company Creation**:

- Owner approves USDC to paygo (100K USDC)
- Create company "Petrobras" with employees
- Verify company creation

4. **Validation Checks**:

- Verify company name
- Confirm employee count
- Validate total cost
- Check USDC reserve

The testing framework uses Python with the Behave library for BDD testing, ensuring that all components work together as expected in a real-world scenario.
