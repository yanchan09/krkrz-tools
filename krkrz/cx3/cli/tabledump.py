# SPDX-FileCopyrightText: 2024 yanchan09 <yan@omg.lol>
#
# SPDX-License-Identifier: 0BSD

import argparse
from krkrz.cx3.hashdb import HashDatabase
from krkrz.cx3.table import ArchiveTable
import krkrz.xp3 as xp3
import struct
import json
from krkrz.cx3.crypt import KeyDerivator
import zlib
from Crypto.Cipher import ChaCha20_Poly1305

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="tabledump")
    parser.add_argument("filename")
    parser.add_argument("-g", "--game")
    parser.add_argument("-d", "--hashdb")
    args = parser.parse_args()

    hdb = None
    if args.hashdb:
        hdb = HashDatabase(args.hashdb)

    with open(args.filename, "rb") as f:
        if xp3.is_xp3_archive(f):
            archive = xp3.XP3Archive(f)

            table_ref_chunk = None
            for chunk_type, chunk_data in archive.index_chunks:
                if chunk_type == b"Hxv4":
                    table_ref_chunk = chunk_data
            if table_ref_chunk is None:
                raise Exception("Archive doesn't include Hxv4 index chunk")

            offset, size, flag = struct.unpack("<QIH", table_ref_chunk)
            print("Hxv4", offset, size, flag)

            f.seek(offset)
            encrypted_table = f.read(size)

            with open(args.game) as pf:
                params = json.load(pf)

            derivator = KeyDerivator(
                bootstrap_string=params["bootstrap_string"],
                warning_string=params["warning_string"],
                params_blob=bytes.fromhex(params["params_blob"]),
                archive_unique_key=params["archive_unique_key"],
                upper_key_seed=bytes.fromhex(params["upper_key_seed"]),
            )
            keys = derivator.derive()

            nonce = None
            if flag == 0:
                nonce = keys.nonce_b
            elif flag == 1:
                nonce = keys.nonce_a
            else:
                raise Exception("Invalid Hxv4 flag value")
            cipher = ChaCha20_Poly1305.new(key=keys.key, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(
                encrypted_table[16:], encrypted_table[0:16]
            )
            data = zlib.decompress(plaintext[4:])
        else:
            data = f.read()

    table = ArchiveTable(data)
    table.dump(hdb)
