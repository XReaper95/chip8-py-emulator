import sys
from pathlib import Path

from chip8 import Chip8
from decoder import InstructionDecoder
from time import sleep


class Emulator:
    def __init__(self):
        self.chip8 = Chip8()

    def load_rom(self, game: Path):
        self.chip8.initialize()
        self.chip8.load_game(game)

    def tick(self) -> None:
        """
        Emulate one CPU cycle
        """
        try:
            while True:
                # fetch opcode
                opcode = self.chip8.fetch_opcode()
                # decode opcode
                instruction = InstructionDecoder.decode_from(opcode)

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
                        print('drawing')

                sleep(0.016)

        except KeyboardInterrupt:
            print("Game stopped")
            sys.exit(0)

    def __handle_input(self):
        """
        Handle keyboard input
        """
        pass

    def decompile(self):
        for address, opcode in self.chip8.memory_dump():
            # decode opcode
            instruction = InstructionDecoder.decode_from(opcode)
            if instruction.assembly != 'NOP':
                print(address, instruction)


if __name__ == '__main__':
    emu = Emulator()
    rom = Path('ROMs', 'PONG')
    emu.load_rom(rom)
    emu.decompile()

