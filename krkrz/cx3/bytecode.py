# SPDX-FileCopyrightText: 2024 yanchan09 <yan@omg.lol>
#
# SPDX-License-Identifier: 0BSD

from enum import Enum, auto
from krkrz._rng import SplitMix64, Xoroshiro128PlusPlus, Xoroshiro128StarStar
from typing import Protocol


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
    SUBTRACT_FROM_CONTEXT = auto()
    SUBROUTINE = auto()
    SUBTRACT_ARG = auto()
    SUBTRACT_CONTEXT = auto()
    SUBTRACT_ONE = auto()


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
            Instruction.SUBTRACT_FROM_CONTEXT: self._exec_subtract_from_context,
            Instruction.SUBROUTINE: self._exec_subroutine,
            Instruction.SUBTRACT_ARG: self._exec_subtract_arg,
            Instruction.SUBTRACT_CONTEXT: self._exec_subtract_context,
            Instruction.SUBTRACT_ONE: self._exec_subtract_one,
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

    def _exec_subtract_from_context(self, arg: int) -> None:
        self.value = (self._ctx - self.value) & 0xFFFFFFFF

    def _exec_subroutine(self, arg: int) -> None:
        self.stack.append(0)

    def _exec_subtract_arg(self, arg: int) -> None:
        self.value = (self.value - arg) & 0xFFFFFFFF

    def _exec_subtract_context(self, arg: int) -> None:
        self.value = (self.value - self._ctx) & 0xFFFFFFFF

    def _exec_subtract_one(self, arg: int) -> None:
        self.value = (self.value - 1) & 0xFFFFFFFF


BytecodeInstruction = tuple[Instruction, int]


class BytecodeTooLargeException(Exception):
    pass


INSTRUCTION_COSTS = {
    Instruction.ADD_ARG: 1,  # +4 argument
    Instruction.ADD_CONTEXT: 2,
    Instruction.ADD_ONE: 1,
    Instruction.BITWISE_NOT: 2,
    Instruction.BITWISE_XOR: 1,  # +4 argument
    Instruction.LOAD_ARG: 1,  # +4 argument
    Instruction.LOAD_FROM_BUFFER: 7,  # +4 argument
    Instruction.LOAD_FROM_BUFFER_INDIRECT: 13,
    Instruction.LOAD_INPUT: 2,
    Instruction.MULTIPLY_CONTEXT: 3,
    Instruction.NEGATE: 2,
    Instruction.RETURN: 1,
    Instruction.SAVE_TO_CONTEXT: 2,
    Instruction.SHL_CONTEXT: 9,
    Instruction.SHR_CONTEXT: 9,
    Instruction.SHUFFLE: 21,
    Instruction.SUBTRACT_FROM_CONTEXT: 4,
    Instruction.SUBROUTINE: 1,
    Instruction.SUBTRACT_ARG: 1,  # +4 argument
    Instruction.SUBTRACT_CONTEXT: 2,
    Instruction.SUBTRACT_ONE: 1,
}


class RNGVariant(Enum):
    PLUS = auto()
    STAR = auto()


class TrackedBytecodeBuffer:
    def __init__(self, max_cost: int) -> None:
        self.max_cost = max_cost
        self.current_cost = 0
        self.buffer: list[BytecodeInstruction] = []

    def append(self, i: Instruction, arg: int = 0) -> None:
        self.add_cost(INSTRUCTION_COSTS[i])
        self.buffer.append((i, arg))

    def set_argument(self, arg: int) -> None:
        self.add_cost(4)
        inst, _ = self.buffer[len(self.buffer) - 1]
        self.buffer[len(self.buffer) - 1] = (inst, arg)

    def add_cost(self, cost: int) -> None:
        self.current_cost += cost
        if self.current_cost > self.max_cost:
            raise BytecodeTooLargeException()

    def unwrap(self) -> list[BytecodeInstruction]:
        return self.buffer


class RNGProtocol(Protocol):
    def next(self) -> int: ...


