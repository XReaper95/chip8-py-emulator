import sys
from pathlib import Path

from chip8 import Chip8
from decoder import InstructionDecoder


class Emulator:
    def __init__(self):
        self._chip8 = Chip8()
        self.frame = None

    def load_rom(self, game: Path):
        self._chip8.initialize()
        self._chip8.load_game(game)

    def tick(self) -> None:
        """
        Emulate one CPU cycle
        """


        # process input
