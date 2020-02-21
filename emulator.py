from pathlib import Path

from chip8 import Chip8


def emulate():
    emulator = Chip8()
    rom = Path('ROMs', 'Airplane.ch8')

    emulator.initialize()
    emulator.load_game(rom)
    print(emulator.memory)


if __name__ == '__main__':
    emulate()
