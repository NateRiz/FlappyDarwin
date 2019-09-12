from FlappyDarwin import FlappyDarwin, State
from PyGP.Hardware import Hardware, InstructionLibrary
import PyGP.Instructions as inst
from PyGP.Selection import *
from PyGP.Mutation import mutate
from threading import Thread
from time import sleep, time
import CustomInstructions as c_inst


def main():
    pop_size = 1000
    game = FlappyDarwin(pop_size)
    Thread(target=test_hardware, args=(game, pop_size)).start()
    game.start()
    print("Thread 1 ended.")


def test_hardware(game, pop_size):
    inst_lib = generate_inst_lib(game)
    hws = [Hardware(inst_lib, i) for i in range(pop_size)]
    [hw.generate_program() for hw in hws]

    pop_size = len(hws)
    gen = 0
    while not game.QUIT_SIGNAL:
        gen += 1
        print(F"Generation: {gen}")

        threads = [Thread(target=run_single_hardware, args=(hws[i], game, i)) for i in range(pop_size)]
        for t in threads:
            t.start()

        game.restart()
        while game.game_state != State.GAMEOVER:
            sleep(.5)

        for t in threads:
            t.join()

        print(max([hw.fitness for hw in hws]))
        hws = tournament(hws)
        [mutate(hw) for hw in hws]


def run_single_hardware(hw, game, id_):
    ticks = 0
    while game.game_state != State.PLAYING:
        sleep(.1)

    while not game.birds[id_].dead:
        hw.tick()
        ticks += 1
        if game.QUIT_SIGNAL: return
        sleep(.025)
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
    inst_lib.add_inst("Close", inst.close, False)
    inst_lib.add_inst("Jump", lambda hw, __: c_inst.jump(hw, game), False)
    inst_lib.add_inst("Wait", lambda _, __: c_inst.wait(), False)
    inst_lib.add_inst("BirdHeight", lambda hw, args: c_inst.get_bird_height(hw, args, game), False)
    inst_lib.add_inst("GapTop", lambda hw, args: c_inst.get_gap_top(hw, args, game), False)
    inst_lib.add_inst("GapBot", lambda hw, args: c_inst.get_gap_bot(hw, args, game), False)
    # inst_lib.add_inst("For", inst.for_, True)
    return inst_lib


if __name__ == '__main__':
    main()
