from chip8 import Chip8

from functools import partial


class Instruction:
    def __init__(self, assembly, func, *args):
        self.assembly = assembly
        if args:
            self._callable = partial(func, *args)
        else:
            self._callable = func

    def __str__(self):
        return self.assembly

    def run(self) -> None:
        self._callable()


class InstructionDecoder:

    @staticmethod
    def decode_from(opcode) -> Instruction:
        nnn = opcode & 0x0FFF  # addr
        kk = opcode & 0x00FF  # byte
        n = opcode & 0x000F  # nibble
        x = (opcode & 0x0F00) >> 8  # register x
        y = (opcode & 0x00F0) >> 4  # register y

        # NOP
        if opcode == 0x0000:
            return Instruction('NOP', Chip8.do_nothing)

        # SINGLE CASES
        opcode_single = opcode & 0xF000
        single_opcodes = {
            0x1000: Instruction(f'JP {hex(nnn)}', Chip8.jump_to_1nnn, nnn),
            0x2000: Instruction(f'CALL {hex(nnn)}', Chip8.call_subroutine_2nnn, nnn),
            0x3000: Instruction(f'SE V{x}, {hex(kk)}', Chip8.skip_if_equal_value_3xkk, x, kk),
            0x4000: Instruction(f'SNE V{x}, {hex(kk)}', Chip8.skip_if_not_equal_value_4xkk, x, kk),
            0x5000: Instruction(f'SE V{x}, V{y}', Chip8.skip_if_equal_reg_5xy0, x, y),
            0x6000: Instruction(f'LD V{x}, {hex(kk)}', Chip8.set_reg_value_6xkk, x, kk),
            0x7000: Instruction(f'ADD V{x}, {hex(kk)} ', Chip8.add_value_7xkk, x, kk),
            0x9000: Instruction(f'SNE V{x}, V{y}', Chip8.skip_if_not_equal_reg_9xy0, x, y),
            0xA000: Instruction(f'LD I, {hex(nnn)}', Chip8.set_index_value_annn, nnn),
            0xB000: Instruction(f'JP V0, {hex(nnn)}', Chip8.jump_value_offset_bnnn, nnn),
            0xC000: Instruction(f'RND V{x}, {hex(kk)}', Chip8.set_random_and_value_cxkk, x, kk),
            0xD000: Instruction(f'DRW V{x}, V{y}, {hex(n)}', Chip8.display_sprite_dxyn, x, y, n),
        }
        if opcode_single in single_opcodes:
            return single_opcodes[opcode_single]

        # 0 CASES
        opcode_0 = opcode & 0xFFFF
        multiple_opcodes_0 = {
            # 0X0000: Instruction(),
            0X00E0: Instruction('CLS', Chip8.clear_display_00e0),
            0X00EE: Instruction('RET', Chip8.return_subroutine_00ee),
        }
        if opcode_0 in multiple_opcodes_0:
            return multiple_opcodes_0[opcode_0]

        # 8 CASES
        opcode_8 = opcode & 0xF00F
        multiple_opcodes_8 = {
            0x8000: Instruction(f'LD V{x}, V{y}', Chip8.set_reg_reg_8xy0, x, y),
            0x8001: Instruction(f'OR V{x}, V{y}', Chip8.or_reg_reg_8xy1, x, y),
            0x8002: Instruction(f'AND V{x}, V{y}', Chip8.and_reg_reg_8xy2, x, y),
            0x8003: Instruction(f'XOR V{x}, V{y}', Chip8.xor_reg_reg_8xy3, x, y),
            0x8004: Instruction(f'ADD V{x}, V{y}', Chip8.add_reg_carry_8xy4, x, y),
            0x8005: Instruction(f'SUB V{x}, V{y}', Chip8.sub_reg_reg_8xy5, x, y),
            0x8006: Instruction(f'SHR V{x}, V{y}', Chip8.shr_reg_8xy6, x, y),
            0x8007: Instruction(f'SUBN V{x}, V{y}', Chip8.subn_reg_reg_8xy7, x, y),
            0x800E: Instruction(f'SHL V{x}, V{y}', Chip8.shl_reg_8xye, x, y),
        }
        if opcode_8 in multiple_opcodes_8:
            return multiple_opcodes_8[opcode_8]

        # E and F CASES
        opcode_ef = opcode & 0xF0FF
        multiple_opcodes_ef = {
            0xE09E: Instruction(f'SKP V{x}', Chip8.skip_if_pressed_ex9e, x),
            0xE0A1: Instruction(f'SKNP V{x}', Chip8.set_reg_reg_8xy0, x),
            0xF007: Instruction(f'LD V{x}, DT', Chip8.save_delay_fx07, x),
            0xF00A: Instruction(f'LD V{x}', Chip8.wait_for_keypress_fx0a, x),
            0xF015: Instruction(f'LD DT, V{x}', Chip8.set_delay_fx15, x),
            0xF018: Instruction(f'LD ST, V{x}', Chip8.set_sound_fx18, x),
            0xF01E: Instruction(f'ADD I, V{x}', Chip8.add_index_fx1e, x),
            0xF029: Instruction(f'LD F, V{x}', Chip8.set_sprite_loc_fx29, x),
            0xF033: Instruction(f'LD B, V{x}', Chip8.bcd_repr_fx33, x),
            0xF055: Instruction(f'LD [I], V{x}', Chip8.store_regs_fx55, x),
            0xF065: Instruction(f'LD V{x}, [I]', Chip8.read_regs_fx65, x),
        }
        if opcode_ef in multiple_opcodes_ef:
            return multiple_opcodes_ef[opcode_ef]

        return Instruction(f"Invalid opcode {opcode}", Chip8.do_nothing)








