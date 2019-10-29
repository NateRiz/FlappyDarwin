from FlappyDarwin import FlappyDarwin
from PyGP.Hardware import InstructionLibrary
import PyGP.Instructions as inst
from PyGP.Selection import *
from PyGP.Mutation import mutate, recombination
from NoveltySelection import Novelty
import CustomInstructions as c_inst
import os
from Settings import Settings, save_programs, load_programs
from Analytics import Analytics
from time import time


def main():

    settings = Settings()
    analytics = Analytics()
    novelty = Novelty()
    cmd_line_args_success = settings.update_command_line_args()
    if not cmd_line_args_success:
        return
    print("Settings:"+"\n".join([f"{i} : {j}" for i, j in vars(settings).items()]))

    hws = [Hardware(None, i, settings.min_program_length, settings.max_program_length) for i in range(settings.pop_size)]
    game = FlappyDarwin(
        hws,
        settings.ticks_per_update,
        settings.num_tests if settings.selection == "lexicase" else 1,
        (lambda: 0) if settings.fitness == "novelty" else (lambda: time())
        )
    inst_lib = generate_inst_lib(game)
    for hw in hws:
        hw.inst_lib = inst_lib
    [hw.generate_program() for hw in hws]

    best_fitness = [0]
    fitness_data = []
    gen = 0

    if settings.save_file:
        if os.path.exists(os.path.join(os.getcwd(), "")):
            print(F"LOADING FROM EXISTING SAVED GP FILE: {settings.save_file}")
            hws, gen = load_programs(inst_lib, settings)
            game.generation = gen

    while not game.QUIT_SIGNAL:
        gen += 1
        print(F"Generation: {gen}")
        game.set_hardware(hws)
        game.start()

        for i, hw in enumerate(hws):
            hw.cache_fitness(game.birds[i].fitness)

        local_best = max(hws, key=lambda hw: min(hw.fitness))
        fitness_data.append(min(local_best.fitness))
        if min(local_best.fitness) > min(best_fitness):
            best_fitness = local_best.fitness
            print(local_best)
            print("Finished with fitness", local_best.fitness)
            print("____________________________")

        if settings.fitness == "novelty":
            dists = novelty.select([(bird.rect.x+bird.last_frame_alive, bird.rect.y) for bird in game.birds])
            for i, hw in enumerate(hws):
                hw.cache_fitness(dists[i])
            assert settings.selection != "lexicase", "Cannot combine lexicase with novelty search."

        copy_best = local_best.copy()
        copy_best.traits = 0

        if settings.selection == "tournament":
            hws = tournament(hws)
        elif settings.selection == "elite":
            hws = elite(hws, len(hws)//2)
        elif settings.selection == "lexicase":
            hws = lexicase(hws)
        else:
            raise NotImplementedError(F"Invalid Selection Scheme: {settings.selection}")
        [mutate(hw) for hw in hws]
        recombination(hws)
        for i, hw in enumerate(hws):
            hw.traits = i

        # Keep around the best performing from the previous generation & reset its hardware
        hws[0] = copy_best
        hws[0].traits = 0

        if gen in {50, 100, 500, 1500, 2500} or not gen % 1000:
            save_programs(gen+1, hws)
            analytics.save(gen, fitness_data)
            fitness_data.clear()



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
