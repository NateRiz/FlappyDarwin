from FlappyDarwin import FlappyDarwin, State
from PyGP.Hardware import Hardware, InstructionLibrary
import PyGP.Instructions as inst
from PyGP.Selection import tournament
from PyGP.Mutation import mutate
from threading import Thread
from time import sleep,time
import CustomInstructions as c_inst


def main():
    game = FlappyDarwin()

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
    inst_lib.add_inst("Jump", lambda _, __: c_inst.jump(game), False)
    inst_lib.add_inst("Wait", lambda _, __: c_inst.wait(), False)
    #inst_lib.add_inst("For", inst.for_, True)


    hws = [Hardware(inst_lib) for _ in range(10)]
    [hw.generate_program() for hw in hws]

    Thread(target=test_hardware, args=(hws, game)).start()
    game.start()
    print("Thread 1 ended.")

def test_hardware(hws, game):
    while not game.QUIT_SIGNAL:
        ticks = 0
        for hw in hws:
            game.restart()

            while not hw.EOP and not game.game_state == State.GAMEOVER:
                hw.tick()
                ticks += 1
                if game.QUIT_SIGNAL: return

            hw.cache_fitness(time()-game.game_start_time)
            print([hw.fitness for hw in hws])

        hws = tournament(hws)
        [mutate(hw) for hw in hws]


if __name__ == '__main__':
    main()
