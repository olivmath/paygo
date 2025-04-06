from stellar_sdk import scval


def convert_arg(value, type_hint: str):
    """
    Convert a value to the appropriate SCVal type
    Args:
        value: The value to convert (can be str, bytes, or other types)
        type_hint: The type to convert to (e.g. "Symbol", "String", "Bytes", etc)
    """
    type_converters = {
        "Symbol": scval.to_symbol,
        "String": scval.to_string,
        "u32": lambda x: scval.to_uint32(int(x)),
        "u64": lambda x: scval.to_uint64(int(x)),
        "i32": lambda x: scval.to_int32(int(x)),
        "i64": lambda x: scval.to_int64(int(x)),
        "bool": lambda x: scval.to_bool(str(x).lower() == "true"),
        "Address": scval.to_address,
        "Bytes": scval.to_bytes,
    }

    converter = type_converters.get(type_hint)
    if not converter:
        raise ValueError(f"Unsupported type hint: {type_hint}")

    return converter(value)
