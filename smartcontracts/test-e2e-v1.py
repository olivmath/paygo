# 1. Create and Found Admin
# 2. Create and Found Owner

# 3. Deploy `token.wasm` with ADMIN, DECIMAL 18, NAME "dolar" SYMBOL "USDC" and save account id

# 4. Upload `company.wasm` and save wasm_hash

# 5. Deploy `paygo.wasm` with USDC <account_id> of `token.wasm` and WASM_HASH from `company.wasm` and save PAYGO account id

# 6. CREATE 100 EMPLOYEES WALLETS with NAME, ACCOUNT_ID, BUDGET with the total cost iqual 100K

# 7. Mint 100K USDC para ADMIN

# 8. Owner approve(100K USDC) to PAYGO

# 9. Owner create a company passing NAME "BANCO", DESCRIPTION "Very good", LIST_OF_EMPLOYEE <created before>

# 10. GET accountid OF new COMPANY

# 11. OWNER `CALL PAY FUNCTION` OF COMPANY CALLED `pay_employee`: 

# 12. the company are will pay the (budget / 432_000) to employee, validate it