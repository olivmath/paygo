Feature: Stellar Payroll System
    As a company owner
    I want to process payroll through Stellar blockchain
    So that I can pay my employees automatically

    Background:
        Given the Stellar network is running
        And I create a wallet from "SDFHKE7ABNQKSCADYBS35SY44AVBT7DTHWFQTXUGMWBVSO5LO53R52LC" called "admin" and funded
        And I create a wallet from "SAYLONVIPX22DMUBPQ3OYG4QRSZSTN7HGF4CTVGHKPKE3MO5L6K3DLIC" called "owner" and funded
        And I have a list of "10" employees with total budget of 100K USDC
        And all contracts are successfully compiled

    Scenario: Deploy contracts and create company
        Given "admin" upload the "company" contract to Stellar
        And "admin" upload the "token" contract to Stellar
        And "admin" upload the "paygo" contract to Stellar
        And admin create the token contract
        And admin create the paygo contract
        And admin mint 200K USDC token to owner

        When owner approves 100K USDC to paygo
        And owner create a company called "Petrobras" in the paygo passing all 100 employee
        And return the contract id to owner
        
        Then the paygo must have create a company called "Petrobras"
        And with 100 employees
        And with 100K USDC of total cost
        And with 100K USDC of reserve deposited
    
    # Scenario: Pay all employees in process payroll    