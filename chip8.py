from pathlib import Path

SYSTEM_MEMORY = 4096
REGISTERS_COUNT = 16
STACK_DEPTH = 16
SCREEN_HEIGHT = 64
SCREEN_WIDTH = 32
HEX_KEYPAD_SIZE = 16


class Chip8:
    def __init__(self):
        self.opcode = bytearray(2)
        self.memory = bytearray(SYSTEM_MEMORY)
        self.gp_registers = [bytes(1)] * REGISTERS_COUNT
        self.index_register = bytearray(3)
        self.pc = 0
        self.gfx = bytearray(SCREEN_HEIGHT * SCREEN_WIDTH)
        self.delay_timer = 0
        self.sound_timer = 0
        self.stack = [0] * STACK_DEPTH
        self.sp = 0
        self.key = [0] * HEX_KEYPAD_SIZE
        self.font_set = 0
        self.draw_flag: bool = False

    def initialize(self) -> None:
        """
        Initialize registers and memory
        """
        self.pc = 0x200
        self.opcode = 0
        self.index_register = 0
        self.sp = 0

    def load_game(self, game: Path) -> None:
        """
        Load a game into memory
        :param game: Game to load
        """
        with game.open(mode='rb') as game_file:
            for i, byte_ in enumerate(game_file.read(), 0):
                self.memory[i + 512] = byte_

    def tick(self) -> None:
        """
        Emulate one CPU cycle
        """
        # fetch opcode
        # decode opcode
        # execute opcode
        # update timers
        pass

    def set_keys(self) -> None:
        """
        Handles user input
        """
        pass
