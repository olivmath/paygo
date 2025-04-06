from stellar_sdk import TransactionBuilder, xdr as stellar_xdr
from stellar_sdk.exceptions import PrepareTransactionException
from stellar_sdk.soroban_rpc import GetTransactionStatus, SendTransactionStatus


def decode_error_xdr(error_xdr: str) -> str:
    """
    Decode a Stellar error XDR string into a human readable message
    """
    try:
        # Decode the base64 XDR
        decoded = stellar_xdr.TransactionResult.from_xdr(error_xdr)

        # Get the result code
        result_code = decoded.result.code

        if result_code == stellar_xdr.TransactionResultCode.txFAILED:
            # Get the operations results
            ops_results = decoded.result.results

            # Get the first failed operation result
            for op_result in ops_results:
                if op_result.tr.code != stellar_xdr.OperationResultCode.opINNER:
                    return f"Transaction failed: {op_result.tr.code.name}"

                # Get the inner result code
                inner_code = op_result.tr.inner_result().code
                return f"Operation failed: {inner_code.name}"

        return f"Transaction failed: {result_code.name}"

    except Exception as e:
        return f"Failed to decode error XDR: {str(e)}"


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
        transaction_meta = stellar_xdr.TransactionMeta.from_xdr(tx_data.result_meta_xdr)
        return transaction_meta.v3.soroban_meta.return_value
    raise RuntimeError(f"Transaction execution failed: {tx_data.result_xdr}")
