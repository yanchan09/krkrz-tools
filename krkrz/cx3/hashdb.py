# SPDX-FileCopyrightText: 2024 yanchan09 <yan@omg.lol>
#
# SPDX-License-Identifier: 0BSD

import sqlite3


class HashType:
    PATH_SIPHASH_48 = 1
    FILE_BLAKE2S = 2


class HashDatabase:
    def __init__(self, path: str) -> None:
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

        self.cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS known_hashes (type, hash, key, value, extra, UNIQUE(type, hash));
            """
        )

    def resolve_hash(self, kind: int, hash: bytes) -> None | str:
        self.cursor.execute(
            "SELECT value FROM known_hashes WHERE type = ? AND hash = ?", (kind, hash)
        )
        maybe_result = self.cursor.fetchone()
        if maybe_result is None:
            return None
        elif maybe_result[0] is None:
            return ""
        else:
            return maybe_result[0].decode("utf-16-le", "replace")
