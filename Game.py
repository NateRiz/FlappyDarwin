from FlappyDarwin import FlappyDarwin
from PyGP.Hardware import InstructionLibrary
import PyGP.Instructions as inst
from PyGP.Selection import *
from PyGP.Mutation import mutate, recombination
import CustomInstructions as c_inst


def main():
    pop_size = 125
    ticks_per_update = 30
    hws = [Hardware(None, id_, 8, 96) for id_ in range(pop_size)]
    game = FlappyDarwin(hws, ticks_per_update)
    inst_lib = generate_inst_lib(game)
    for hw in hws:
        hw.inst_lib = inst_lib

    [hw.generate_program() for hw in hws]
    #[hw.load_program("PyGP/program.txt") for hw in hws]

    best_fitness = 0
    gen = 0
    while not game.QUIT_SIGNAL:
        gen += 1
        print(F"Generation: {gen}")
        game.set_hardware(hws)
        game.restart()
        game.start()

        for i, hw in enumerate(hws):
            hw.cache_fitness(game.birds[i].fitness)

        local_best = max(hws, key=lambda hw: hw.fitness)
        if local_best.fitness > best_fitness:
            best_fitness = local_best.fitness
            print(local_best)
            print("Finished with fitness", local_best.fitness)
            print("____________________________")

        copy_best = local_best.copy()
        copy_best.traits = 0

        hws = tournament(hws)
        [mutate(hw) for hw in hws]
        recombination(hws)
        for i, hw in enumerate(hws):
            hw.traits = i

        # Keep around the best performing from the previous generation & reset its hardware
        hws[0] = copy_best
        hws[0].traits = 0



def generate_inst_lib(game):
    inst_lib = InstructionLibrary()
    inst_lib.add_inst("Add", inst.add, False)
    inst_lib.add_inst("Sub", inst.sub, False)
    inst_lib.add_inst("Mul", inst.mul, False)
    inst_lib.add_inst("Div", inst.div, False)
    inst_lib.add_inst("Eq", inst.eq, False)
    inst_lib.add_inst("Greater", inst.greater, False)
    inst_lib.add_inst("Less", inst.less, False)
    inst_lib.add_inst("Not", inst.not_, False)
    inst_lib.add_inst("Assign", inst.assign, False)
    inst_lib.add_inst("Copy", inst.copy, False)
    inst_lib.add_inst("While", inst.while_, True)
    inst_lib.add_inst("Break", inst.break_, False)
    inst_lib.add_inst("Close", inst.close, False)
    inst_lib.add_inst("Jump", lambda hw, __: c_inst.jump(hw, game), False)
    inst_lib.add_inst("BirdHeight", lambda hw, args: c_inst.get_bird_height(hw, args, game), False)
    inst_lib.add_inst("GapTop", lambda hw, args: c_inst.get_gap_top(hw, args, game), False)
    inst_lib.add_inst("GapBot", lambda hw, args: c_inst.get_gap_bot(hw, args, game), False)
    inst_lib.add_inst("PipeX", lambda hw, args: c_inst.get_pipe_x(hw, args, game), False)
    inst_lib.add_inst("Pixel", lambda hw, args: c_inst.check_pixel_collide(hw, args, game), False)
    inst_lib.add_inst("ScreenHeight", lambda hw, args: c_inst.get_screen_height(hw, args, game), False)
    inst_lib.add_inst("For", inst.for_, True)
    inst_lib.add_inst("If", inst.if_, True)
    return inst_lib


if __name__ == '__main__':
    main()