class BytecodeEmitter:
    rng: RNGProtocol

    def __init__(self, seed: int, order: list[int], rng_variant: RNGVariant) -> None:
        split_mix = SplitMix64(seed)
        xoroshiro_seed = (split_mix.next(), split_mix.next())
        if rng_variant == RNGVariant.PLUS:
            self.rng = Xoroshiro128PlusPlus(xoroshiro_seed)
        else:
            self.rng = Xoroshiro128StarStar(xoroshiro_seed)
        self.order = order  # @todo - validate order?

    def _rnd32(self) -> int:
        return self.rng.next() & 0xFFFFFFFF

    def emit(self, max_cost: int = 128) -> list[BytecodeInstruction]:
        for rounds in range(5, 0, -1):
            buffer = TrackedBytecodeBuffer(max_cost)
            try:
                buffer.add_cost(9)
                self.emit_subroutine(buffer, rounds)
                buffer.append(Instruction.RETURN)
                buffer.add_cost(5)
                return buffer.unwrap()
            except BytecodeTooLargeException:
                continue
        raise Exception("Failed to generate bytecode")

    def emit_final(self, buf: TrackedBytecodeBuffer) -> None:
        val = self._rnd32() % 3
        if val == self.order[14]:
            buf.append(Instruction.LOAD_ARG)
            buf.set_argument(self._rnd32() & 0xFFFFFFFF)
        elif val == self.order[15]:
            buf.append(Instruction.LOAD_INPUT)
        elif val == self.order[16]:
            buf.append(Instruction.LOAD_FROM_BUFFER)
            buf.set_argument(self._rnd32() & 0x3FF)
        else:
            raise Exception("emit_final failed")

    def emit_subroutine(
        self,
        buf: TrackedBytecodeBuffer,
        step: int,
    ) -> None:
        if step == 1:
            return self.emit_final(buf)

        buf.append(Instruction.SUBROUTINE)
        val = self._rnd32()
        if val % 2 == 0:
            self.emit_inner(buf, step - 1)
        else:
            self.emit_subroutine(buf, step - 1)

        buf.append(Instruction.SAVE_TO_CONTEXT)
        val = self._rnd32()
        if val % 2 == 0:
            self.emit_inner(buf, step - 1)
        else:
            self.emit_subroutine(buf, step - 1)

        val = self._rnd32() % 6
        if val == self.order[8]:
            buf.append(Instruction.ADD_CONTEXT)
        elif val == self.order[9]:
            buf.append(Instruction.SUBTRACT_CONTEXT)
        elif val == self.order[10]:
            buf.append(Instruction.SUBTRACT_FROM_CONTEXT)
        elif val == self.order[11]:
            buf.append(Instruction.MULTIPLY_CONTEXT)
        elif val == self.order[12]:
            buf.append(Instruction.SHL_CONTEXT)
        elif val == self.order[13]:
            buf.append(Instruction.SHR_CONTEXT)
        else:
            raise Exception("emit_subroutine failed")
        buf.append(Instruction.RETURN)

    def emit_inner(
        self,
        buf: TrackedBytecodeBuffer,
        step: int,
    ) -> None:
        if step == 1:
            return self.emit_final(buf)

        val = self._rnd32()
        if val % 2 == 0:
            self.emit_inner(buf, step - 1)
        else:
            self.emit_subroutine(buf, step - 1)

        val = self._rnd32() % 8
        if val == self.order[0]:
            buf.append(Instruction.BITWISE_NOT)
        elif val == self.order[1]:
            buf.append(Instruction.NEGATE)
        elif val == self.order[2]:
            buf.append(Instruction.ADD_ONE)
        elif val == self.order[3]:
            buf.append(Instruction.SUBTRACT_ONE)
        elif val == self.order[4]:
            buf.append(Instruction.SHUFFLE, 0xAAAAAAAA)
        elif val == self.order[5]:
            buf.append(Instruction.BITWISE_XOR)
            buf.set_argument(self._rnd32())
        elif val == self.order[6]:
            arg = self._rnd32()
            if arg % 2 == 0:
                buf.append(Instruction.SUBTRACT_ARG)
            else:
                buf.append(Instruction.ADD_ARG)
            buf.set_argument(self._rnd32())
        elif val == self.order[7]:
            buf.append(Instruction.LOAD_FROM_BUFFER_INDIRECT, 0x3FF)
        else:
            raise Exception("emit_inner failed")


class Blackbox:
    def __init__(self, order: list[int], rng_variant: RNGVariant) -> None:
        self.order = order
        self.rng_variant = rng_variant
        self.slots: list[None | list[BytecodeInstruction]] = [None] * 128

    def _ensure_slot(self, idx: int) -> list[BytecodeInstruction]:
        if self.slots[idx] is None:
            seed_lo = idx
            seed_hi = ~idx & 0xFFFFFFFF
            bc = BytecodeEmitter(seed_hi << 32 | seed_lo, self.order, self.rng_variant)
            self.slots[idx] = bc.emit()

        return self.slots[idx]  # type: ignore # slot is definitely assigned

    def execute(self, value: int) -> int:
        slot = self._ensure_slot(value % 128)

        bytecode_input = value >> 7

        interp_lo = BytecodeInterpreter(bytecode_input)
        result_lo = interp_lo.exec(slot)

        interp_hi = BytecodeInterpreter(~bytecode_input & 0xFFFFFFFF)
        result_hi = interp_hi.exec(slot)
        return result_hi << 32 | result_lo
