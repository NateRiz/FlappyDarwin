import sys

usage = \
"""
python3 Game.py [pop_size 100 ticks_per_update 20 max_program_length 64 ...]

Args:
pop_size {int} : Amount of birds in the population.
ticks_per_update {int} : How many instructions are run on each hardware before a frame passes.
min_program_length {int} : How small a program is allowed to get in terms of instructions.
max_program_length {int} : How large a program is allowed to get in terms of instructions.
num_tests {int} : Number of tests if using lexicase - Adjusts height of gap in first pipe .
selection {Lexicase/Tournament} : Choice of which selection scheme to use.
save_file {str} : Which file to use if continuing from a previous run.
"""


class Settings:
    def __init__(self):
        self.pop_size = 100
        self.ticks_per_update = 50
        self.min_program_length = 16
        self.max_program_length = 80
        self.num_tests = 5
        self.selection = "lexicase"
        self.save_file = ""

    def update_command_line_args(self):
        if len(sys.argv) <= 1:
            return True
        original_num_settings = len(self.__dict__)
        args = sys.argv[1::]
        cmd_args = {args[2 * i].lower(): int(args[2 * i + 1]) if args[2 * i + 1].isdigit() else args[2 * i + 1]
                    for i in range(len(args) // 2)}
        self.__dict__.update(cmd_args)
        self.selection = self.selection.lower()
        if original_num_settings != len(self.__dict__):
            print(usage)
            return False
        return True
