import subprocess


def compile_all_smartcontracts():
    try:
        subprocess.run(
            ["cargo", "build", "--target", "wasm32-unknown-unknown", "--release"],
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise AssertionError(f"Failed to build contract : {e.stderr}")
