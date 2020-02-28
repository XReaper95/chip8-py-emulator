from pathlib import Path
from random import randint

SYSTEM_MEMORY = 4096
MIN_PROGRAM_ADDR = 0x200
MIN_PROGRAM_ADDR_ETI = 0x600  # for ETI 660 computer

REGISTERS_COUNT = 16

STACK_DEPTH = 16
SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32
KEYPAD_SIZE = 16


class Chip8:
    def __init__(self):
        # MEMORY
        self.memory = [0] * SYSTEM_MEMORY
        self.pc = 0

        # REGISTERS
        self.gp_registers = [0] * (REGISTERS_COUNT - 1)
        self.vf_register = 0
        self.index_register = 0
        self.delay_timer = 0
        self.sound_timer = 0

        # STACK
        self.stack = [0] * STACK_DEPTH

        # SCREEN
        self.gfx = [[0] * SCREEN_WIDTH] * SCREEN_HEIGHT

        # KEYPAD
        self.keypad = {
            "1": 0x1, "2": 0x2, "3": 0x3, "4": 0xC,
            "q": 0x4, "w": 0x5, "e": 0x6, "r": 0xD,
            "a": 0x7, "s": 0x8, "d": 0x9, "f": 0xE,
            "z": 0xA, "x": 0x0, "c": 0xB, "v": 0xF
        }

        self.key_pressed = None

        # MISC
        self.font_set = [0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
                         0x20, 0x60, 0x20, 0x20, 0x70,  # 1
                         0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
                         0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
                         0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
                         0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
                         0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
                         0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
                         0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
                         0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
                         0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
                         0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
                         0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
                         0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
                         0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
                         0xF0, 0x80, 0xF0, 0x80, 0x80]  # F

        self.draw_flag: bool = False
        self.pause = False

    def initialize(self) -> None:
        """
        Initialize registers and memory
        """
        self.pc = MIN_PROGRAM_ADDR
        self.index_register = 0

    def load_game(self, game: Path) -> None:
        """
        Load a game into memory, also load fonts
        :param game: Game to load
        """
        for i, font_byte in enumerate(self.font_set, 0):
            self.memory[i] = font_byte

        game_size = 0
        with game.open(mode='rb') as game_file:
            for i, byte in enumerate(game_file.read(), 0):
                self.memory[MIN_PROGRAM_ADDR + i] = byte
                game_size += 1

        print(f"Game size is {game_size} bytes")

    def fetch_opcode(self):
        opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
        self.pc += 2
        return opcode

    def dump_memory(self):
        memory_pointer = MIN_PROGRAM_ADDR

        while memory_pointer < SYSTEM_MEMORY - 1:
            yield hex(memory_pointer), self.memory[memory_pointer] << 8 | self.memory[memory_pointer + 1]
            memory_pointer += 2

    # INSTRUCTIONS EXECUTION

    def do_nothing(self):
        pass

    def clear_display_00e0(self):
        self.gfx = [[0] * SCREEN_WIDTH] * SCREEN_HEIGHT
        self.draw_flag = True

    def return_subroutine_00ee(self):
        self.pc = self.stack.pop()

    def jump_to_1nnn(self, addr):
        self.pc = addr

    def call_subroutine_2nnn(self, addr):
        self.stack.append(self.pc)
        self.pc = addr

    def skip_if_equal_value_3xkk(self, vx, byte):
        if self.gp_registers[vx] == byte:
            self.pc += 2

    def skip_if_not_equal_value_4xkk(self, vx, byte):
        if self.gp_registers[vx] != byte:
            self.pc += 2

    def skip_if_equal_reg_5xy0(self, vx, vy):
        if self.gp_registers[vx] == self.gp_registers[vy]:
            self.pc += 2

    def set_reg_value_6xkk(self, vx, byte):
        self.gp_registers[vx] = byte

    def add_value_7xkk(self, vx, byte):
        self.gp_registers[vx] += byte

    def set_reg_reg_8xy0(self, vx, vy):
        self.gp_registers[vx] = self.gp_registers[vy]

    def or_reg_reg_8xy1(self, vx, vy):
        self.gp_registers[vx] |= self.gp_registers[vy]

    def and_reg_reg_8xy2(self, vx, vy):
        self.gp_registers[vx] &= self.gp_registers[vy]

    def xor_reg_reg_8xy3(self, vx, vy):
        self.gp_registers[vx] ^= self.gp_registers[vy]

    def add_reg_carry_8xy4(self, vx, vy):
        result = self.gp_registers[vx] + self.gp_registers[vy]
        if result > 0xFF:
            self.vf_register = 0x01
        else:
            self.vf_register = 0x00

        self.gp_registers[vx] = result & 0xFF

    def sub_reg_reg_8xy5(self, vx, vy):
        if self.gp_registers[vx] > self.gp_registers[vy]:
            self.vf_register = 0x01
        else:
            self.vf_register = 0x00

        self.gp_registers[vx] = self.gp_registers[vx] - self.gp_registers[vy]

    def shr_reg_8xy6(self, vx):
        self.vf_register = self.gp_registers[vx] & 0x01
        self.gp_registers[vx] >>= 2

    def subn_reg_reg_8xy7(self, vx, vy):
        self.sub_reg_reg_8xy5(vy, vx)

    def shl_reg_8xye(self, vx):
        self.vf_register = self.gp_registers[vx] & 0x01
        self.gp_registers[vx] <<= 2

    def skip_if_not_equal_reg_9xy0(self, vx, vy):
        if self.gp_registers[vx] != self.gp_registers[vy]:
            self.pc += 2

    def set_index_value_annn(self, addr):
        self.index_register = addr

    def jump_value_offset_bnnn(self, addr):
        self.pc = self.gp_registers[0] + addr

    def set_random_and_value_cxkk(self, vx, byte):
        rnd = randint(0, 255)
        self.gp_registers[vx] = rnd & byte

    def display_sprite_dxyn(self, vx, vy, nibble):
        sprite = self.memory[self.index_register: self.index_register + nibble]  # array of bytes
        start_column = self.gp_registers[vx]
        start_row = self.gp_registers[vy]

        # convert sprite to plain bitmap (tuple of tuples)
        sprite_bitmap = tuple(tuple(int(bit) for bit in format(byte, '08b')) for byte in sprite)

        # iterate the sprite overlapping region with the screen (8X{sprite length in bytes})
        for column in range(8):
            # wrap screen when sprite is out of bounds at x
            if start_column + column > SCREEN_WIDTH:
                start_column = 0

            for row in range(len(sprite)):
                # wrap screen when pixel is out of bounds at y
                if start_row + row > SCREEN_HEIGHT:
                    start_row = 0

                # compare screen pixel with sprite pixel
                screen_pixel = self.gfx[start_row + row][start_column + column]
                sprite_pixel = sprite_bitmap[row][column]

                # collision detection
                if screen_pixel == sprite_pixel:
                    self.vf_register = 1

                # XOR pixels
                self.gfx[start_row + row][start_column + column] = screen_pixel ^ sprite_pixel

        self.draw_flag = True

    def skip_if_pressed_ex9e(self, vx):
        if self.key_pressed:
            key = self.keypad[self.key_pressed]
            if self.gp_registers[vx] == key:
                self.pc += 2

    def skip_if_not_pressed_exa1(self, vx):
        if self.key_pressed:
            key = self.keypad[self.key_pressed]
            if self.gp_registers[vx] != key:
                self.pc += 2
        else:
            self.pc += 2

    def save_delay_fx07(self, vx):
        self.gp_registers[vx] = self.delay_timer

    def wait_for_keypress_fx0a(self, vx):
        self.pause = True
        if self.key_pressed:
            self.pause = False
            self.gp_registers[vx] = self.keypad[self.key_pressed]

    def set_delay_fx15(self, vx):
        self.delay_timer = self.gp_registers[vx]

    def set_sound_fx18(self, vx):
        self.sound_timer = self.gp_registers[vx]

    def add_index_fx1e(self, vx):
        self.index_register += self.gp_registers[vx]

    def set_sprite_loc_fx29(self, vx):
        self.index_register = self.gp_registers[vx] * 5

    def bcd_repr_fx33(self, vx):
        reg_value = self.gp_registers[vx]
        hundreds = reg_value // 100
        reg_value *= 100

        tens = reg_value // 10
        reg_value *= 10

        units = reg_value

        self.memory[self.index_register] = hundreds
        self.memory[self.index_register + 1] = tens
        self.memory[self.index_register + 2] = units

    def store_regs_fx55(self, vx):
        for reg in range(vx):
            self.memory[self.index_register + reg] = self.gp_registers[reg]

    def read_regs_fx65(self, vx):
        for reg in range(vx):
            self.gp_registers[reg] = self.memory[self.index_register + reg]
