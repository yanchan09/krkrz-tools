# SPDX-FileCopyrightText: 2024 yanchan09 <yan@omg.lol>
#
# SPDX-License-Identifier: 0BSD

_U64_BITS = 2**64 - 1


def _rotl64(v: int, k: int) -> int:
    return (v << k) & _U64_BITS | (v >> (64 - k))


class SplitMix64:
    def __init__(self, state: int = 0) -> None:
        self.state = state

    def next(self) -> int:
        self.state = (self.state + 0x9E3779B97F4A7C15) & _U64_BITS

        z = self.state
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9 & _U64_BITS
        z = (z ^ (z >> 27)) * 0x94D049BB133111EB & _U64_BITS
        return z ^ (z >> 31)


class Xoroshiro128PlusPlus:
    def __init__(self, state: tuple[int, int]) -> None:
        self.state = state

    def next(self) -> int:
        result = (self.state[0] + self.state[1]) & _U64_BITS
        result = _rotl64(result, 17)
        result = (result + self.state[0]) & _U64_BITS

        sx = self.state[0] ^ self.state[1]
        self.state = (
            _rotl64(self.state[0], 49) ^ sx ^ ((sx << 21) & _U64_BITS),
            _rotl64(sx, 28),
        )
        return result


class Xoroshiro128StarStar:
    def __init__(self, state: tuple[int, int]) -> None:
        self.state = state

    def next(self) -> int:
        result = _rotl64((self.state[0] * 5) & _U64_BITS, 7)
        result = (result * 9) & _U64_BITS

        sx = self.state[0] ^ self.state[1]
        self.state = (
            _rotl64(self.state[0], 24) ^ sx ^ ((sx << 16) & _U64_BITS),
            _rotl64(sx, 37),
        )
        return result
