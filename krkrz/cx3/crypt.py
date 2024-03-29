# SPDX-FileCopyrightText: 2024 yanchan09 <yan@omg.lol>
#
# SPDX-License-Identifier: 0BSD

import hashlib
import struct
import argon2


def triple32(v: int) -> int:
    v ^= v >> 17
    v = (v * 0xED5AD4BB) & 0xFFFFFFFF
    v ^= v >> 11
    v = (v * 0xAC4C1B51) & 0xFFFFFFFF
    v ^= v >> 15
    v = (v * 0x31848BAB) & 0xFFFFFFFF
    v ^= v >> 14
    return v


def fnv_blake(data: bytes, fnvbase: int) -> bytes:
    fnv_value = ((0x811C9DC5 ^ fnvbase) * 0x01000193) & 0xFFFFFFFF

    hash_value = fnv_value
    out = bytearray([0] * 32)
    for i, b in enumerate(data):
        hash_value = triple32(hash_value ^ b)
        ob = (i * 4) % 32
        out[ob] ^= (hash_value) & 0xFF
        out[ob + 1] ^= (hash_value >> 8) & 0xFF
        out[ob + 2] ^= (hash_value >> 16) & 0xFF
        out[ob + 3] ^= (hash_value >> 24) & 0xFF

    h = hashlib.blake2s()
    h.update(data)
    h.update(out)
    return h.digest()


class TableKeys:
    def __init__(self, buffer):
        self.key = buffer[0:32]
        self.nonce_a = buffer[32:56]
        self.nonce_b = buffer[64:88]


class KeyDerivator:
    def __init__(self, **kwargs) -> None:
        self.bootstrap_string = kwargs["bootstrap_string"]
        self.warning_string = kwargs["warning_string"]
        self.params_blob = kwargs["params_blob"]
        self.archive_unique_key = kwargs["archive_unique_key"]
        self.upper_key_seed = kwargs["upper_key_seed"]

    def derive(self) -> TableKeys:
        bootstrap_and_warning = (self.bootstrap_string + self.warning_string).encode(
            "utf-16-le"
        )

        h = hashlib.sha3_224()
        h.update(self.params_blob)
        params_hash = h.digest()[0:16]

        lower_key = argon2.low_level.hash_secret_raw(
            bootstrap_and_warning,
            params_hash,
            parallelism=1,
            time_cost=3,
            memory_cost=8,
            hash_len=64,
            type=argon2.low_level.Type.I,
        )[0:32]
        upper_key = fnv_blake(
            self.upper_key_seed, struct.unpack("<I", self.upper_key_seed[0:4])[0]
        )

        b0 = fnv_blake(bootstrap_and_warning, 0)
        b1 = fnv_blake(self.params_blob, 1)
        b2 = fnv_blake(self.archive_unique_key.encode("utf-16-le"), 2)

        key_buffer = bytearray(b0 + b1 + b2)
        for i in range(64):
            key_buffer[i] ^= lower_key[i % 32]
        for i in range(64, 96):
            key_buffer[i] ^= upper_key[i - 64]

        return TableKeys(key_buffer)
