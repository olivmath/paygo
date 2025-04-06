from stellar_sdk import TransactionBuilder, xdr as stellar_xdr
from stellar_sdk.exceptions import PrepareTransactionException
from stellar_sdk.soroban_rpc import GetTransactionStatus, SendTransactionStatus

from tests.features.steps.contract.utils_steps import decode_error_xdr


def send_tx(context, sender_keypair, transaction: TransactionBuilder):
    try:
        transaction = context.soroban_server.prepare_transaction(transaction)
    except PrepareTransactionException as e:
        raise RuntimeError(
            f"Transaction preparation failed: {e.simulate_transaction_response}"
        ) from e

    transaction.sign(sender_keypair)

    try:
        send_response = context.soroban_server.send_transaction(transaction)
        if send_response.status != SendTransactionStatus.PENDING:
            raise RuntimeError(f"Transaction submission failed: {send_response.status}")
    except Exception as e:
        error_xdr = getattr(
            e, "error_result_xdr", getattr(send_response, "error_result_xdr", None)
        )
        decoded_error = decode_error_xdr(error_xdr) if error_xdr else "Unknown error"
        raise RuntimeError(f"Transaction failed: {decoded_error}") from e

    tx_hash = send_response.hash
    while True:
        tx_data = context.soroban_server.get_transaction(tx_hash)
        if tx_data.status != GetTransactionStatus.NOT_FOUND:
            break

    if tx_data.status == GetTransactionStatus.SUCCESS:
        return _extract_scval_hex(tx_data.result_meta_xdr)
    raise RuntimeError(f"Transaction execution failed: {tx_data.result_xdr}")


def _extract_scval_hex(result_meta_xdr: str) -> str:
    meta = stellar_xdr.TransactionMeta.from_xdr(result_meta_xdr)
    return meta.v3.soroban_meta.return_value.bytes.sc_bytes.hex()
