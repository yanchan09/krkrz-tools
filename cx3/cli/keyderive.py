import sys
import argparse
import json
from cx3.crypt import KeyDerivator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="keyderive")
    parser.add_argument("filename")
    args = parser.parse_args()

    with open(args.filename) as f:
        params = json.load(f)

    derivator = KeyDerivator(
        bootstrap_string=params["bootstrap_string"],
        warning_string=params["warning_string"],
        params_blob=bytes.fromhex(params["params_blob"]),
        archive_unique_key=params["archive_unique_key"],
        upper_key_seed=bytes.fromhex(params["upper_key_seed"]),
    )
    keys = derivator.derive()
    print(f"Key:\t\t{keys.key.hex()}")
    print(f"Nonce A:\t{keys.nonce_a.hex()}")
    print(f"Nonce B:\t{keys.nonce_b.hex()}")
