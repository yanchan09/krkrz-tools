# SPDX-FileCopyrightText: 2024 yanchan09 <yan@omg.lol>
#
# SPDX-License-Identifier: 0BSD

import struct
import io
from enum import IntFlag
import zlib
import os


class IndexFlag(IntFlag):
    COMPRESSED_ZLIB = 1
    CONTINUE = 0x80


def is_xp3_archive(file: io.BufferedIOBase) -> bool:
    magic = file.read(11)
    file.seek(-11, os.SEEK_CUR)
    return magic == b"XP3\r\n \n\x1a\x8b\x67\x01"


class XP3Archive:
    def __init__(self, file: io.BufferedIOBase) -> None:
        self.index_chunks: list[tuple[int, bytes]] = []

        magic = file.read(11)
        if magic != b"XP3\r\n \n\x1a\x8b\x67\x01":
            raise Exception("Invalid XP3 archive magic")

        index_flags = IndexFlag(0x80)
        while IndexFlag.CONTINUE in index_flags:
            (index_offset,) = struct.unpack("<q", file.read(8))
            file.seek(index_offset)

            index_flags = IndexFlag(file.read(1)[0])
            if IndexFlag.COMPRESSED_ZLIB in index_flags:
                compressed_size, real_size = struct.unpack("<qq", file.read(16))
                index_data = zlib.decompress(file.read(compressed_size))
                self._add_index_data(index_data)
            else:
                (real_size,) = struct.unpack("<q", file.read(8))
                index_data = file.read(real_size)
                self._add_index_data(index_data)

    def _add_index_data(self, data: bytes) -> None:
        offset = 0
        while offset < len(data):
            (
                ty,
                sz,
            ) = struct.unpack("<4sq", data[offset : offset + 12])
            offset += 12
            self.index_chunks.append((ty, data[offset : offset + sz]))
            offset += sz
