from PyGP.Hardware import Hardware, InstructionLibrary
from PyGP import Instructions as inst
from PyGP.Selection import tournament
from PyGP.Mutation import mutate


def main():
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
    inst_lib.add_inst("Break", inst.break_, False)
    inst_lib.add_inst("For", inst.for_, True)
    inst_lib.add_inst("If", inst.if_, True)
    hws = [Hardware(inst_lib) for _ in range(1000)]
    [hw.generate_program() for hw in hws]

    ticks = 0
    best = 0
    """
    while 1:
        for hw in hws:
            ticks = 0
            while not hw.EOP and ticks < 10:
                ticks += 1
                hw.tick()
            hw.cache_fitness(hw.registers[0])
            if hw.fitness > best:
                best = hw.fitness
                print(hw)
                print("Fin with Fit:", best)
        hws = tournament(hws)
        [mutate(hw) for hw in hws]

    """
    hw = Hardware(inst_lib)
    hw.load_program("PyGP/program.txt")
    while not hw.EOP and ticks<100:
        ticks+=1
        print(hw.instructions[hw.IP])
        hw.tick()
        print(hw.registers)


if __name__ == '__main__':
    main()
