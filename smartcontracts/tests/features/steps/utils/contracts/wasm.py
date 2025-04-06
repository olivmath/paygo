import os


def get_wasm_path(contract_path: str) -> str:
    """Get the path to the compiled WASM file"""
    contract_name = contract_path.split("/")[-1]
    workspace_root = os.path.abspath(os.path.join(contract_path, "../../"))
    wasm_path = os.path.join(
        workspace_root,
        "target/wasm32-unknown-unknown/release",
        f"{contract_name}.wasm",
    )
    return os.path.normpath(wasm_path)
