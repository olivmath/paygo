Feature: Stellar Payroll System
    As a company owner
    I want to process payroll through Stellar blockchain
    So that I can pay my employees automatically

    Background:
        Given the Stellar network is running
        And the following wallets are created and funded:
            | role  | secret                                                              |
            | admin | SDFHKE7ABNQKSCADYBS35SY44AVBT7DTHWFQTXUGMWBVSO5LO53R52LC |
            | owner | SAYLONVIPX22DMUBPQ3OYG4QRSZSTN7HGF4CTVGHKPKE3MO5L6K3DLIC |

    Scenario: Setup company with employees and initial funding
        Given I have a list of "10" employees with the following details:
            | name      | budget |
            | Employee1 | 10000  |
            | Employee2 | 10000  |
            | Employee3 | 10000  |
        And all smart contracts are compiled successfully
        When admin deploys the following contracts:
            | contract | initialization                    |
            | company  | -                                |
            | token    | name=USDC,symbol=USDC,decimal=7  |
            | paygo    | usdc=token,company=company       |
        And admin mints "200000" USDC tokens to owner
        And owner approves "100000" USDC to paygo contract
        Then all contracts should be deployed successfully
        And owner should have "200000" USDC balance

    Scenario: Create company and verify setup
        Given the contracts are deployed and initialized
        When owner creates a company with the following details:
            | name      | Petrobras             |
            | employees | 10                    |
            | budget    | 100000               |
        Then the company should be created successfully
        And the company should have the following properties:
            | property       | value    |
            | name          | Petrobras |
            | employee_count| 10        |
            | total_budget  | 100000    |
            | usdc_reserve  | 100000    |

    Scenario: Process monthly payroll
        Given a company "Petrobras" exists with funded balance
        When the monthly payroll process is triggered
        Then each employee should receive their allocated payment
        And the company's USDC reserve should be updated accordingly