import sys
import tkinter as tk
from pathlib import Path
from time import sleep

from chip8 import Chip8
from decoder import InstructionDecoder
from utils import snapshot_frame


class Emulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.chip8 = Chip8()
        self.title("Chip8 PyEmulator")
        self.resizable(False, False)
        self.screen = tk.Canvas()

    def load_rom(self, game: Path):
        self.chip8.initialize()
        self.chip8.load_game(game)

    def tick(self) -> None:
        """
        Emulate one CPU cycle
        """
        frame_count = 0

        try:
            while True:
                # fetch opcode
                opcode = self.chip8.fetch_opcode()
                # decode opcode
                instruction = InstructionDecoder.decode_from(self.chip8, opcode)

                # execute opcode
                if not self.chip8.pause:
                    instruction.run()

                    # update timers
                    if self.chip8.delay_timer > 0:
                        self.chip8.delay_timer -= 1

                    if self.chip8.sound_timer > 0:
                        self.chip8.sound_timer -= 1
                        if self.chip8.sound_timer == 1:
                            # play beep
                            print('beep')

                    # draw_screen
                    if self.chip8.draw_flag:
                        snapshot_frame(self.chip8.gfx)
                        self.chip8.draw_flag = False
                        frame_count += 1

                sleep(60 / 1000)

        except KeyboardInterrupt:
            print("Game stopped")
            sys.exit(0)

    def __handle_input(self):
        """
        Handle keyboard input
        """
        pass

    def decompile(self):
        for address, opcode in self.chip8.dump_memory():
            # decode opcode
            instruction = InstructionDecoder.decode_from(self.chip8, opcode)
            if instruction.assembly != 'NOP':
                print(address, instruction)


if __name__ == '__main__':
    emu = Emulator()
    rom = Path('ROMs', '15 Puzzle [Roger Ivie].ch8')
    emu.load_rom(rom)
    emu.tick()

