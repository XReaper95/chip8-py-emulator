from functools import partial


class Instruction:
    def __init__(self, name, func, *args):
        self.name = name
        self._callable = partial(func, *args)

    def run(self):
        self._callable()


class InstructionDecoder:

    @staticmethod
    def decode_from(opcode):
        addr = opcode & 0x0FFF
        byte = opcode & 0x00FF
        nibble = opcode & 0x000F
        vx = opcode & 0x0F00
        vy = opcode & 0x00F0


