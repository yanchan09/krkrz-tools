# SPDX-FileCopyrightText: 2024 yanchan09 <yan@omg.lol>
#
# SPDX-License-Identifier: 0BSD

import struct
from krkrz.cx3.hashdb import HashType, HashDatabase


class MarshalReader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.offset = 0

    def read_value(self) -> bytes | list | int:
        kind = self.data[self.offset]
        self.offset += 1
        if kind == 0x81:  # array
            (count,) = struct.unpack(">I", self.data[self.offset : self.offset + 4])
            self.offset += 4

            values = []
            for _ in range(count):
                values.append(self.read_value())
            return values
        elif kind == 0x03:  # bytes
            (size,) = struct.unpack(">I", self.data[self.offset : self.offset + 4])
            self.offset += 4

            data_offset = self.offset
            self.offset += size
            return self.data[data_offset : data_offset + size]
        elif kind == 0x04:  # uint64
            (value,) = struct.unpack(">Q", self.data[self.offset : self.offset + 8])
            self.offset += 8
            return value
        else:
            raise Exception(f"Unknown value type: {kind:02x}")


class FileEntry:
    def __init__(self, value: list) -> None:
        self.hash = value[0]
        self.id = value[1][0]
        self.key = value[1][1]


def dump_hash(hash: tuple[int, bytes], hdb: HashDatabase | None) -> str:
    resolved_name = None
    if hdb:
        resolved_name = hdb.resolve_hash(hash[0], hash[1])
    if resolved_name is not None:
        return f"{resolved_name} ({hash[1].hex()})"
    else:
        return hash[1].hex()


class PathEntry:
    def __init__(self, value: list) -> None:
        [hash, children] = value
        self.hash = hash
        self.files = [
            FileEntry(children[i : i + 2]) for i in range(0, len(children), 2)
        ]

    def dump(self, hdb: HashDatabase | None) -> None:
        path_hash = dump_hash((HashType.PATH_SIPHASH_48, self.hash), hdb)
        print(f"* Path {path_hash}")
        for file in self.files:
            print(f"\t* File {file.id}")
            file_hash = dump_hash((HashType.FILE_BLAKE2S, file.hash), hdb)
            print(f"\t\t- Name hash: {file_hash}")
            print(f"\t\t- Key: {file.key:016x}")


class ArchiveTable:
    def __init__(self, data: bytes) -> None:
        parsed = MarshalReader(data).read_value()
        if not isinstance(parsed, list):
            raise Exception("Expected marshalled table type to be a list")
        self.paths = [PathEntry(parsed[i : i + 2]) for i in range(0, len(parsed), 2)]

    def dump(self, hdb: HashDatabase | None) -> None:
        for path in self.paths:
            path.dump(hdb)
