from behave import when, then
from stellar_sdk import Keypair, ContractClient, Network, scval


@when('owner create a company called "Petrobras" in the paygo passing all 100 employee')
def step_impl(context):
    # Configuração do cliente Soroban
    contract_id = context.contract_id

    # Preparar dados dos funcionários
    employees = []
    for i in range(100):
        employee = {
            "name": scval.to_string(f"employee_{i}"),
            "account_id": scval.to_address(Keypair.random().public_key),
            "budget": scval.to_int128(1000),  # 1000 USDC por funcionário
        }
        employees.append(employee)

    employees_scval = scval.to_vec([scval.to_map(employee) for employee in employees])

    # Parâmetros para criar a empresa
    parameters = [
        scval.to_address(context.owner_address),
        scval.to_string("Petrobras"),
        scval.to_string("Brazilian Oil Company"),
        employees_scval,
    ]

    # Invocar o contrato
    assembled = contract_client.invoke(
        "create_company",
        parameters,
        source=source_keypair.address(),
        signer=source_keypair,
    )

    # Submeter a transação
    response = assembled.submit()
    if response["status"] == "success":
        context.company_id = response[
            "hash"
        ]  # Guardar o ID para verificações posteriores
    else:
        raise Exception(f"Falha ao criar empresa: {response}")


@then('the paygo must have create a company called "Petrobras"')
def step_impl(context):
    # Verificar se a empresa foi criada (implementar lógica de verificação)
    assert context.company_id is not None, "Company ID não foi gerado"
    # Aqui você deve implementar a lógica para verificar se a empresa existe no contrato


@then("with 100 employees")
def step_impl(context):
    # Implementar verificação do número de funcionários
    # Você precisará fazer uma chamada ao contrato para obter os detalhes da empresa
    pass


@then("with 100K USDC of total cost")
def step_impl(context):
    # Implementar verificação do custo total
    # 100 funcionários * 1000 USDC = 100K USDC
    pass


@then("with 100K USDC of reserve deposited")
def step_impl(context):
    # Implementar verificação da reserva depositada
    pass


@then("return the contract id to owner")
def step_impl(context):
    assert context.company_id is not None, "Contract ID não foi retornado"
