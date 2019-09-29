from FlappyDarwin import FlappyDarwin, State
from PyGP.Hardware import InstructionLibrary
import PyGP.Instructions as inst
from PyGP.Selection import *
from PyGP.Mutation import mutate, recombination
from threading import Thread, active_count
from time import sleep
import CustomInstructions as c_inst


def main():
    pop_size = 125
    game = FlappyDarwin(pop_size)
    Thread(target=test_hardware, args=(game, pop_size)).start()
    game.start()
    print("Thread 1 ended.")


def test_hardware(game, pop_size):
    inst_lib = generate_inst_lib(game)
    hws = [Hardware(inst_lib, id_, 8, 96) for id_ in range(pop_size)]
    [hw.generate_program() for hw in hws]
    #[hw.load_program("PyGP/program.txt") for hw in hws]
    best_fitness = 0
    gen = 0
    while not game.QUIT_SIGNAL:
        gen += 1
        print(F"Generation: {gen}")

        threads = [Thread(target=run_single_hardware, args=(hws[i], game, i)) for i in range(pop_size)]
        for t in threads:
            t.start()

        game.restart()

        while game.game_state != State.GAMEOVER:
            sleep(.1)

        for t in threads:
            t.join()

        local_best = None
        for hw in hws:
            if not local_best or hw.fitness > local_best.fitness:
                local_best = hw
            if hw.fitness > best_fitness:
                best_fitness = hw.fitness
                print(hw)
                print("Finished with fitness", hw.fitness)
                print("____________________________")

        copy_best = local_best.copy()
        copy_best.traits = 0

        hws = tournament(hws)
        [mutate(hw) for hw in hws]
        recombination(hws)

        # Keep around the best performing from the previous generation & reset its hardware
        hws[0] = copy_best

def run_single_hardware(hw, game, id_):
    ticks = 0
    insts_per_frame = 30

    while game.game_state != State.PLAYING:
        sleep(.1)
        game.birds[id_].ready_to_start = True

    while not game.birds[id_].dead and not hw.EOP:
        sleep(.01)
        while ticks < game.frames * insts_per_frame and not hw.EOP and not game.birds[id_].dead:
            game.birds[id_].ready_for_update = False
            hw.tick()
            ticks += 1
            if game.QUIT_SIGNAL:
                return
        game.birds[id_].ready_for_update = True

    hw.cache_fitness(game.birds[id_].fitness)



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
