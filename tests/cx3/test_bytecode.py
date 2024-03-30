# SPDX-FileCopyrightText: 2024 yanchan09 <yan@omg.lol>
#
# SPDX-License-Identifier: 0BSD

from krkrz.cx3.bytecode import BytecodeInterpreter, Instruction


def test_arithmetic():
    i = BytecodeInterpreter(42)
    i.exec_one(Instruction.LOAD_INPUT, 0)
    assert i.value == 42
    i.exec_one(Instruction.ADD_ARG, 100)
    assert i.value == 142
    i.exec_one(Instruction.ADD_ONE, 0)
    assert i.value == 143
    i.exec_one(Instruction.SUBTRACT_ONE, 0)
    assert i.value == 142
    i.exec_one(Instruction.SUBTRACT_ARG, 100)
    assert i.value == 42
    i.exec_one(Instruction.BITWISE_NOT, 0)
    assert i.value == 0xFFFFFFD5
    i.exec_one(Instruction.BITWISE_XOR, 0xFFFFFFFF)
    assert i.value == 42
    i.exec_one(Instruction.NEGATE, 0)
    assert i.value == 0xFFFFFFD6  # two's complement
    i.exec_one(Instruction.SHUFFLE, 0x55555555)
    assert i.value == 0x7FFFFFAE

    i.exec_one(Instruction.LOAD_ARG, 5)
    i.exec_one(Instruction.SAVE_TO_CONTEXT, 0)
    assert i._ctx == 5

    i.exec_one(Instruction.LOAD_INPUT, 0)
    assert i.value == 42
    i.exec_one(Instruction.MULTIPLY_CONTEXT, 0)
    assert i.value == 210
    i.exec_one(Instruction.SHL_CONTEXT, 0)
    assert i.value == 6720
    i.exec_one(Instruction.SHR_CONTEXT, 0)
    assert i.value == 210
    i.exec_one(Instruction.SUBTRACT_FROM_CONTEXT, 0)
    assert i.value == 0xFFFFFF33  # -205 in two's complement
    i.exec_one(Instruction.ADD_ARG, 205)
    assert i.value == 0
    i.exec_one(Instruction.ADD_CONTEXT, 0)
    assert i.value == 5
    i.exec_one(Instruction.SUBTRACT_CONTEXT, 0)
    assert i.value == 0


def test_buffer_loads():
    buffer = [
        0x00000000,
        0x33333333,
        0x22222222,
        0x11111111,
        0x44444444,
    ]
    i = BytecodeInterpreter(0, buffer)
    i.exec_one(Instruction.LOAD_FROM_BUFFER, 3)
    assert i.value == 0x11111111
    i.exec_one(Instruction.LOAD_FROM_BUFFER_INDIRECT, 0xF)
    assert i.value == 0x33333333


def test_subroutines():
    i = BytecodeInterpreter(42)
    value = i.exec(
        [
            (Instruction.LOAD_ARG, 5),
            (Instruction.SAVE_TO_CONTEXT, 0),
            (Instruction.SUBROUTINE, 0),
            # ctx = input * 7 (294 = 42 * 7)
            (Instruction.LOAD_ARG, 7),
            (Instruction.SAVE_TO_CONTEXT, 0),
            (Instruction.LOAD_INPUT, 0),
            (Instruction.MULTIPLY_CONTEXT, 0),
            (Instruction.SAVE_TO_CONTEXT, 0),
            (Instruction.SUBROUTINE, 0),
            # value = input * 11 (462 = 42 * 7)
            (Instruction.LOAD_ARG, 11),
            (Instruction.SAVE_TO_CONTEXT, 0),
            (Instruction.LOAD_INPUT, 0),
            (Instruction.MULTIPLY_CONTEXT, 0),
            (Instruction.RETURN, 0),
            # value = ctx + value (756 = 294 + 462)
            (Instruction.ADD_CONTEXT, 0),
            (Instruction.RETURN, 0),
            # value = value * 5 (3780 = 756 * 5)
            (Instruction.MULTIPLY_CONTEXT, 0),
            (Instruction.RETURN, 0),
            # should not be executed
            (Instruction.LOAD_ARG, 0x55555555),
        ]
    )
    assert value == 3780
