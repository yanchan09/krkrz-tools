import struct


class TableParser:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.offset = 0

    def parse(self) -> list:
        values = []
        while self.offset < len(self.data):
            value = self.read_next_value()
            values.append(value)
        return values

    def read_next_value(self) -> bytes | list | int:
        kind = self.data[self.offset]
        self.offset += 1
        if kind == 0x81:  # array
            (count,) = struct.unpack(">I", self.data[self.offset : self.offset + 4])
            self.offset += 4

            values = []
            for i in range(count):
                values.append(self.read_next_value())
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


if __name__ == "__main__":
    import sys
    import pprint

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <table file>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        data = f.read()

    data = TableParser(data).parse()
    pprint.pprint(data, width=120)
