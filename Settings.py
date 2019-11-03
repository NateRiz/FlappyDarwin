import sys
import os
from PyGP.Hardware import Hardware

usage = \
"""
python3 Game.py [pop_size 100 ticks_per_update 20 max_program_length 64 ...]

Args:
pop_size {int} : Amount of birds in the population.
ticks_per_update {int} : How many instructions are run on each hardware before a frame passes.
min_program_length {int} : How small a program is allowed to get in terms of instructions.
max_program_length {int} : How large a program is allowed to get in terms of instructions.
num_tests {int} : Number of tests if using lexicase - Adjusts height of gap in first pipe .
selection {Lexicase/Tournament/Elite} : Choice of which selection scheme to use.
fitness {Distance/Novelty} : Choice of which fitness function to use. 
save_file {str} : Which file to use if continuing from a previous run.
analytics_enabled {bool} : True if storing fitness and outputting to analytics.txt
"""


class Settings:
    def __init__(self):
        self.pop_size = 100
        self.ticks_per_update = 50
        self.min_program_length = 16
        self.max_program_length = 64
        self.num_tests = 5
        self.selection = "roulette"
        self.fitness = "distance"
        self.save_file = ""
        self.analytics_enabled = True

    def update_command_line_args(self):
        if len(sys.argv) <= 1:
            return True
        original_num_settings = len(self.__dict__)
        args = sys.argv[1::]
        cmd_args = {args[2 * i].lower(): int(args[2 * i + 1]) if args[2 * i + 1].isdigit() else args[2 * i + 1]
                    for i in range(len(args) // 2)}
        self.__dict__.update(cmd_args)
        self.selection = self.selection.lower()
        self.fitness = self.fitness.lower()
        if original_num_settings != len(self.__dict__):
            print(usage)
            return False
        assert self.selection in ["tournament", "elite", "lexicase", "roulette"], F"Incorrect selection scheme: {self.selection}"
        assert self.fitness in ["distance", "novelty"], F"Incorrect fitness function: {self.fitness}"
        return True


def save_programs(gen, hws, gen_finished_test):
    with open(F"gen{gen}.gp", "w") as file:
        file.write(str(gen)+"\n")
        file.write(str(gen_finished_test)+"\n")
        for hw in hws:
            file.write(hw.get_writable_program())
            file.write("\n#\n")


def load_programs(inst_lib, settings):
    path = os.path.join(os.getcwd(), settings.save_file)
    with open(path, "r") as file:
        gen = int(file.readline().strip())
        gen_finished_test = int(file.readline().strip())
        hws = []
        i = 0
        build = []
        for line in file.readlines():
            line = line.strip()
            if line[0] == "#":
                hws.append(Hardware(inst_lib, i, settings.min_program_length, settings.max_program_length))
                hws[-1].load_program_from_string("\n".join(build))
                build.clear()
                i += 1
                assert i <= settings.pop_size
            else:
                build.append(line)

        if build:
            hws.append(Hardware(inst_lib, i, settings.min_program_length, settings.max_program_length))
            hws[-1].load_program_from_string("\n".join(build))
            build.clear()

        return hws, gen, gen_finished_test

