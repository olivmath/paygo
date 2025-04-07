from stellar_sdk.contract import ContractClient
from utils.contracts.types import parse_result_xdr


def invoke_fn_in_contract(context, contract_id, fn_name, invoker, *args):
    assembled = ContractClient(
        contract_id,
        context.stellar_url,
        context.network_passphrase,
    ).invoke(fn_name, args, invoker.public_key, invoker, parse_result_xdr_fn=parse_result_xdr)
    print(f"Result from simulation: {assembled.result}")
    return assembled.result
