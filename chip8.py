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
        self.gfx = [0] * (SCREEN_HEIGHT * SCREEN_WIDTH)
        self.delay_timer = 0
        self.sound_timer = 0
        self.stack = [0] * STACK_DEPTH
        self.sp = 0
        self.key = [0] * HEX_KEYPAD_SIZE
        self.draw_flag: bool = False

    def initialize(self) -> None:
        """
        Initialize the game system
        """
        # initialize registers and memory
        pass

    def load_game(self, game) -> None:
        """
        Load a game into memory
        :param game: Game to load
        """
        pass

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
