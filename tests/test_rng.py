# SPDX-FileCopyrightText: 2024 yanchan09 <yan@omg.lol>
#
# SPDX-License-Identifier: 0BSD

from krkrz._rng import SplitMix64, Xoroshiro128PlusPlus, Xoroshiro128StarStar


def test_splitmix64():
    i = SplitMix64()
    assert i.next() == 0xE220A8397B1DCDAF
    assert i.next() == 0x6E789E6AA1B965F4
    assert i.next() == 0x06C45D188009454F

    i = SplitMix64(0x4242424242424242)
    assert i.next() == 0xA0E10B9A572C4B95
    assert i.next() == 0x967623BBA0906E8B
    assert i.next() == 0x098FD558C5591190


def test_xoroshiro128plusplus():
    i = Xoroshiro128PlusPlus((0x0123456789ABCDEF, 0xFEDCBA9876543210))
    assert i.next() == 0x0123456789ABCDEE
    assert i.next() == 0xA06B17E864202464
    assert i.next() == 0xCC9792EF68E54A58


def test_xoroshiro128starstar():
    i = Xoroshiro128StarStar((0x0123456789ABCDEF, 0xFEDCBA9876543210))
    assert i.next() == 0x9999999999998192
    assert i.next() == 0x99999981A9E65912
    assert i.next() == 0x8D91F41DE505EB24
