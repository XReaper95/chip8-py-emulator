from pathlib import Path

from chip8 import Chip8
from decoder import InstructionDecoder


class Emulator:
    def __init__(self):
        self.chip8 = Chip8()

    def load_rom(self):
        self.chip8.initialize()
        rom = Path('ROMs', 'Airplane.ch8')
        self.chip8.load_game(rom)

    def tick(self) -> None:
        """
        Emulate one CPU cycle
        """
        # fetch opcode
        if not self.chip8.pause:
            opcode = self.chip8.fetch_opcode()

            # decode opcode
            instruction = InstructionDecoder.decode_from(opcode)

            # execute opcode
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
                pass

    def handle_input(self):
        """
        Handle keyboard input
        """
        pass


if __name__ == '__main__':
    pass
