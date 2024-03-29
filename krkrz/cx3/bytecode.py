# SPDX-FileCopyrightText: 2024 yanchan09 <yan@omg.lol>
#
# SPDX-License-Identifier: 0BSD

from enum import Enum, auto


class StopExecution(Exception):
    pass


class Instruction(Enum):
    ADD_ARG = auto()
    ADD_CONTEXT = auto()
    ADD_ONE = auto()
    BITWISE_NOT = auto()
    BITWISE_XOR = auto()
    LOAD_ARG = auto()
    LOAD_FROM_BUFFER = auto()
    LOAD_FROM_BUFFER_INDIRECT = auto()
    LOAD_INPUT = auto()
    MULTIPLY_CONTEXT = auto()
    NEGATE = auto()
    RETURN = auto()
    SAVE_TO_CONTEXT = auto()
    SHL_CONTEXT = auto()
    SHR_CONTEXT = auto()
    SHUFFLE = auto()
    SUB_FROM_CONTEXT = auto()
    SUBROUTINE = auto()
    SUBTRACT_ARG = auto()
    SUBTRACT_CONTEXT = auto()


class BytecodeInterpreter:
    def __init__(self, input: int, seed_block: list[int] = []) -> None:
        self.input = input
        self.value = 0
        self.stack = [0]
        self.seed_block = seed_block

    @property
    def _ctx(self) -> int:
        return self.stack[len(self.stack) - 1]

    @_ctx.setter
    def _ctx(self, v: int):
        self.stack[len(self.stack) - 1] = v

    def exec(self, instructions: list) -> int:
        for ty, arg in instructions:
            try:
                self.exec_one(ty, arg)
            except StopExecution:
                break
        return self.value

    def exec_one(self, ty: Instruction, arg: int) -> None:
        handlers = {
            Instruction.ADD_ARG: self._exec_add_arg,
            Instruction.ADD_CONTEXT: self._exec_add_context,
            Instruction.ADD_ONE: self._exec_add_one,
            Instruction.BITWISE_NOT: self._exec_bitwise_not,
            Instruction.BITWISE_XOR: self._exec_bitwise_xor,
            Instruction.LOAD_ARG: self._exec_load_arg,
            Instruction.LOAD_FROM_BUFFER: self._exec_load_from_buffer,
            Instruction.LOAD_FROM_BUFFER_INDIRECT: self._exec_load_from_buffer_indirect,
            Instruction.LOAD_INPUT: self._exec_load_input,
            Instruction.MULTIPLY_CONTEXT: self._exec_multiply_context,
            Instruction.NEGATE: self._exec_negate,
            Instruction.RETURN: self._exec_return,
            Instruction.SAVE_TO_CONTEXT: self._exec_save_to_context,
            Instruction.SHL_CONTEXT: self._exec_shl_context,
            Instruction.SHR_CONTEXT: self._exec_shr_context,
            Instruction.SHUFFLE: self._exec_shuffle,
            Instruction.SUB_FROM_CONTEXT: self._exec_sub_from_context,
            Instruction.SUBROUTINE: self._exec_subroutine,
            Instruction.SUBTRACT_ARG: self._exec_subtract_arg,
            Instruction.SUBTRACT_CONTEXT: self._exec_subtract_context,
        }
        handlers[ty](arg)

    def _exec_add_arg(self, arg: int) -> None:
        self.value = (self.value + arg) & 0xFFFFFFFF

    def _exec_add_context(self, arg: int) -> None:
        self.value = (self.value + self._ctx) & 0xFFFFFFFF

    def _exec_add_one(self, arg: int) -> None:
        self.value = (self.value + 1) & 0xFFFFFFFF

    def _exec_bitwise_not(self, arg: int) -> None:
        self.value = ~self.value & 0xFFFFFFFF

    def _exec_bitwise_xor(self, arg: int) -> None:
        self.value ^= arg

    def _exec_load_arg(self, arg: int) -> None:
        self.value = arg

    def _exec_load_from_buffer(self, arg: int) -> None:
        self.value = self.seed_block[arg]

    def _exec_load_from_buffer_indirect(self, arg: int) -> None:
        self.value = self.seed_block[self.value & arg]

    def _exec_load_input(self, arg: int) -> None:
        self.value = self.input

    def _exec_multiply_context(self, arg: int) -> None:
        self.value = (self.value * self._ctx) & 0xFFFFFFFF

    def _exec_negate(self, arg: int) -> None:
        self.value = -self.value & 0xFFFFFFFF

    def _exec_return(self, arg: int) -> None:
        self.stack.pop()
        if not self.stack:
            raise StopExecution()

    def _exec_save_to_context(self, arg: int) -> None:
        self._ctx = self.value

    def _exec_shl_context(self, arg: int) -> None:
        self.value = (self.value << (self._ctx & 0xF)) & 0xFFFFFFFF

    def _exec_shr_context(self, arg: int) -> None:
        self.value = self.value >> (self._ctx & 0xF)

    def _exec_shuffle(self, arg: int) -> None:
        self.value = ((self.value & arg) >> 1 | (self.value & ~arg) << 1) & 0xFFFFFFFF

    def _exec_sub_from_context(self, arg: int) -> None:
        self.value = (self._ctx - self.value) & 0xFFFFFFFF

    def _exec_subroutine(self, arg: int) -> None:
        self.stack.append(0)

    def _exec_subtract_arg(self, arg: int) -> None:
        self.value = (self.value - arg) & 0xFFFFFFFF

    def _exec_subtract_context(self, arg: int) -> None:
        self.value = (self.value - self._ctx) & 0xFFFFFFFF
