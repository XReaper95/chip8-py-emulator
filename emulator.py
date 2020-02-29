import sys
import tkinter as tk
from pathlib import Path
from time import sleep

from chip8 import Chip8
from decoder import InstructionDecoder


class Emulator:
    def __init__(self):
        super().__init__()
        self.chip8 = Chip8()
        self.screen = tk.Canvas()

    def load_rom(self, game: Path):
        self.chip8.initialize()
        self.chip8.load_game(game)

    def tick(self) -> None:
        """
        Emulate one CPU cycle
        """
        try:
            while True:
                self.chip8.emulate_cycle()

                # draw
                if self.chip8.draw_flag:
                    self.chip8.draw_flag = False

                # process input

                sleep(60 / 1000)

        except KeyboardInterrupt:
            print("Game stopped")
            sys.exit(0)

    def decompile(self):
        for address, opcode in self.chip8.dump_memory():
            # decode opcode
            instruction = InstructionDecoder.decode_from(self.chip8, opcode)
            if instruction.assembly != 'NOP':
                print(address, instruction)


if __name__ == '__main__':
    emu = Emulator()
    rom = Path('ROMs', 'BLITZ')
    emu.load_rom(rom)
    emu.tick()

