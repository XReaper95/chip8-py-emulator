from pathlib import Path
from random import randint
from typing import (
    List,
    Dict,
    Text,
    NoReturn
)

from decoder import InstructionDecoder

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
        self.memory: List[int] = [0] * SYSTEM_MEMORY
        self.pc: int = 0
        self.gp_registers: List[int] = [0] * REGISTERS_COUNT
        self.index_register: int = 0
        self.delay_timer: int = 0
        self.sound_timer: int = 0
        self.stack: List[int] = [0] * STACK_DEPTH
        self.gfx: List[List[int]] = [[0 for _ in range(SCREEN_WIDTH)] for _ in range(SCREEN_HEIGHT)]
        self.keypad: Dict[Text, int] = {}
        self.key_pressed: Text = ''
        self.font_set: List[int] = [0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
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
        self.inc_pc: bool = True
        self.halt_execution: bool = False

    def initialize(self) -> NoReturn:
        """
        Initialize registers and memory
        """
        self.pc = MIN_PROGRAM_ADDR

        for i, font_byte in enumerate(self.font_set, 0):
            self.memory[i] = font_byte

        self.keypad = {
            "1": 0x1, "2": 0x2, "3": 0x3, "4": 0xC,
            "q": 0x4, "w": 0x5, "e": 0x6, "r": 0xD,
            "a": 0x7, "s": 0x8, "d": 0x9, "f": 0xE,
            "z": 0xA, "x": 0x0, "c": 0xB, "v": 0xF
        }

    def load_game(self, game_path: Path) -> NoReturn:
        """
        Load a game into memory
        :param game_path: Game to load
        """
        game_size = 0
        with game_path.open(mode='rb') as game_file:
            for i, byte in enumerate(game_file.read(), 0):
                self.memory[MIN_PROGRAM_ADDR + i] = byte
                game_size += 1

        print(f"Game size is {game_size} bytes")

    def emulate_cycle(self) -> NoReturn:
        # fetch
        opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
        # decode
        instruction = InstructionDecoder.decode_from(self, opcode)
        # execute
        print(hex(opcode), instruction.assembly)
        instruction.run()
        # update timers and pc
        if not self.halt_execution and self.pc + 2 < SYSTEM_MEMORY:
            if self.inc_pc:
                self.pc += 2
            else:
                self.inc_pc = True

            if self.delay_timer > 0:
                self.delay_timer -= 1

            if self.sound_timer > 0:
                self.sound_timer -= 1
                if self.sound_timer == 1:
                    # play beep
                    print('beep')

    def key_press(self, key: Text) -> NoReturn:
        self.key_pressed = key

    def dump_memory(self) -> NoReturn:
        memory_pointer = MIN_PROGRAM_ADDR

        while memory_pointer < SYSTEM_MEMORY - 1:
            opcode = self.memory[memory_pointer] << 8 | self.memory[memory_pointer + 1]
            instruction = InstructionDecoder.decode_from(self, opcode)
            if instruction.assembly != 'NOP':
                print(hex(memory_pointer), instruction)
            memory_pointer += 2

    # INSTRUCTIONS EXECUTION

    def do_nothing(self) -> NoReturn:
        pass

    def clear_display_00e0(self) -> NoReturn:
        for row in range(len(self.gfx)):
            for pixel in range(len(self.gfx[0])):
                self.gfx[row][pixel] = 0
        self.draw_flag = True

    def return_subroutine_00ee(self) -> NoReturn:
        self.pc = self.stack.pop()

    def jump_to_1nnn(self, addr):
        self.pc = addr
        self.inc_pc = False

    def call_subroutine_2nnn(self, addr) -> NoReturn:
        self.stack.append(self.pc)
        self.pc = addr
        self.inc_pc = False

    def skip_if_equal_value_3xkk(self, vx, byte) -> NoReturn:
        if self.gp_registers[vx] == byte:
            self.pc += 2

    def skip_if_not_equal_value_4xkk(self, vx, byte) -> NoReturn:
        if self.gp_registers[vx] != byte:
            self.pc += 2

    def skip_if_equal_reg_5xy0(self, vx, vy) -> NoReturn:
        if self.gp_registers[vx] == self.gp_registers[vy]:
            self.pc += 2

    def set_reg_value_6xkk(self, vx, byte) -> NoReturn:
        self.gp_registers[vx] = byte

    def add_value_7xkk(self, vx, byte):
        result = self.gp_registers[vx] + byte
        if result > 0xFF:
            self.gp_registers[0xF] = 0x01
        else:
            self.gp_registers[0xF] = 0x00

        self.gp_registers[vx] = result & 0xFF

    def set_reg_reg_8xy0(self, vx, vy) -> NoReturn:
        self.gp_registers[vx] = self.gp_registers[vy]

    def or_reg_reg_8xy1(self, vx, vy) -> NoReturn:
        self.gp_registers[vx] |= self.gp_registers[vy]

    def and_reg_reg_8xy2(self, vx, vy) -> NoReturn:
        self.gp_registers[vx] &= self.gp_registers[vy]

    def xor_reg_reg_8xy3(self, vx, vy) -> NoReturn:
        self.gp_registers[vx] ^= self.gp_registers[vy]

    def add_reg_carry_8xy4(self, vx, vy) -> NoReturn:
        result = self.gp_registers[vx] + self.gp_registers[vy]
        if result > 0xFF:
            self.gp_registers[0xF] = 0x01
        else:
            self.gp_registers[0xF] = 0x00

        self.gp_registers[vx] = result & 0xFF

    def sub_reg_reg_8xy5(self, vx, vy) -> NoReturn:
        if self.gp_registers[vy] > self.gp_registers[vx]:
            self.gp_registers[0xF] = 0x00
        else:
            self.gp_registers[0xF] = 0x01

        self.gp_registers[vx] -= self.gp_registers[vy]

    def shr_reg_8xy6(self, vx) -> NoReturn:
        self.gp_registers[0xF] = self.gp_registers[vx] & 0x1
        self.gp_registers[vx] >>= 1

    def subn_reg_reg_8xy7(self, vx, vy) -> NoReturn:
        self.sub_reg_reg_8xy5(vy, vx)

    def shl_reg_8xye(self, vx) -> NoReturn:
        self.gp_registers[0xF] = self.gp_registers[vx] >> 7
        self.gp_registers[vx] <<= 1

    def skip_if_not_equal_reg_9xy0(self, vx, vy) -> NoReturn:
        if self.gp_registers[vx] != self.gp_registers[vy]:
            self.pc += 2

    def set_index_value_annn(self, addr) -> NoReturn:
        self.index_register = addr

    def jump_value_offset_bnnn(self, addr) -> NoReturn:
        self.pc = self.gp_registers[0] + addr
        self.inc_pc = False

    def set_random_and_value_cxkk(self, vx, byte) -> NoReturn:
        rnd = randint(0, 255)
        self.gp_registers[vx] = rnd & byte

    def display_sprite_dxyn(self, vx, vy, nibble) -> NoReturn:
        sprite = self.memory[self.index_register: self.index_register + nibble]  # array of bytes
        screen_x = self.gp_registers[vx]
        screen_y = self.gp_registers[vy]

        # convert sprite to plain bitmap (tuple of tuples)
        sprite_bitmap = tuple(tuple(int(bit) for bit in format(byte, '08b')) for byte in sprite)
        sprite_h = len(sprite)

        # iterate the sprite overlapping region with the screen (8X{sprite length in bytes})
        for row in range(sprite_h):
            if screen_y + row < SCREEN_HEIGHT:
                for pixel_pos, pixel in enumerate(sprite_bitmap[row], 0):
                    if screen_x + pixel_pos < SCREEN_WIDTH:
                        screen_pixel = self.gfx[screen_y + row][screen_x + pixel_pos]
                        # collision detection
                        if screen_pixel == pixel:
                            self.gp_registers[0xF] = 1
                        # XOR pixels
                        self.gfx[screen_y + row][screen_x + pixel_pos] = screen_pixel ^ pixel

        self.draw_flag = True

    def skip_if_pressed_ex9e(self, vx) -> NoReturn:
        if self.key_pressed:
            key = self.keypad[self.key_pressed]
            if self.gp_registers[vx] == key:
                self.pc += 2
            self.key_pressed = ''

    def skip_if_not_pressed_exa1(self, vx) -> NoReturn:
        if self.key_pressed:
            key = self.keypad[self.key_pressed]
            if self.gp_registers[vx] != key:
                self.pc += 2
            self.key_pressed = ''
        else:
            self.pc += 2

    def save_delay_fx07(self, vx) -> NoReturn:
        self.gp_registers[vx] = self.delay_timer

    def wait_for_keypress_fx0a(self, vx) -> NoReturn:
        self.halt_execution = True
        if self.key_pressed:
            self.halt_execution = False
            self.gp_registers[vx] = self.keypad[self.key_pressed]
            self.key_pressed = ''

    def set_delay_fx15(self, vx) -> NoReturn:
        self.delay_timer = self.gp_registers[vx]

    def set_sound_fx18(self, vx) -> NoReturn:
        self.sound_timer = self.gp_registers[vx]

    def add_index_fx1e(self, vx) -> NoReturn:
        result = self.index_register + self.gp_registers[vx]
        if result > 0xFF:
            self.gp_registers[0xF] = 0x01
        else:
            self.gp_registers[0xF] = 0x00
        self.index_register = result

    def set_sprite_loc_fx29(self, vx) -> NoReturn:
        self.index_register = self.gp_registers[vx] * 5

    def bcd_repr_fx33(self, vx) -> NoReturn:
        hundreds = self.gp_registers[vx] // 100
        tens = (self.gp_registers[vx] // 10) % 10
        units = self.gp_registers[vx] % 10

        self.memory[self.index_register] = hundreds
        self.memory[self.index_register + 1] = tens
        self.memory[self.index_register + 2] = units

    def store_regs_fx55(self, vx) -> NoReturn:
        for reg in range(vx + 1):
            self.memory[self.index_register + reg] = self.gp_registers[reg]

    def read_regs_fx65(self, vx) -> NoReturn:
        for reg in range(vx + 1):
            self.gp_registers[reg] = self.memory[self.index_register + reg]
