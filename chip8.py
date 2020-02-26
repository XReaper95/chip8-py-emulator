from pathlib import Path
from random import randint

SYSTEM_MEMORY = 4096
MIN_PROGRAM_ADDR = 0x200
MIN_PROGRAM_ADDR_ETI = 0x600  # for ETI 660 computer

REGISTERS_COUNT = 16

STACK_DEPTH = 16
SCREEN_HEIGHT = 64
SCREEN_WIDTH = 32
KEYPAD_SIZE = 16


class Chip8:
    def __init__(self):
        # MEMORY
        self.memory = bytearray(SYSTEM_MEMORY)
        self.pc = 0

        # REGISTERS
        self.gp_registers = bytearray(REGISTERS_COUNT - 1)
        self.vf_register = 0
        self.index_register = 0
        self.delay_timer = 0
        self.sound_timer = 0

        # STACK
        self.stack = [0] * STACK_DEPTH

        # SCREEN
        self.gfx = [[0] * SCREEN_HEIGHT] * SCREEN_WIDTH

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
        self.memory[0: MIN_PROGRAM_ADDR - 1] = self.font_set

        with game.open(mode='rb') as game_file:
            for i, byte_ in enumerate(game_file.read(), 0):
                self.memory[MIN_PROGRAM_ADDR + i] = byte_

    def fetch_opcode(self):
        return self.memory[self.pc] << 8 | self.memory[self.pc + 1]

    # INSTRUCTIONS EXECUTION

    def clear_display_00e0(self):
        self.gfx.clear()
        self.gfx = bytearray(SCREEN_HEIGHT * SCREEN_WIDTH)
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
        sprite = self.memory[self.index_register: nibble + 1]
        x_offset = self.gp_registers[vx]
        y_offset = self.gp_registers[vy]

        for x_pos, sprite_byte in enumerate(sprite, 0):  # iterate sprite
            # wrap screen when sprite is out of bounds at x
            if x_offset + x_pos > SCREEN_HEIGHT:
                x_offset = 0

            screen_row = self.gfx[x_offset + x_pos]  # run for every row

            for y_pos in range(0, 8):  # iterate screen row 8-bits a time
                # wrap screen when sprite is out of bounds at y
                if y_offset + y_pos > SCREEN_WIDTH:
                    y_offset = 0

                # convert byte to bit tuple
                sprite_bits = tuple(int(item) for item in (format(int(sprite_byte, base=16), '08b')))
                pixel = screen_row[y_offset + y_pos]
                bit = sprite_bits[y_pos]

                if pixel == bit:
                    self.vf_register = 1

                self.gfx[x_offset + x_pos][y_offset + y_pos] = pixel ^ bit

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
        self.memory[self.index_register:] = self.gp_registers[0:vx]

    def read_regs_fx65(self, vx):
        self.gp_registers[0:vx] = self.memory[self.index_register:]
