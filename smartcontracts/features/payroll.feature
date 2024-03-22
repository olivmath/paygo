Feature: Stellar Payroll System
    As a company owner
    I want to process payroll through Stellar blockchain
    So that I can pay my employees automatically

    Background:
        Given the Stellar network is running
        And I have an admin wallet funded
        And I have an owner wallet funded
        And I have a list of 100 employees with total budget of 100K USDC

    Scenario: Deploy contracts and process payroll
        Given admin uploads the company contract to Stellar
        And admin upload and deploy the USDC contract
        And admin upload and deploy the PayGo contract
        When owner approves 100K USDC to PayGo contract
        And owner creates a company with the employee list
        And owner retrieves the company contract account ID
        And owner calls pay_employees on the company contract
        Then all 100 employee wallets should receive their correct payment 