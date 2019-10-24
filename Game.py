from FlappyDarwin import FlappyDarwin
from PyGP.Hardware import InstructionLibrary
import PyGP.Instructions as inst
from PyGP.Selection import *
from PyGP.Mutation import mutate, recombination
import CustomInstructions as c_inst
import os
from time import sleep
import sys


def main():

    pop_size = 100
    ticks_per_update = 100
    min_program_length = 16
    max_program_length = 80
    num_tests = 5
    hws = [Hardware(None, i, min_program_length, max_program_length) for i in range(pop_size)]
    game = FlappyDarwin(hws, ticks_per_update, num_tests)
    inst_lib = generate_inst_lib(game)
    for hw in hws:
        hw.inst_lib = inst_lib

    [hw.generate_program() for hw in hws]
    #hws[0] = Hardware(inst_lib, 0, 8, 96)
    #hws[0].load_program("PyGP/program.txt")
    #hws[0].set_verbose()

    best_fitness = [0]
    gen = 0

    if len(sys.argv) > 1:
        if os.path.exists(os.path.join(os.getcwd(), "")):
            print(F"LOADING FROM EXISTING SAVED GP FILE: {sys.argv[1]}")
            hws, gen = load_programs(sys.argv[1], inst_lib, min_program_length, max_program_length, pop_size)
            game.generation = gen

    while not game.QUIT_SIGNAL:
        gen += 1
        print(F"Generation: {gen}")
        game.set_hardware(hws)
        game.start()

        for i, hw in enumerate(hws):
            hw.cache_fitness(game.birds[i].fitness)

        local_best = max(hws, key=lambda hw: min(hw.fitness))
        if min(local_best.fitness) > min(best_fitness):
            best_fitness = local_best.fitness
            print(local_best)
            print("Finished with fitness", local_best.fitness)
            print("____________________________")

        copy_best = local_best.copy()
        copy_best.traits = 0

        hws = lexicase(hws)
        #hws = tournament(hws)
        [mutate(hw) for hw in hws]
        recombination(hws)
        for i, hw in enumerate(hws):
            hw.traits = i

        # Keep around the best performing from the previous generation & reset its hardware
        hws[0] = copy_best
        hws[0].traits = 0

        if gen in {50, 100, 500, 1000, 1500, 2000, 2500, 3000}:
            save_programs(gen, hws)


def save_programs(gen, hws):
    with open(F"gen{gen}.gp", "w") as file:
        file.write(str(gen)+"\n")
        for hw in hws:
            file.write(hw.get_writable_program())
            file.write("\n#\n")


def load_programs(file, inst_lib, min_len, max_len, pop_size):
    with open(file, "r") as file:
        gen = int(file.readline().strip())
        hws = []
        i = 0
        build = []
        for line in file.readlines():
            line = line.strip()
            if line[0] == "#":
                hws.append(Hardware(inst_lib, i, min_len, max_len))
                hws[-1].load_program_from_string("\n".join(build))
                build.clear()
                i += 1
                assert i <= pop_size
            else:
                build.append(line)

        if build:
            hws.append(Hardware(inst_lib, i, min_len, max_len))
            hws[-1].load_program_from_string("\n".join(build))
            build.clear()

        return hws, gen



def generate_inst_lib(game):
    inst_lib = InstructionLibrary()
    inst_lib.add_inst("Add", inst.add, False)
    inst_lib.add_inst("Sub", inst.sub, False)
    #inst_lib.add_inst("Mul", inst.mul, False)
    #inst_lib.add_inst("Div", inst.div, False)
    inst_lib.add_inst("Eq", inst.eq, False)
    inst_lib.add_inst("Greater", inst.greater, False)
    inst_lib.add_inst("Less", inst.less, False)
    #inst_lib.add_inst("Not", inst.not_, False)
    inst_lib.add_inst("Assign", inst.assign, False)
    inst_lib.add_inst("Copy", inst.copy, False)
    inst_lib.add_inst("While", inst.while_, True)
    #inst_lib.add_inst("Break", inst.break_, False) broken when its not in a loop or when its in an if
    inst_lib.add_inst("Close", inst.close, False)
    inst_lib.add_inst("Jump", lambda hw, __: c_inst.jump(hw, game), False)
    inst_lib.add_inst("BirdHeight", lambda hw, args: c_inst.get_bird_height(hw, args, game), False)
    inst_lib.add_inst("GapTop", lambda hw, args: c_inst.get_gap_top(hw, args, game), False)
    inst_lib.add_inst("GapMid", lambda hw, args: c_inst.get_gap_midpoint(hw, args, game) , False)
    inst_lib.add_inst("GapBot", lambda hw, args: c_inst.get_gap_bot(hw, args, game), False)
    #inst_lib.add_inst("PipeX", lambda hw, args: c_inst.get_pipe_x(hw, args, game), False)
    #inst_lib.add_inst("Pixel", lambda hw, args: c_inst.check_pixel_collide(hw, args, game), False)
    #inst_lib.add_inst("ScreenHeight", lambda hw, args: c_inst.get_screen_height(hw, args, game), False)
    inst_lib.add_inst("For", inst.for_, True)
    inst_lib.add_inst("If", inst.if_, True)
    return inst_lib


if __name__ == '__main__':
    main()
